"""📊 SlideDeck - Data model for presentation decks."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .slide import Slide, SlideRegion

if TYPE_CHECKING:
    from .theme import LayoutStyle, Theme, ThemeContext, ThemeOverrides


def _parse_page_selection(pages: str | list[int] | None, total: int) -> list[int]:
    """Parse page selection into list of 0-based indices.
    
    Supports:
    - None or empty: all pages
    - List of ints: direct indices (1-based)
    - String: comma-separated ranges like "1,3-5,7" (1-based)
    
    :param pages: Page selection (1-based).
    :param total: Total number of pages available.
    :return: List of 0-based indices.
    """
    if pages is None or pages == '' or pages == []:
        return list(range(total))
    
    if isinstance(pages, list):
        # Convert 1-based to 0-based
        return [p - 1 for p in pages if 1 <= p <= total]
    
    # Parse string like "1,3-5,7"
    indices = []
    for part in pages.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            indices.extend(range(start - 1, min(end, total)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total:
                indices.append(idx)
    
    return sorted(set(indices))


@dataclass
class SlideDeck:
    """📚 Collection of slides forming a presentation.
    
    This is the data model only - use DeckViewer for presentation UI.
    
    :ivar title: The presentation title.
    :ivar master: Reference to a master deck for layouts (optional).
    :ivar slides: List of Slide objects.
    :ivar width: Slide width in pixels (default 1920).
    :ivar height: Slide height in pixels (default 1080).
    :ivar default_background: Default background style for all slides.
    :ivar default_layout: Default layout name from master deck.
    :ivar default_style: Default LayoutStyle for all slides (cascade fallback).
    :ivar default_step_duration: Default duration in seconds for each step.
    :ivar default_transition_duration: Default transition animation duration in seconds.
    :ivar theme_context: Theme context for cascading theme resolution.
    :ivar media_folders: Registered media folders (url_path -> local_path).
    :ivar source_files: Markdown files loaded via add_from_file() for hot-reload.
    """
    title: str = 'Presentation'
    master: 'SlideDeck | None' = None
    slides: list[Slide] = field(default_factory=list)
    width: int = 1920
    height: int = 1080
    default_background: str = ''
    default_layout: str = ''
    default_style: 'LayoutStyle | None' = None
    default_step_duration: float = 5.0
    default_transition_duration: float = 0.5
    theme_context: 'ThemeContext | None' = None
    media_folders: dict[str, Path] = field(default_factory=dict)
    source_files: list[Path] = field(default_factory=list)
    
    @property
    def aspect_ratio(self) -> float:
        """📐 Get the aspect ratio (width/height)."""
        return self.width / self.height
    
    @property
    def total_slides(self) -> int:
        """🔢 Get total number of slides."""
        return len(self.slides)
    
    @property
    def total_steps(self) -> int:
        """🔢 Get total number of steps across all slides."""
        return sum(slide.steps for slide in self.slides)
    
    @property
    def total_duration(self) -> float:
        """⏱️ Get total duration of the presentation in seconds."""
        return sum(
            slide.get_total_duration(self.default_step_duration)
            for slide in self.slides
        )
    
    def add_slide(self, slide: Slide) -> 'SlideDeck':
        """➕ Add a slide to the deck. Returns self for chaining."""
        self.slides.append(slide)
        return self
    
    def add_media_folder(
        self,
        local_path: str | Path,
        url_path: str = '/media',
    ) -> 'SlideDeck':
        """📁 Register a media folder for use in markdown.
        
        The folder will be served at the specified URL path, allowing
        images and other media to be referenced in markdown:
        
        ```python
        deck.add_media_folder('./media')
        
        deck.add('''
        # My Slide
        
        ![inline](/media/diagram.png)
        ''')
        ```
        
        Security: Only files within the registered folder are accessible.
        Path traversal attempts (../) are blocked.
        
        :param local_path: Path to the local folder (absolute or relative).
        :param url_path: URL path prefix (default '/media').
        :return: Self for chaining.
        :raises ValueError: If the folder doesn't exist.
        """
        path = Path(local_path).resolve()
        
        if not path.exists():
            raise ValueError(f"Media folder does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Media path is not a directory: {path}")
        
        # Normalize url_path to start with / and not end with /
        url_path = '/' + url_path.strip('/')
        
        self.media_folders[url_path] = path
        return self
    
    def add(
        self,
        markdown: str = '',
        *,
        name: str = '',
        layout: str = '',
        title: str = '',
        content: str = '',
        subtitle: str = '',
        notes: str = '',
        background: str = '',
        background_color: str = '',  # Alias for background (backward compat)
        style: 'LayoutStyle | None' = None,
        theme_overrides: 'ThemeOverrides | None' = None,
        steps: int = 1,
        step_names: list[str] | None = None,
        step_durations: list[float] | None = None,
        transition_duration: float | None = None,
        **kwargs,
    ) -> 'SlideDeck':
        """➕ Add a slide from markdown or explicit parameters.
        
        Can be called with a single markdown string that includes title,
        subtitle, background, and content following Deckset conventions:
        
        ```python
        deck.add('''
        ![background](#1a1a2e)
        
        # Slide Title
        ## Optional Subtitle
        
        Content goes here...
        ''')
        ```
        
        Or with explicit parameters (backward compatible):
        
        ```python
        deck.add(
            title='Slide Title',
            content='Content here',
            background='#1a1a2e',
        )
        ```
        
        Markdown syntax:
        - `# Heading` = slide title
        - `## Heading` after title = subtitle  
        - `![background](#color)` = background color
        - `![background](image.jpg)` = background image
        - `![](image.jpg)` at start = background image
        - `^ Note text` = presenter notes
        - Everything else = content
        
        :param markdown: Markdown source for the slide (parsed automatically).
        :param name: Slide name (auto-generated if empty).
        :param layout: Master layout name.
        :param title: Slide title (overrides markdown).
        :param content: Slide content (overrides markdown).
        :param subtitle: Slide subtitle (overrides markdown).
        :param notes: Speaker notes (overrides markdown).
        :param background: Background color/gradient/image.
        :param background_color: Alias for background (backward compat).
        :param style: LayoutStyle for this slide.
        :param theme_overrides: Slide-specific theme overrides.
        :param steps: Number of incremental steps.
        :param step_names: Names for each step.
        :param step_durations: Duration for each step.
        :param transition_duration: Transition animation duration.
        :param kwargs: Additional data for layout elements.
        :return: Self for chaining.
        """
        # Parse markdown if provided
        parsed_title = ''
        parsed_subtitle = ''
        parsed_content = ''
        parsed_background = ''
        parsed_background_position = ''
        parsed_notes = ''
        parsed_regions: list[SlideRegion] = []
        parsed_direction = 'horizontal'
        parsed_background_modifiers = ''  # Raw modifier string for ImageView
        parsed_style_overrides: dict[str, Any] = {}  # Collected from markdown
        
        if markdown:
            from .components.markdown_parser import MarkdownParser
            parser = MarkdownParser()
            
            # Use multi-region parser to detect if this is a multi-region slide
            multi = parser.parse_multi_region_markdown(markdown)
            parsed_notes = multi.get('notes', '')
            parsed_direction = multi.get('direction', 'horizontal')
            regions_data = multi.get('regions', [])
            
            # Get name from multi-region parse (applies to all cases)
            parsed_name = multi.get('name', '')
            
            if len(regions_data) > 1:
                # Multi-region slide
                for r in regions_data:
                    # Build region theme context from overrides
                    region_theme = None
                    overlay = r.get('overlay_opacity')
                    blur = r.get('blur_radius')
                    
                    if overlay is not None or blur is not None:
                        from .theme import ThemeContext
                        region_theme = ThemeContext()
                        if overlay is not None:
                            region_theme.slide_overrides.set('overlay', overlay)
                        if blur is not None:
                            region_theme.slide_overrides.set('blur', blur)
                    
                    parsed_regions.append(SlideRegion(
                        image=r.get('image', ''),
                        modifiers=r.get('modifiers', ''),
                        content=r.get('content', ''),
                        title=r.get('title', ''),
                        subtitle=r.get('subtitle', ''),
                        position=r.get('position', ''),
                        theme_context=region_theme,
                    ))
            else:
                # Single-region slide - use standard parsing for backward compat
                parsed = parser.parse_slide_markdown(markdown)
                parsed_title = parsed.get('title', '')
                parsed_subtitle = parsed.get('subtitle', '')
                parsed_content = parsed.get('content', '')
                parsed_background = parsed.get('background', '')
                parsed_background_modifiers = parsed.get('background_modifiers', '')
                parsed_background_position = parsed.get('background_position', '')
                parsed_notes = parsed.get('notes', '')
                parsed_name = parsed.get('name', '')
                
                # Collect style overrides from parsed markdown
                if parsed.get('overlay_opacity') is not None:
                    parsed_style_overrides['overlay'] = parsed['overlay_opacity']
                if parsed.get('blur_radius') is not None:
                    parsed_style_overrides['blur'] = parsed['blur_radius']
                if parsed.get('text_style'):
                    parsed_style_overrides.update(parsed['text_style'])
        else:
            parsed_name = ''
        
        # Explicit params override parsed values
        final_title = title if title else parsed_title
        final_subtitle = subtitle if subtitle else parsed_subtitle
        final_content = content if content else parsed_content
        final_notes = notes if notes else parsed_notes
        
        # Background: explicit > background_color (alias) > parsed
        final_background = background or background_color or parsed_background
        
        # Name: explicit > parsed from [name: ...] > auto-generated
        slide_name = name if name else (parsed_name if parsed_name else f'slide_{len(self.slides)}')
        slide_layout = layout if layout else self.default_layout
        
        # Build data dict from explicit params and kwargs
        data = dict(kwargs)
        if final_title:
            data['title'] = final_title
        if final_subtitle:
            data['subtitle'] = final_subtitle
        if final_content:
            data['body'] = final_content  # Map content to body for layouts
        
        # Build slide theme from overrides
        slide_theme = None
        if parsed_style_overrides or theme_overrides:
            from .theme import ThemeContext
            # Start with deck theme if available, otherwise create empty context
            if self.theme_context:
                slide_theme = self.theme_context.child(**parsed_style_overrides)
            else:
                slide_theme = ThemeContext()
                for key, value in parsed_style_overrides.items():
                    slide_theme.slide_overrides.set(key, value)
            # Apply explicit theme_overrides on top
            if theme_overrides:
                slide_theme.push_slide_overrides(theme_overrides)
        
        # Store parsed overrides in data for layout rendering
        data['_style_overrides'] = parsed_style_overrides
        
        self.slides.append(Slide(
            name=slide_name,
            layout=slide_layout,
            title=final_title,
            content=final_content,
            subtitle=final_subtitle,
            notes=final_notes,
            background_color=final_background,
            background_modifiers=parsed_background_modifiers,
            background_position=parsed_background_position,
            regions=parsed_regions,
            region_direction=parsed_direction,
            theme_context=slide_theme,
            steps=steps,
            step_names=step_names,
            step_durations=step_durations,
            transition_duration=transition_duration if transition_duration is not None else self.default_transition_duration,
            data=data,
        ))
        return self
    
    def add_from_file(
        self,
        path: str | Path,
        pages: str | list[int] | None = None,
        *,
        before: str = '',
        after: str = '',
        name_prefix: str = 'pptx',
        url_prefix: str = '/pptx_slides',
    ) -> 'SlideDeck':
        """📄 Load slides from a markdown or PPTX file.
        
        Supports both markdown (.md) and PowerPoint (.pptx) files.
        For PPTX, LibreOffice is required for first conversion, but cached
        images can be committed to git for deployment without LibreOffice.
        
        Example usage:
        ```python
        # Load all slides from markdown (appends to end)
        deck.add_from_file('slides.md')
        
        # Load specific slides (1-based)
        deck.add_from_file('slides.md', pages='1,3-5')
        deck.add_from_file('slides.md', pages=[1, 3, 4, 5])
        
        # Load from PowerPoint
        deck.add_from_file('presentation.pptx')
        deck.add_from_file('presentation.pptx', pages='2-4')
        
        # Insert slides at specific position
        deck.add_from_file('extra.pptx', after='intro')
        deck.add_from_file('charts.md', before='conclusion')
        ```
        
        :param path: Path to the markdown or PPTX file.
        :param pages: Page selection - None for all, or "1,3-5" or [1,3,4,5] (1-based).
        :param before: Insert before the slide with this name.
        :param after: Insert after the slide with this name.
        :param name_prefix: Prefix for PPTX slide names (e.g., 'pptx' -> 'pptx_001').
        :param url_prefix: URL prefix for serving PPTX images.
        :return: Self for chaining.
        :raises FileNotFoundError: If file doesn't exist.
        :raises ValueError: If both before and after are specified.
        """
        if before and after:
            raise ValueError("Cannot specify both 'before' and 'after'")
        
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Calculate insertion index if before/after specified
        insert_idx = None
        if before or after:
            target_name = before or after
            target_idx = self.get_slide_index(target_name)
            if target_idx is None:
                raise ValueError(f"Slide not found: '{target_name}'")
            insert_idx = target_idx if before else target_idx + 1
        
        # Remember current slide count for insertion
        count_before = len(self.slides)
        
        # Dispatch based on file extension
        if path.suffix.lower() == '.pptx':
            self._add_from_pptx(path, pages, name_prefix, url_prefix)
        else:
            self._add_from_markdown(path, pages)
        
        # Move new slides to insertion point if needed
        if insert_idx is not None:
            new_slides = self.slides[count_before:]
            del self.slides[count_before:]
            for i, slide in enumerate(new_slides):
                self.slides.insert(insert_idx + i, slide)
        
        return self
    
    def _add_from_markdown(
        self,
        path: Path,
        pages: str | list[int] | None,
    ) -> 'SlideDeck':
        """Load slides from a markdown file."""
        from .components.markdown_parser import SLIDE_SEPARATOR
        
        # Track source file for hot-reload
        if path not in self.source_files:
            self.source_files.append(path)
        
        content = path.read_text(encoding='utf-8')
        
        # Split by separator (must be on its own line)
        slides_md = re.split(rf'^{re.escape(SLIDE_SEPARATOR)}\s*$', content, flags=re.MULTILINE)
        slides_md = [s.strip() for s in slides_md if s.strip()]
        
        # Apply page selection
        indices = _parse_page_selection(pages, len(slides_md))
        
        for idx in indices:
            self.add(slides_md[idx])
        
        return self
    
    def _add_from_pptx(
        self,
        path: Path,
        pages: str | list[int] | None,
        name_prefix: str,
        url_prefix: str,
    ) -> 'SlideDeck':
        """Load slides from a PPTX file."""
        from .utils.pptx_loader import convert_pptx_to_images
        
        # Convert PPTX to images (uses hash-based cache)
        cache_dir, image_paths = convert_pptx_to_images(path)
        
        # Register the cache directory as a media folder
        self.add_media_folder(cache_dir, url_prefix)
        
        # Apply page selection
        indices = _parse_page_selection(pages, len(image_paths))
        
        # Add selected slides
        for idx in indices:
            img_path = image_paths[idx]
            slide_num = idx + 1
            name = f"{name_prefix}_{slide_num:03d}"
            
            # Create slide with image as full background
            self.add(
                f"![](/{url_prefix.strip('/')}/{img_path.name})",
                name=name,
            )
        
        return self
    
    def insert(
        self,
        markdown: str = '',
        *,
        before: str = '',
        after: str = '',
        **kwargs,
    ) -> 'SlideDeck':
        """➕ Insert a slide before or after a named slide.
        
        Either `before` or `after` must be specified (not both).
        
        Example:
        ```python
        # Load markdown slides
        deck.add_from_file('slides.md')
        
        # Insert a Python slide after 'features'
        deck.insert('''
        # Dynamic Chart
        ''', after='features')
        
        # Insert before 'conclusion'
        deck.insert(title='Extra Slide', before='conclusion')
        ```
        
        :param markdown: Markdown source for the slide.
        :param before: Insert before the slide with this name.
        :param after: Insert after the slide with this name.
        :param kwargs: Additional parameters passed to add().
        :return: Self for chaining.
        :raises ValueError: If neither/both before/after specified, or name not found.
        """
        if bool(before) == bool(after):
            raise ValueError("Exactly one of 'before' or 'after' must be specified")
        
        target_name = before or after
        target_idx = self.get_slide_index(target_name)
        
        if target_idx is None:
            raise ValueError(f"Slide not found: '{target_name}'")
        
        # Calculate insertion index
        insert_idx = target_idx if before else target_idx + 1
        
        # Add slide to end first (reuse add() logic)
        self.add(markdown, **kwargs)
        
        # Move from end to insertion point
        slide = self.slides.pop()
        self.slides.insert(insert_idx, slide)
        
        return self
    
    def replace(
        self,
        name: str,
        markdown: str = '',
        **kwargs,
    ) -> 'SlideDeck':
        """🔄 Replace a named slide with new content.
        
        Useful for replacing placeholder/dummy slides with Python-generated content.
        
        Example:
        ```python
        # Markdown file has: [name: chart_placeholder]
        deck.add_from_file('slides.md')
        
        # Replace with actual chart
        deck.replace('chart_placeholder', '''
        # Sales Chart
        ''', builder=my_chart_builder)
        ```
        
        :param name: Name of the slide to replace.
        :param markdown: Markdown source for the new slide.
        :param kwargs: Additional parameters passed to add().
        :return: Self for chaining.
        :raises ValueError: If slide name not found.
        """
        target_idx = self.get_slide_index(name)
        
        if target_idx is None:
            raise ValueError(f"Slide not found: '{name}'")
        
        # Add new slide to end (reuse add() logic)
        # Preserve the name unless explicitly overridden
        if 'name' not in kwargs:
            kwargs['name'] = name
        self.add(markdown, **kwargs)
        
        # Remove old slide and move new one to its position
        del self.slides[target_idx]
        slide = self.slides.pop()
        self.slides.insert(target_idx, slide)
        
        return self
    
    def get_layout(self, layout_name: str) -> Slide | None:
        """🎨 Get a layout slide from the master deck.
        
        :param layout_name: Name of the layout to find.
        :return: The layout Slide from master, or None if not found.
        """
        if self.master is None:
            return None
        return self.master.get_slide_by_name(layout_name)
    
    def get_slide(self, index: int) -> Slide | None:
        """🔍 Get a slide by index."""
        if 0 <= index < len(self.slides):
            return self.slides[index]
        return None
    
    def get_slide_by_name(self, name: str) -> Slide | None:
        """🔍 Find a slide by its name."""
        for slide in self.slides:
            if slide.name == name:
                return slide
        return None
    
    def get_slide_index(self, name: str) -> int | None:
        """🔍 Get the index of a slide by its name."""
        for i, slide in enumerate(self.slides):
            if slide.name == name:
                return i
        return None
    
    def get_duration_at(self, slide_index: int, step: int = 0) -> float:
        """⏱️ Get elapsed duration up to a specific slide and step."""
        elapsed = 0.0
        for i, slide in enumerate(self.slides):
            if i < slide_index:
                elapsed += slide.get_total_duration(self.default_step_duration)
            elif i == slide_index:
                elapsed += slide.transition_duration
                for s in range(step):
                    elapsed += slide.get_step_duration(s, self.default_step_duration)
                break
        return elapsed
    
    # =========================================================================
    # 🎨 Theme Management
    # =========================================================================
    
    def use_theme(self, theme: 'Theme | str') -> 'SlideDeck':
        """Set the primary theme for this deck. Returns self for chaining.
        
        :param theme: Theme instance or reference string (e.g., 'default:aurora.json').
        :return: Self for chaining.
        
        Example:
            >>> deck.use_theme('default:aurora.json')
            >>> deck.use_theme('default:midnight.json')
        """
        from .theme import ThemeContext, Theme as ThemeClass
        
        if isinstance(theme, str):
            theme = ThemeClass.from_reference(theme)
        
        if self.theme_context is None:
            self.theme_context = ThemeContext(themes=[theme])
        else:
            self.theme_context.themes.insert(0, theme)
        return self
    
    def use_themes(self, *themes: 'Theme | str') -> 'SlideDeck':
        """Set multiple themes (first is primary). Returns self for chaining.
        
        :param themes: Theme instances or reference strings.
        :return: Self for chaining.
        
        Example:
            >>> deck.use_themes('default:aurora.json', 'default:midnight.json')
        """
        from .theme import ThemeContext
        self.theme_context = ThemeContext.from_themes(*themes)
        return self
    
    def override(self, key: str, value: Any) -> 'SlideDeck':
        """Set a deck-level theme override. Returns self for chaining.
        
        Overrides apply to all slides unless slide has its own override.
        
        :param key: Property key (e.g., 'primary', 'pie_chart.colors').
        :param value: Override value.
        :return: Self for chaining.
        
        Example:
            >>> deck.override('primary', '#ff0000')
            >>> deck.override('pie_chart.colors', ['#f00', '#0f0', '#00f'])
        """
        self._ensure_theme_context()
        self.theme_context.override(key, value)
        return self
    
    def override_palette(self, **kwargs) -> 'SlideDeck':
        """Set multiple palette overrides. Returns self for chaining.
        
        Example:
            >>> deck.override_palette(primary='#ff0000', accent='#00ff00')
        """
        self._ensure_theme_context()
        self.theme_context.override_palette(**kwargs)
        return self
    
    def get_theme_value(self, key: str, default: Any = None) -> Any:
        """Get a resolved theme value.
        
        :param key: Property key.
        :param default: Default if not found.
        :return: Resolved value.
        """
        if self.theme_context is None:
            return default
        return self.theme_context.get(key, default)
    
    def _ensure_theme_context(self) -> None:
        """Ensure theme_context exists, creating default if needed."""
        if self.theme_context is None:
            from .theme import ThemeContext, Theme as ThemeClass
            # Load default theme
            default_theme = ThemeClass.from_reference('default:aurora.json')
            self.theme_context = ThemeContext(themes=[default_theme])
    
    # =========================================================================
    # 🎨 Theme Search Path Management
    # =========================================================================
    
    @staticmethod
    def add_theme_path(symbol: str, path: str | Path) -> None:
        """Register a theme search path symbol.
        
        Allows themes to be referenced using symbol:filename syntax.
        
        :param symbol: Symbol name (e.g., 'corporate', 'brand').
        :param path: Directory containing theme files.
        
        Example:
            >>> SlideDeck.add_theme_path('corporate', '/path/to/themes')
            >>> theme = Theme.from_reference('corporate:main.json')
        """
        from .theme import get_theme_loader
        get_theme_loader().add_search_path(symbol, path)
    
    @staticmethod
    def remove_theme_path(symbol: str) -> None:
        """Remove a registered theme search path.
        
        :param symbol: Symbol to remove (cannot remove 'default').
        """
        from .theme import get_theme_loader
        get_theme_loader().remove_search_path(symbol)
    
    @staticmethod
    def get_theme_paths() -> dict[str, Path]:
        """Get all registered theme search paths.
        
        :return: Dictionary mapping symbols to directory paths.
        """
        from .theme import get_theme_loader
        return get_theme_loader().search_paths
