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

from .content_elements import MediaView

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

# Track injected CSS to avoid duplicates
_injected_css_hash: set[int] = set()


def _inject_theme_css(style: 'LayoutStyle') -> None:
    """Inject theme-specific CSS for elements like bold text.
    
    :param style: The layout style containing theme element definitions.
    """
    # Get bold style from theme
    bold_style = style.get('bold')
    if not bold_style or not bold_style.color:
        return
    
    # Create CSS for bold text
    css = f'.nicegui-markdown strong {{ color: {bold_style.color}; }}'
    
    # Avoid duplicate injection
    css_hash = hash(css)
    if css_hash in _injected_css_hash:
        return
    _injected_css_hash.add(css_hash)
    
    # Inject via NiceGUI
    ui.add_head_html(f'<style>{css}</style>')


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
    has_content = bool(slide.content) or slide.has_custom_build()
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
    deck: 'SlideDeck | None' = None,
) -> None:
    """Build slide with automatic layout and scaling.
    
    :param slide: The slide to render.
    :param step: Current animation step.
    :param style: Style to apply (from theme cascade).
    :param config: Layout configuration (uses defaults if None).
    :param final_content: Content used for sizing (for animation stability).
                         If None, uses slide.content.
    :param deck: Parent deck for default background fallback.
    """
    from ..theme import LayoutStyle
    
    config = config or DEFAULT_CONFIG
    style = style or LayoutStyle()
    
    # Inject theme-specific CSS for bold text
    _inject_theme_css(style)
    
    # Check for multi-region slide
    if slide.regions and len(slide.regions) > 1:
        _build_multi_region_layout(slide, step, style, config)
        return
    
    mode = detect_layout_mode(slide)
    
    # Use final_content for sizing calculations, current content for display
    sizing_content = final_content if final_content is not None else slide.content
    
    # Background - use slide's background, or fall back to deck's default
    effective_bg = slide.background_color
    effective_bg_modifiers = slide.background_modifiers
    if not effective_bg and deck and deck.default_background:
        effective_bg = deck.default_background
        effective_bg_modifiers = deck.default_background_modifiers
    
    # Temporarily set for helper functions
    original_bg = slide.background_color
    original_modifiers = slide.background_modifiers
    slide.background_color = effective_bg
    slide.background_modifiers = effective_bg_modifiers
    
    bg_style = _get_background_style(slide)
    has_bg_image = _has_background_image(slide)
    
    # Get theme defaults for filters
    overlay_style = style.get('overlay')
    theme_overlay_color = overlay_style.color if overlay_style.color else 'rgba(0, 0, 0, 0.5)'
    theme_overlay_opacity = getattr(overlay_style, 'opacity', 0.5) if overlay_style else 0.5
    
    blur_style = style.get('blur')
    theme_blur_radius = 4  # Default
    if blur_style and hasattr(blur_style, 'css') and blur_style.css:
        # Try to extract radius from css if set
        pass
    
    # Get split background color from theme
    split_bg_style = style.get('split_background')
    split_bg_color = split_bg_style.color if split_bg_style.color else '#1a1a2e'
    
    # For split layouts, we need a container structure to clip the image
    position = slide.background_position
    is_split = position in ('left', 'right', 'top', 'bottom')
    
    # Get style overrides from slide data (parsed from markdown)
    style_overrides = slide.data.get('_style_overrides', {})
    slide_blur = style_overrides.get('blur')
    slide_overlay = style_overrides.get('overlay')
    
    # Determine main container style
    # Don't apply background to main container if:
    # - It's a split layout with image (handled separately)
    # - It's a full image with blur (will be rendered as separate blurred layer)
    needs_blur = slide_blur is not None and has_bg_image
    main_style = '' if (is_split and has_bg_image) or needs_blur else bg_style
    
    with ui.element('div').classes('slide-layout w-full h-full relative').style(main_style):
        # For split layouts with images, create a clipped container
        if is_split and has_bg_image:
            if position == 'left':
                clip_classes = 'absolute inset-y-0 left-0 w-1/2 overflow-hidden'
            elif position == 'right':
                clip_classes = 'absolute inset-y-0 right-0 w-1/2 overflow-hidden'
            elif position == 'top':
                clip_classes = 'absolute inset-x-0 top-0 h-1/2 overflow-hidden'
            else:  # bottom
                clip_classes = 'absolute inset-x-0 bottom-0 h-1/2 overflow-hidden'
            
            with ui.element('div').classes(clip_classes):
                # Use raw modifiers string from slide
                media_view = MediaView.from_string(slide.background_color, slide.background_modifiers)
                media_view.build_background(
                    container_classes='w-full h-full',
                    theme_overlay_opacity=theme_overlay_opacity,
                    theme_blur_default=theme_blur_radius,
                )
        elif has_bg_image:
            # Full background image - use raw modifiers from slide
            media_view = MediaView.from_string(slide.background_color, slide.background_modifiers)
            media_view.build_background(
                container_classes='absolute inset-0',
                theme_overlay_opacity=theme_overlay_opacity,
                theme_blur_default=theme_blur_radius,
            )
        
        # Content container (above overlay)
        # For split layouts, position content on the opposite side with theme background
        content_classes = 'relative w-full h-full z-10'
        content_style = ''
        position = slide.background_position
        
        # No padding here - _build_title_content handles its own padding
        # This ensures split layouts match non-split layouts
        if position == 'left':
            # Image on left, content on right half
            content_classes = 'absolute right-0 top-0 w-1/2 h-full z-10 flex flex-col'
            content_style = f'background: {split_bg_color};'
        elif position == 'right':
            # Image on right, content on left half
            content_classes = 'absolute left-0 top-0 w-1/2 h-full z-10 flex flex-col'
            content_style = f'background: {split_bg_color};'
        elif position == 'top':
            # Image on top, content on bottom half
            content_classes = 'absolute left-0 bottom-0 w-full h-1/2 z-10 flex flex-col'
            content_style = f'background: {split_bg_color};'
        elif position == 'bottom':
            # Image on bottom, content on top half
            content_classes = 'absolute left-0 top-0 w-full h-1/2 z-10 flex flex-col'
            content_style = f'background: {split_bg_color};'
        
        with ui.element('div').classes(content_classes).style(content_style):
            # For split layouts, always use title_content layout (title at top)
            # This ensures consistent title positioning with non-split layouts
            if is_split:
                _build_title_content(slide, step, style, config, sizing_content, use_split_styles=True)
            elif mode == LayoutMode.TITLE_ONLY:
                _build_title_only(slide, style, config, use_split_styles=False)
            elif mode == LayoutMode.TITLE_CENTERED:
                _build_title_centered(slide, style, config, use_split_styles=False)
            elif mode == LayoutMode.CONTENT_ONLY:
                _build_content_only(slide, step, style, config, sizing_content)
            else:
                _build_title_content(slide, step, style, config, sizing_content, use_split_styles=False)
    
    # Restore original background values
    slide.background_color = original_bg
    slide.background_modifiers = original_modifiers


def _extract_image_path(image_url: str) -> str:
    """Extract the base image path from a URL for comparison.
    
    :param image_url: Image URL like 'url(/media/photo.jpg)' or '/media/photo.jpg'.
    :return: Normalized path for comparison.
    """
    if image_url.startswith('url(') and image_url.endswith(')'):
        return image_url[4:-1].strip('"\'')
    return image_url


def _build_multi_region_layout(
    slide: 'Slide',
    step: int,
    style: 'LayoutStyle',
    config: LayoutConfig,
) -> None:
    """Build a multi-region slide with multiple image/content pairs.
    
    Regions are laid out in equal-width columns (horizontal) or rows (vertical).
    Filters are only applied when explicitly requested via overlay/blur modifiers.
    
    When regions share the same image, renders a seamless panorama where each
    region shows its portion of the full image.
    """
    from .content_elements import REM_TO_PX_FACTOR
    
    regions = slide.regions
    num_regions = len(regions)
    direction = slide.region_direction
    
    # Check if all regions share the same base image (for seamless panorama)
    image_paths = [_extract_image_path(r.image) for r in regions if r.image]
    all_same_image = len(set(image_paths)) == 1 and len(image_paths) == num_regions
    
    # Get theme defaults for filters
    overlay_style = style.get('overlay')
    theme_overlay_opacity = getattr(overlay_style, 'opacity', 0.5) if overlay_style else 0.5
    theme_blur_radius = 4  # Default
    
    split_bg_style = style.get('split_background')
    split_bg_color = split_bg_style.color if split_bg_style.color else '#1a1a2e'
    
    split_title_style = style.get('split_title')
    split_subtitle_style = style.get('split_subtitle')
    split_text_style = style.get('split_text')
    
    # Calculate region size
    if direction == 'horizontal':
        region_width = f'{100 / num_regions}%'
        region_height = '100%'
        flex_direction = 'row'
    else:
        region_width = '100%'
        region_height = f'{100 / num_regions}%'
        flex_direction = 'column'
    
    with ui.element('div').classes('slide-layout w-full h-full').style(
        f'display: flex; flex-direction: {flex_direction};'
    ):
        for idx, region in enumerate(regions):
            # Region container
            with ui.element('div').classes('relative overflow-hidden').style(
                f'width: {region_width}; height: {region_height};'
            ):
                # Background image (if any)
                if region.image:
                    # Use raw modifiers string directly from region
                    media_view = MediaView.from_string(region.image, region.modifiers)
                    
                    # Pass region info for seamless tiling when same image is used
                    media_view.build_background(
                        container_classes='absolute inset-0',
                        theme_overlay_opacity=theme_overlay_opacity,
                        theme_blur_default=theme_blur_radius,
                        region_index=idx if all_same_image else 0,
                        region_count=num_regions if all_same_image else 1,
                        region_direction=direction,
                    )
                else:
                    # No image - use theme background for content
                    ui.element('div').classes('absolute inset-0').style(
                        f'background: {split_bg_color};'
                    )
                
                # Content container - single padding to match non-split layouts
                padding = f'padding: {config.margin_top}% {config.margin_right}% {config.margin_bottom}% {config.margin_left}%;'
                
                with ui.element('div').classes('relative z-10 w-full h-full flex flex-col').style(padding):
                    # Title - use split_title style from theme (fixed at top)
                    # Use same title_gap as single split layout for consistency
                    if region.title:
                        with ui.element('div').classes('flex-shrink-0').style(
                            f'margin-bottom: {config.title_gap}%;'
                        ):
                            title_el = ui.label(region.title)
                            if split_title_style:
                                split_title_style.apply(title_el)
                    
                    # Subtitle - use split_subtitle style from theme (fixed below title)
                    if region.subtitle:
                        with ui.element('div').classes('flex-shrink-0').style('margin-bottom: 1rem;'):
                            subtitle_el = ui.label(region.subtitle)
                            if split_subtitle_style:
                                split_subtitle_style.apply(subtitle_el)
                    
                    # Content - fills remaining space, vertically centered within
                    if region.content:
                        with ui.element('div').classes('flex-1 flex flex-col justify-center').style('min-height: 0;') as content_el:
                            if split_text_style:
                                split_text_style.apply(content_el)
                            # Use proper content rendering with font sizing
                            _render_content(region.content, style, config, is_full_page=False)


def _get_background_style(slide: 'Slide') -> str:
    """Get CSS background style for slide."""
    if not slide.background_color:
        return ''
    
    bg = slide.background_color
    position = slide.background_position
    
    # Handle background images: url(...)
    if bg.startswith('url('):
        # For split layouts, position the image with cover to maintain aspect ratio
        if position == 'left':
            return f'background: {bg} left center/cover no-repeat;'
        elif position == 'right':
            return f'background: {bg} right center/cover no-repeat;'
        elif position == 'top':
            return f'background: {bg} center top/cover no-repeat;'
        elif position == 'bottom':
            return f'background: {bg} center bottom/cover no-repeat;'
        else:
            return f'background: {bg} center/cover no-repeat;'
    
    # Handle gradients
    if 'gradient' in bg or bg.startswith('radial') or bg.startswith('linear'):
        return f'background: {bg};'
    
    # Plain color
    return f'background-color: {bg};'


def _has_background_image(slide: 'Slide') -> bool:
    """Check if slide has a background image."""
    return slide.background_color.startswith('url(')


def _get_element_style(slide: 'Slide', element: str) -> tuple[str, str]:
    """Get CSS and Tailwind classes for a specific element from slide overrides.
    
    :param slide: The slide containing style overrides.
    :param element: Element name ('title', 'subtitle', 'text', etc.).
    :return: Tuple of (css_string, tailwind_classes).
    """
    text_style = slide.data.get('_style_overrides', {}).get(element, {})
    if not text_style:
        return '', ''
    
    css_parts = []
    classes = []
    
    for prop, value in text_style.items():
        if prop == 'class':
            # Tailwind classes
            classes.append(value)
        else:
            # CSS property - convert common shorthand names
            css_prop = prop.replace('_', '-')
            # Map common shortcuts to full CSS property names
            prop_map = {
                'shadow': 'text-shadow',
                'bg': 'background',
                'size': 'font-size',
                'weight': 'font-weight',
            }
            css_prop = prop_map.get(css_prop, css_prop)
            css_parts.append(f'{css_prop}: {value};')
    
    return ' '.join(css_parts), ' '.join(classes)


def _build_title_only(
    slide: 'Slide',
    style: 'LayoutStyle',
    config: LayoutConfig,
    use_split_styles: bool = False,
) -> None:
    """Build title-only layout - large centered title."""
    # For centered content, use symmetric vertical padding
    vertical_padding = (config.margin_top + config.margin_bottom) / 2
    
    # Get element-specific overrides from slide
    title_override_css, title_override_classes = _get_element_style(slide, 'title')
    subtitle_override_css, subtitle_override_classes = _get_element_style(slide, 'subtitle')
    
    # Get theme styles - use split styles for dark backgrounds
    if use_split_styles:
        title_style = style.get('split_title')
        subtitle_style = style.get('split_subtitle')
    else:
        title_style = style.get('title')
        subtitle_style = style.get('subtitle')
    
    # Full-page centered container
    with ui.element('div').classes('w-full h-full flex flex-col items-center justify-center').style(
        f'padding: {vertical_padding}% {config.margin_right}% {vertical_padding}% {config.margin_left}%;'
    ):
        # Title
        title_el = ui.label(slide.title).classes(f'text-center {title_override_classes}')
        if title_style:
            title_style.apply(title_el)
        if title_override_css:
            title_el.style(title_override_css)
        
        # Subtitle if present
        if slide.subtitle:
            subtitle_el = ui.label(slide.subtitle).classes(f'text-center mt-8 {subtitle_override_classes}')
            if subtitle_style:
                subtitle_style.apply(subtitle_el)
            if subtitle_override_css:
                subtitle_el.style(subtitle_override_css)


def _build_title_centered(
    slide: 'Slide',
    style: 'LayoutStyle',
    config: LayoutConfig,
    use_split_styles: bool = False,
) -> None:
    """Build centered layout - title, subtitle, and small content all centered."""
    # For centered content, use symmetric vertical padding
    vertical_padding = (config.margin_top + config.margin_bottom) / 2
    
    # Get element-specific overrides from slide
    title_override_css, title_override_classes = _get_element_style(slide, 'title')
    subtitle_override_css, subtitle_override_classes = _get_element_style(slide, 'subtitle')
    text_override_css, text_override_classes = _get_element_style(slide, 'text')
    
    # Get theme styles - use split styles for dark backgrounds
    if use_split_styles:
        title_style = style.get('split_title')
        subtitle_style = style.get('split_subtitle')
        text_style = style.get('split_text')
    else:
        title_style = style.get('title')
        subtitle_style = style.get('subtitle')
        text_style = style.get('text')
    
    # Full-page centered container
    with ui.element('div').classes('w-full h-full flex flex-col items-center justify-center').style(
        f'padding: {vertical_padding}% {config.margin_right}% {vertical_padding}% {config.margin_left}%;'
    ):
        # Title
        title_el = ui.label(slide.title).classes(f'text-center {title_override_classes}')
        if title_style:
            title_style.apply(title_el)
        if title_override_css:
            title_el.style(title_override_css)
        
        # Subtitle
        if slide.subtitle:
            subtitle_el = ui.label(slide.subtitle).classes(f'text-center mt-6 {subtitle_override_classes}')
            if subtitle_style:
                subtitle_style.apply(subtitle_el)
            if subtitle_override_css:
                subtitle_el.style(subtitle_override_css)
        
        # Small content - centered below
        if slide.content:
            with ui.element('div').classes(f'mt-12 text-center {text_override_classes}') as content_el:
                if text_style:
                    text_style.apply(content_el)
                if text_override_css:
                    content_el.style(text_override_css)
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
    use_split_styles: bool = False,
) -> None:
    """Build title+content layout - PowerPoint style."""
    # Detect if content is a table (needs to fill space)
    is_table_content = slide.content.strip().startswith('|') and '|' in slide.content
    
    # Get element-specific overrides from slide
    title_override_css, title_override_classes = _get_element_style(slide, 'title')
    subtitle_override_css, subtitle_override_classes = _get_element_style(slide, 'subtitle')
    text_override_css, text_override_classes = _get_element_style(slide, 'text')
    
    # Get theme styles - use split styles for dark backgrounds
    if use_split_styles:
        title_style = style.get('split_title')
        subtitle_style = style.get('split_subtitle')
        text_style = style.get('split_text')
    else:
        title_style = style.get('title')
        subtitle_style = style.get('subtitle')
        text_style = style.get('text')
    
    # Main container with margins
    with ui.element('div').classes('w-full h-full flex flex-col').style(
        f'padding: {config.margin_top}% {config.margin_right}% {config.margin_bottom}% {config.margin_left}%;'
    ):
        # Title region (fixed height, title at top)
        with ui.element('div').classes('flex-shrink-0').style(
            f'margin-bottom: {config.title_gap}%;'
        ):
            title_el = ui.label(slide.title).classes(title_override_classes)
            if title_style:
                title_style.apply(title_el)
            if title_override_css:
                title_el.style(title_override_css)
        
        # Subtitle if present (part of title region)
        if slide.subtitle:
            with ui.element('div').classes('flex-shrink-0').style('margin-bottom: 1rem;'):
                subtitle_el = ui.label(slide.subtitle).classes(subtitle_override_classes)
                if subtitle_style:
                    subtitle_style.apply(subtitle_el)
                if subtitle_override_css:
                    subtitle_el.style(subtitle_override_css)
        
        # Content region (fills remaining space)
        # For tables: center horizontally and vertically. For other content: center vertically
        content_classes = 'flex-1 flex flex-col justify-center'
        if is_table_content:
            content_classes += ' items-center'  # Center table horizontally
        
        with ui.element('div').classes(f'{content_classes} {text_override_classes}') as content_el:
            content_el.style('min-height: 0;')
            if text_style:
                text_style.apply(content_el)
            if text_override_css:
                content_el.style(text_override_css)
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
            # Table: don't force full width so it can be centered
            with ui.element('div').style(
                f'font-size: {px_size}px; line-height: 1.4;'
            ):
                ui.markdown(content)
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
