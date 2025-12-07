"""Slide Layout System - Automatic content scaling and layout modes.

This module implements the content scaling principles documented in MARKDOWN_SLIDES.md:
- Maximize space usage
- Consistent sizing across slides
- Animation-stable layouts (final_content for sizing)
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
    from ..slide import Slide
    from ..slide_deck import SlideDeck
    from ..theme import LayoutStyle


class LayoutMode(Enum):
    """Layout modes based on content presence."""
    TITLE_ONLY = auto()      # Just title (and optional subtitle)
    TITLE_CENTERED = auto()  # Title + subtitle + small content (centered, like end slides)
    CONTENT_ONLY = auto()    # Just content, no title
    TITLE_CONTENT = auto()   # Title + content (PowerPoint-style)


@dataclass
class LayoutConfig:
    """Configuration for slide layout margins and regions.
    
    All values are percentages of slide dimensions.
    """
    # Margins (percentage of slide dimensions)
    margin_top: float = 3.0       # Header area (reduced)
    margin_bottom: float = 6.0    # Footer area (increased for footer space)
    margin_left: float = 5.0      # Left safe area
    margin_right: float = 5.0     # Right safe area
    
    # Title region (percentage of slide height, when title present)
    title_height: float = 10.0    # Fixed title region height (reduced)
    title_gap: float = 2.5        # Gap between title and content
    
    # Title-only mode
    title_only_size: float = 8.0  # rem - large centered title
    subtitle_size: float = 3.5    # rem - subtitle below title
    
    # Content-only mode  
    content_only_padding: float = 8.0  # Extra padding when no title
    
    # Title+Content mode
    title_size: float = 4.5       # rem - title in header region
    content_title_gap: float = 3.0  # rem - gap below title
    
    # Base content sizes (rem) - for 1920x1080 slides
    # 1rem = 16px, so 2rem = 32px which is readable on a 1920px wide slide
    base_text_size: float = 2.0       # Default text/bullet size
    base_table_size: float = 1.8      # Default table size  
    base_code_size: float = 1.6       # Default code size
    
    # Minimum scale factor (never go below this)
    min_scale: float = 0.4


# Default configuration
DEFAULT_CONFIG = LayoutConfig()


# =============================================================================
# Content Analysis & Scaling
# =============================================================================

@dataclass
class ContentMetrics:
    """Metrics extracted from content for scaling calculations."""
    content_type: str = 'text'  # 'table', 'bullets', 'code', 'text'
    
    # Table metrics
    table_rows: int = 0
    table_cols: int = 0
    avg_cell_length: float = 0.0
    max_cell_length: int = 0
    
    # List metrics
    bullet_count: int = 0
    max_line_length: int = 0
    
    # Code metrics
    code_lines: int = 0
    max_code_line_length: int = 0
    
    # General
    total_chars: int = 0
    line_count: int = 0


def analyze_content(content: str) -> ContentMetrics:
    """Analyze content to extract metrics for scaling.
    
    :param content: Markdown content to analyze.
    :return: ContentMetrics with extracted measurements.
    """
    metrics = ContentMetrics()
    content = content.strip()
    
    if not content:
        return metrics
    
    metrics.total_chars = len(content)
    metrics.line_count = content.count('\n') + 1
    
    # Check for table
    if content.startswith('|') and '|' in content:
        metrics.content_type = 'table'
        lines = [l for l in content.split('\n') if l.strip().startswith('|')]
        
        # Count rows (excluding header separator)
        data_lines = [l for l in lines if not l.strip().startswith('|--') and not l.strip().startswith('|-')]
        metrics.table_rows = len(data_lines)
        
        # Count columns from first line
        if lines:
            cells = [c.strip() for c in lines[0].split('|') if c.strip()]
            metrics.table_cols = len(cells)
        
        # Calculate cell lengths
        all_cells = []
        for line in data_lines:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            all_cells.extend(cells)
        
        if all_cells:
            metrics.avg_cell_length = sum(len(c) for c in all_cells) / len(all_cells)
            metrics.max_cell_length = max(len(c) for c in all_cells)
        
        return metrics
    
    # Check for code block
    if '```' in content:
        metrics.content_type = 'code'
        # Extract code between ```
        import re
        code_blocks = re.findall(r'```\w*\n(.*?)```', content, re.DOTALL)
        if code_blocks:
            code = '\n'.join(code_blocks)
            code_lines = code.split('\n')
            metrics.code_lines = len(code_lines)
            metrics.max_code_line_length = max(len(l) for l in code_lines) if code_lines else 0
        return metrics
    
    # Check for bullet list
    bullet_pattern = r'^[\s]*[-*+]\s+'
    import re
    bullet_lines = re.findall(bullet_pattern, content, re.MULTILINE)
    if bullet_lines:
        metrics.content_type = 'bullets'
        metrics.bullet_count = len(bullet_lines)
        lines = content.split('\n')
        metrics.max_line_length = max(len(l) for l in lines) if lines else 0
        return metrics
    
    # Default to text
    metrics.content_type = 'text'
    lines = content.split('\n')
    metrics.max_line_length = max(len(l) for l in lines) if lines else 0
    
    return metrics


def calculate_content_scale(metrics: ContentMetrics, config: LayoutConfig) -> tuple[float, float]:
    """Calculate font size and scale factor based on content metrics.
    
    :param metrics: Content metrics from analyze_content().
    :param config: Layout configuration.
    :return: Tuple of (font_size_rem, scale_factor).
    """
    scale = 1.0
    
    if metrics.content_type == 'table':
        base_size = config.base_table_size
        
        # Scale based on row count - maximize space usage
        # Fewer rows = larger text to fill space
        # More rows = smaller text to fit all content
        if metrics.table_rows <= 5:
            # Small tables: scale UP significantly to fill space
            scale = 1.6
        elif metrics.table_rows <= 7:
            scale = 1.4
        elif metrics.table_rows <= 8:
            scale = 1.2
        elif metrics.table_rows <= 10:
            scale = 1.0
        elif metrics.table_rows <= 12:
            scale = 0.8
        else:
            scale = 0.65
        
        # Adjust for column count (less aggressive)
        if metrics.table_cols > 6:
            scale *= 0.9
        elif metrics.table_cols > 5:
            scale *= 0.95
        
        # Adjust for long cell content
        if metrics.avg_cell_length > 30:
            scale *= 0.9
        elif metrics.avg_cell_length > 20:
            scale *= 0.95
        
    elif metrics.content_type == 'bullets':
        base_size = config.base_text_size
        
        # Scale down for many items
        if metrics.bullet_count > 10:
            scale = min(scale, 0.7)
        elif metrics.bullet_count > 8:
            scale = min(scale, 0.8)
        elif metrics.bullet_count > 6:
            scale = min(scale, 0.9)
        
        # Scale down for long lines
        if metrics.max_line_length > 100:
            scale = min(scale, 0.8)
        elif metrics.max_line_length > 80:
            scale = min(scale, 0.9)
        
    elif metrics.content_type == 'code':
        base_size = config.base_code_size
        
        # Scale down for many lines
        if metrics.code_lines > 20:
            scale = min(scale, 0.7)
        elif metrics.code_lines > 15:
            scale = min(scale, 0.8)
        elif metrics.code_lines > 10:
            scale = min(scale, 0.9)
        
        # Scale down for long lines
        if metrics.max_code_line_length > 80:
            scale = min(scale, 0.8)
        elif metrics.max_code_line_length > 60:
            scale = min(scale, 0.9)
        
    else:  # text
        base_size = config.base_text_size
        
        # Scale down for lots of text
        if metrics.total_chars > 800:
            scale = min(scale, 0.7)
        elif metrics.total_chars > 500:
            scale = min(scale, 0.85)
    
    # Apply minimum scale
    scale = max(scale, config.min_scale)
    
    return base_size * scale, scale


def detect_layout_mode(slide: 'Slide') -> LayoutMode:
    """Detect the appropriate layout mode for a slide.
    
    :param slide: The slide to analyze.
    :return: Detected layout mode.
    """
    has_title = bool(slide.title)
    has_content = bool(slide.content) or slide.has_custom_builder()
    has_subtitle = bool(slide.subtitle)
    
    if has_title and not has_content and not has_subtitle:
        return LayoutMode.TITLE_ONLY
    if has_title and has_subtitle and not has_content:
        return LayoutMode.TITLE_ONLY  # Title + subtitle = title-only mode
    if not has_title and has_content:
        return LayoutMode.CONTENT_ONLY
    
    # Check if content is "small" (short text, no tables/code) - use centered layout
    if has_title and has_subtitle and has_content:
        content = slide.content.strip()
        # Small content: few lines, no complex elements
        is_small = (
            len(content) < 300 and
            '|' not in content and  # No tables
            '```' not in content and  # No code blocks
            content.count('\n') < 8  # Few lines
        )
        if is_small:
            return LayoutMode.TITLE_CENTERED
    
    return LayoutMode.TITLE_CONTENT


def build_slide_layout(
    slide: 'Slide',
    step: int = 0,
    style: 'LayoutStyle | None' = None,
    config: LayoutConfig | None = None,
    final_content: str | None = None,
) -> None:
    """Build slide with automatic layout and scaling.
    
    :param slide: The slide to render.
    :param step: Current animation step.
    :param style: Style to apply (from theme cascade).
    :param config: Layout configuration (uses defaults if None).
    :param final_content: Content used for sizing (for animation stability).
                         If None, uses slide.content.
    """
    from ..theme import LayoutStyle
    
    config = config or DEFAULT_CONFIG
    style = style or LayoutStyle()
    mode = detect_layout_mode(slide)
    
    # Use final_content for sizing calculations, current content for display
    sizing_content = final_content if final_content is not None else slide.content
    
    # Background
    bg_style = _get_background_style(slide)
    
    with ui.element('div').classes('slide-layout w-full h-full').style(bg_style):
        if mode == LayoutMode.TITLE_ONLY:
            _build_title_only(slide, style, config)
        elif mode == LayoutMode.TITLE_CENTERED:
            _build_title_centered(slide, style, config)
        elif mode == LayoutMode.CONTENT_ONLY:
            _build_content_only(slide, step, style, config, sizing_content)
        else:
            _build_title_content(slide, step, style, config, sizing_content)


def _get_background_style(slide: 'Slide') -> str:
    """Get CSS background style for slide."""
    if not slide.background_color:
        return ''
    
    bg = slide.background_color
    if 'gradient' in bg or bg.startswith('radial') or bg.startswith('linear'):
        return f'background: {bg};'
    return f'background-color: {bg};'


def _build_title_only(
    slide: 'Slide',
    style: 'LayoutStyle',
    config: LayoutConfig,
) -> None:
    """Build title-only layout - large centered title."""
    # For centered content, use symmetric vertical padding
    vertical_padding = (config.margin_top + config.margin_bottom) / 2
    
    # Full-page centered container
    with ui.element('div').classes('w-full h-full flex flex-col items-center justify-center').style(
        f'padding: {vertical_padding}% {config.margin_right}% {vertical_padding}% {config.margin_left}%;'
    ):
        # Title - large and prominent
        title_css = style.to_css('title') or ''
        ui.label(slide.title).classes(
            f'text-center font-bold {style.to_tailwind("title")}'
        ).style(
            f'font-size: {config.title_only_size}rem; line-height: 1.1; {title_css}'
        )
        
        # Subtitle if present
        if slide.subtitle:
            subtitle_css = style.to_css('subtitle') or ''
            ui.label(slide.subtitle).classes(
                f'text-center mt-8 {style.to_tailwind("subtitle")}'
            ).style(
                f'font-size: {config.subtitle_size}rem; line-height: 1.3; opacity: 0.8; {subtitle_css}'
            )


def _build_title_centered(
    slide: 'Slide',
    style: 'LayoutStyle',
    config: LayoutConfig,
) -> None:
    """Build centered layout - title, subtitle, and small content all centered."""
    # For centered content, use symmetric vertical padding
    vertical_padding = (config.margin_top + config.margin_bottom) / 2
    
    # Full-page centered container
    with ui.element('div').classes('w-full h-full flex flex-col items-center justify-center').style(
        f'padding: {vertical_padding}% {config.margin_right}% {vertical_padding}% {config.margin_left}%;'
    ):
        # Title - large
        title_css = style.to_css('title') or ''
        ui.label(slide.title).classes(
            f'text-center font-bold {style.to_tailwind("title")}'
        ).style(
            f'font-size: {config.title_only_size}rem; line-height: 1.1; {title_css}'
        )
        
        # Subtitle
        if slide.subtitle:
            subtitle_css = style.to_css('subtitle') or ''
            ui.label(slide.subtitle).classes(
                f'text-center mt-6 {style.to_tailwind("subtitle")}'
            ).style(
                f'font-size: {config.subtitle_size}rem; line-height: 1.3; opacity: 0.8; {subtitle_css}'
            )
        
        # Small content - centered below
        if slide.content:
            text_css = style.to_css('text') or ''
            with ui.element('div').classes('mt-12 text-center').style(
                f'font-size: 1.8rem; line-height: 1.6; {text_css}'
            ):
                ui.markdown(slide.content).classes('text-center')


def _build_content_only(
    slide: 'Slide',
    step: int,
    style: 'LayoutStyle',
    config: LayoutConfig,
    sizing_content: str,
) -> None:
    """Build content-only layout - content fills entire slide."""
    # Calculate padding (slightly more than normal margins)
    padding_v = config.margin_top + config.content_only_padding
    padding_h = config.margin_left + config.content_only_padding
    
    # Full-page content container
    with ui.element('div').classes('w-full h-full flex flex-col').style(
        f'padding: {padding_v}% {padding_h}%;'
    ):
        # Content area fills everything
        with ui.element('div').classes(
            'flex-1 flex flex-col items-center justify-center overflow-hidden'
        ):
            _render_content(slide.content, style, config, is_full_page=True)


def _build_title_content(
    slide: 'Slide',
    step: int,
    style: 'LayoutStyle',
    config: LayoutConfig,
    sizing_content: str,
) -> None:
    """Build title+content layout - PowerPoint style."""
    # Detect if content is a table (needs to fill space)
    is_table_content = slide.content.strip().startswith('|') and '|' in slide.content
    
    # Main container with margins
    with ui.element('div').classes('w-full h-full flex flex-col').style(
        f'padding: {config.margin_top}% {config.margin_right}% {config.margin_bottom}% {config.margin_left}%;'
    ):
        # Title region (fixed height, title at top)
        with ui.element('div').classes('flex-shrink-0').style(
            f'margin-bottom: {config.title_gap}%;'
        ):
            title_css = style.to_css('title') or ''
            ui.label(slide.title).classes(
                f'font-bold {style.to_tailwind("title")}'
            ).style(
                f'font-size: {config.title_size}rem; line-height: 1.2; {title_css}'
            )
        
        # Subtitle if present (part of title region)
        if slide.subtitle:
            with ui.element('div').classes('flex-shrink-0').style('margin-bottom: 1rem;'):
                subtitle_css = style.to_css('subtitle') or ''
                ui.label(slide.subtitle).classes(
                    f'{style.to_tailwind("subtitle")}'
                ).style(
                    f'font-size: 2rem; line-height: 1.3; opacity: 0.8; {subtitle_css}'
                )
        
        # Content region (fills remaining space)
        # For tables: fill and stretch. For other content: center vertically
        content_classes = 'flex-1 flex flex-col'
        if not is_table_content:
            content_classes += ' justify-center'
        
        with ui.element('div').classes(content_classes).style('min-height: 0;'):
            _render_content(slide.content, style, config, is_full_page=False)


def _render_content(
    content: str,
    style: 'LayoutStyle',
    config: LayoutConfig,
    is_full_page: bool = False,
) -> None:
    """Render markdown content with programmatic scaling.
    
    Uses content analysis to determine optimal font size, then renders
    using the appropriate content element component.
    
    :param content: Markdown content to render.
    :param style: Style to apply.
    :param config: Layout configuration.
    :param is_full_page: Whether content should fill the entire page.
    """
    from .content_elements import (
        TableElement,
        BulletListElement,
        CodeBlockElement,
        MixedContentElement,
        REM_TO_PX_FACTOR,
    )
    
    if not content:
        return
    
    # Analyze content and calculate optimal scale
    metrics = analyze_content(content)
    font_size, scale = calculate_content_scale(metrics, config)
    
    # Adjust for full-page mode (slightly larger)
    if is_full_page:
        font_size *= 1.2
    
    # Content container with theme styles
    text_css = style.to_css('text') or ''
    container_classes = f'w-full {style.to_tailwind("text")}'
    
    # Convert to px for consistent sizing
    px_size = font_size * REM_TO_PX_FACTOR
    
    with ui.element('div').classes(container_classes).style(text_css):
        # Route to appropriate renderer based on content type
        # Use inline rendering (not async build) for synchronous layout
        if metrics.content_type == 'table':
            with ui.element('div').classes('w-full').style(
                f'font-size: {px_size}px; line-height: 1.4;'
            ):
                ui.markdown(content).classes('w-full')
        elif metrics.content_type == 'bullets':
            with ui.element('div').classes('w-full').style(
                f'font-size: {px_size}px; line-height: 1.5;'
            ):
                ui.markdown(content)
        elif metrics.content_type == 'code':
            with ui.element('div').classes('w-full').style(
                f'font-size: {px_size}px; line-height: 1.5;'
            ):
                ui.markdown(content)
        else:
            # Mixed or plain text content
            with ui.element('div').classes('w-full').style(
                f'font-size: {px_size}px; line-height: 1.5;'
            ):
                ui.markdown(content)
