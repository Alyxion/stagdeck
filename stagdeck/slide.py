"""🎴 Slide component for presentations."""

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .theme import LayoutStyle, ThemeOverrides, ThemeContext
    from .slide_deck import SlideDeck


@dataclass
class SlideRegion:
    """📦 A region within a multi-region slide.
    
    Each region has an optional image and content that are displayed together.
    Regions are laid out horizontally or vertically based on the layout direction.
    
    :ivar image: Background image URL for this region (or '').
    :ivar modifiers: Raw modifier string from markdown (e.g., "blur:8 overlay:0.5 left").
    :ivar content: Markdown content for this region.
    :ivar title: Optional title extracted from content.
    :ivar subtitle: Optional subtitle extracted from content.
    :ivar position: Background position hint ('left', 'right', 'top', 'bottom', '').
    :ivar theme_context: ThemeContext for this region. Falls back to slide's theme if not set.
    """
    image: str = ''
    modifiers: str = ''  # Raw modifier string for ImageView
    content: str = ''
    title: str = ''
    subtitle: str = ''
    position: str = ''  # For background-position alignment
    theme_context: 'ThemeContext | None' = None


@dataclass
class Slide:
    """🎴 Represents a single slide in a presentation.
    
    :ivar name: Unique identifier for this slide. Auto-generated if not provided.
    :ivar layout: Name of the master layout to use (renders as base layer).
    :ivar title: The slide title displayed at the top.
    :ivar content: Main content - can be plain text or markdown.
    :ivar final_content: Content used for layout sizing (for animation stability).
                        If None, uses content. This ensures progressive reveals
                        don't cause layout shifts.
    :ivar subtitle: Optional subtitle below the title.
    :ivar notes: Speaker notes (not displayed during presentation).
    :ivar background_color: CSS color/gradient for background (if no layout).
    :ivar background_position: Position for split layouts ('left', 'right', 'top', 'bottom', or '').
    :ivar regions: List of SlideRegion for multi-region layouts.
    :ivar region_direction: Layout direction for regions ('horizontal' or 'vertical').
    :ivar theme_context: ThemeContext for this slide. Falls back to deck's theme if not set.
    :ivar steps: Total number of steps in this slide (for incremental reveals).
    :ivar step_names: Names for each step. Auto-generated if not provided.
    :ivar step_durations: Duration in seconds for each step. If None, uses deck default.
    :ivar transition_duration: Duration of transition animation to this slide in seconds.
    :ivar data: Parsed/resolved content dict for layout elements.
    """
    name: str = ''
    layout: str = ''
    title: str = ''
    content: str = ''
    final_content: str | None = None  # For animation-stable sizing
    subtitle: str = ''
    notes: str = ''
    # Runtime context (set during build, not persisted)
    _build_context: dict = field(default_factory=dict, repr=False)
    background_color: str = ''
    background_modifiers: str = ''  # Raw modifier string for ImageView
    background_position: str = ''  # 'left', 'right', 'top', 'bottom', or '' for full
    regions: list[SlideRegion] = field(default_factory=list)  # Multi-region content
    region_direction: str = 'horizontal'  # 'horizontal' or 'vertical'
    theme_context: 'ThemeContext | None' = None  # Slide-level theme, falls back to deck
    steps: int = 1
    step_names: list[str] | None = None
    step_durations: list[float] | None = None
    transition_duration: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)  # Parsed/resolved content for elements
    
    def get_sizing_content(self) -> str:
        """Get content used for layout sizing (final_content or content)."""
        return self.final_content if self.final_content is not None else self.content
    
    def has_custom_build(self) -> bool:
        """🔧 Check if slide has a custom async build_content method."""
        # Check if build_content is overridden (not the base class version)
        return type(self).build_content is not Slide.build_content
    
    # =========================================================================
    # 🎨 Theme Override Methods
    # =========================================================================
    
    def override(self, key: str, value: Any) -> 'Slide':
        """Set a slide-level theme override. Returns self for chaining.
        
        :param key: Property key (e.g., 'primary', 'pie_chart.colors').
        :param value: Override value.
        :return: Self for chaining.
        
        Example:
            >>> slide.override('primary', '#ff0000')
            >>> slide.override('pie_chart.colors', ['#f00', '#0f0'])
        """
        self._ensure_theme_context()
        self.theme_context.slide_overrides.set(key, value)
        return self
    
    def override_palette(self, **kwargs) -> 'Slide':
        """Set multiple palette overrides. Returns self for chaining.
        
        Example:
            >>> slide.override_palette(primary='#ff0000', accent='#00ff00')
        """
        self._ensure_theme_context()
        for key, value in kwargs.items():
            self.theme_context.slide_overrides.palette[key] = value
        return self
    
    def _ensure_theme_context(self) -> None:
        """Ensure theme context exists."""
        if self.theme_context is None:
            from .theme import ThemeContext
            self.theme_context = ThemeContext()
    
    def get_style(
        self,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> 'LayoutStyle':
        """🎨 Get the style for this slide.
        
        Returns style in priority order:
        1. This slide's style (if set)
        2. Master layout's style (if using a layout)
        3. Deck's default_style (if set)
        4. Default content style
        
        :param master_slide: The resolved master layout slide.
        :param deck: The parent deck for default_style fallback.
        :return: LayoutStyle for styling elements.
        """
        from .theme import LayoutStyle
        
        # Use slide's theme to get style if set
        if self.theme_context is not None:
            # Get layout style from theme context
            layout = self.theme_context.get('layouts.content')
            if layout is not None:
                return layout
        
        # Use master layout's theme if available
        if master_slide is not None and master_slide.theme_context is not None:
            layout = master_slide.theme_context.get('layouts.content')
            if layout is not None:
                return layout
        
        # Use deck's default style if available
        if deck is not None and deck.default_style is not None:
            return deck.default_style
        
        # Default to empty style
        return LayoutStyle()
    
    def get_element_style(self, element: str, master_slide: 'Slide | None' = None) -> str:
        """🎨 Get Tailwind classes for a specific element type.
        
        Convenience method for use in builders.
        
        :param element: Element name ('title', 'subtitle', 'text', etc.).
        :param master_slide: The resolved master layout slide.
        :return: Tailwind classes for the element.
        """
        return self.get_style(master_slide).to_tailwind(element)
    
    async def build(
        self,
        step: int = 0,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> None:
        """🏗️ Build this slide, optionally layered on top of a master slide.
        
        Slides can be composed: master renders first, then this slide layers on top.
        Multiple levels of inheritance are supported.
        
        :param step: Current step index for incremental reveals.
        :param master_slide: Optional master slide to render as base layer.
        :param deck: Parent deck for style cascade fallback.
        """
        from nicegui import ui
        
        if master_slide is not None:
            # Layered mode: master below, content on top
            with ui.element('div').classes('w-full h-full relative'):
                # Layer 0: Master slide
                with ui.element('div').classes('absolute inset-0 z-0'):
                    await master_slide.build(step=step, master_slide=None, deck=deck)
                
                # Layer 1: This slide's content
                with ui.element('div').classes('absolute inset-0 z-10'):
                    await self._build_content(step, master_slide, deck)
        else:
            # Simple mode: just render content directly
            await self._build_content(step, None, deck)
    
    async def _build_content(
        self,
        step: int = 0,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> None:
        """🏗️ Build slide content (custom build_content or default).
        
        If the subclass overrides build_content(), it sets up the layout frame
        (background, title) and calls build_content() for the content area.
        Otherwise uses the default markdown layout system.
        """
        if self.has_custom_build():
            await self._build_custom_slide(step, master_slide, deck)
        else:
            self._build_default_content(step, master_slide, deck)
    
    # =========================================================================
    # 🎨 Layout Helper Methods - for use in build_content()
    # =========================================================================
    
    def add_content_area(
        self,
        align: str = 'center',
        background: str = '',
        background_modifiers: str = '',
    ):
        """📦 Add a content area container for custom NiceGUI components.
        
        Use as a context manager to add content:
        
            with self.add_content_area():
                ui.label('Hello')
                ui.button('Click me')
        
        :param align: Content alignment - 'center', 'left', 'right', 'top', 'bottom'.
        :param background: Optional background color/gradient/image URL.
        :param background_modifiers: Modifiers like 'blur:8 overlay:0.5'.
        :return: Context manager for the content container.
        
        Example:
            async def build_content(self, step: int = 0):
                with self.add_content_area(align='left'):
                    ui.label('Left-aligned content')
        """
        from nicegui import ui
        from .components.content_elements import ImageView
        
        # Alignment classes
        align_classes = {
            'center': 'items-center justify-center',
            'left': 'items-start justify-center',
            'right': 'items-end justify-center',
            'top': 'items-center justify-start',
            'bottom': 'items-center justify-end',
        }
        classes = align_classes.get(align, align_classes['center'])
        
        # Create container
        container = ui.element('div').classes(f'flex-1 flex flex-col {classes} w-full')
        
        # Add background if specified
        if background:
            if background.startswith('url(') or background.startswith('/'):
                # Image background
                bg_url = background if background.startswith('url(') else f'url({background})'
                image_view = ImageView(bg_url, background_modifiers)
                with container:
                    image_view.build_background(
                        container_classes='absolute inset-0',
                        theme_overlay_opacity=0.5,
                    )
            else:
                # Color/gradient
                container.style(f'background: {background};')
        
        return container
    
    def add_section(
        self,
        position: str = '',
        background: str = '',
        background_modifiers: str = '',
        width: str = '',
        height: str = '',
    ):
        """📐 Add a section/region within the slide.
        
        Creates a positioned section, similar to markdown split layouts.
        
        :param position: 'left', 'right', 'top', 'bottom', or '' for full.
        :param background: Background color/gradient/image URL.
        :param background_modifiers: Modifiers like 'blur:8 overlay:0.5'.
        :param width: Custom width (e.g., '60%'). Defaults based on position.
        :param height: Custom height (e.g., '40%'). Defaults based on position.
        :return: Context manager for the section container.
        
        Example:
            async def build_content(self, step: int = 0):
                with self.add_section(position='left', background='/media/photo.jpg'):
                    pass  # Image fills left half
                with self.add_section(position='right'):
                    ui.label('Content on right')
        """
        from nicegui import ui
        from .components.content_elements import ImageView
        
        # Position-based sizing
        if position == 'left':
            classes = 'absolute inset-y-0 left-0'
            default_width = '50%'
            style = f'width: {width or default_width};'
        elif position == 'right':
            classes = 'absolute inset-y-0 right-0'
            default_width = '50%'
            style = f'width: {width or default_width};'
        elif position == 'top':
            classes = 'absolute inset-x-0 top-0'
            default_height = '50%'
            style = f'height: {height or default_height};'
        elif position == 'bottom':
            classes = 'absolute inset-x-0 bottom-0'
            default_height = '50%'
            style = f'height: {height or default_height};'
        else:
            classes = 'w-full h-full'
            style = ''
        
        container = ui.element('div').classes(f'{classes} flex flex-col items-center justify-center overflow-hidden')
        if style:
            container.style(style)
        
        # Add background
        if background:
            if background.startswith('url(') or background.startswith('/'):
                bg_url = background if background.startswith('url(') else f'url({background})'
                image_view = ImageView(bg_url, background_modifiers)
                with container:
                    image_view.build_background(
                        container_classes='absolute inset-0',
                        theme_overlay_opacity=0.5,
                    )
            else:
                container.style(f'background: {background};')
        
        return container
    
    async def build_content(self, step: int = 0) -> None:
        """🎨 Override this method to build custom slide content.
        
        This is called after the slide frame (background, title) is set up.
        Use layout helpers like add_content_area() and add_section().
        
        :param step: Current animation step (0-based).
        
        Example:
            @dataclass
            class MySlide(Slide):
                async def build_content(self, step: int = 0):
                    with self.add_content_area():
                        ui.label('Hello World').classes('text-4xl')
        """
        pass  # Base implementation does nothing
    
    async def _build_custom_slide(
        self,
        step: int = 0,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> None:
        """🔧 Build slide with custom build_content() method.
        
        Sets up the layout frame (background, title) then calls build_content().
        """
        from nicegui import ui
        from .components.slide_layout import (
            _get_background_style, _has_background_image, DEFAULT_CONFIG
        )
        from .components.content_elements import ImageView
        
        style = self.get_style(master_slide, deck)
        config = DEFAULT_CONFIG
        
        # Store context for helper methods
        self._build_context = {
            'step': step,
            'style': style,
            'config': config,
            'master_slide': master_slide,
            'deck': deck,
        }
        
        # Get theme defaults
        overlay_style = style.get('overlay')
        theme_overlay_opacity = getattr(overlay_style, 'opacity', 0.5) if overlay_style else 0.5
        theme_blur_radius = 4
        
        split_bg_style = style.get('split_background')
        split_bg_color = split_bg_style.color if split_bg_style.color else '#1a1a2e'
        
        # Title styles
        title_style = style.get('split_title') or style.get('title')
        subtitle_style = style.get('split_subtitle') or style.get('subtitle')
        
        position = self.background_position
        is_split = position in ('left', 'right', 'top', 'bottom')
        has_bg_image = _has_background_image(self)
        bg_style = _get_background_style(self)
        
        # Main container
        main_style = '' if (is_split and has_bg_image) else bg_style
        
        with ui.element('div').classes('slide-layout w-full h-full relative').style(main_style):
            # Background image handling
            if is_split and has_bg_image:
                if position == 'left':
                    clip_classes = 'absolute inset-y-0 left-0 w-1/2 overflow-hidden'
                elif position == 'right':
                    clip_classes = 'absolute inset-y-0 right-0 w-1/2 overflow-hidden'
                elif position == 'top':
                    clip_classes = 'absolute inset-x-0 top-0 h-1/2 overflow-hidden'
                else:
                    clip_classes = 'absolute inset-x-0 bottom-0 h-1/2 overflow-hidden'
                
                with ui.element('div').classes(clip_classes):
                    image_view = ImageView(self.background_color, self.background_modifiers)
                    image_view.build_background(
                        container_classes='w-full h-full',
                        theme_overlay_opacity=theme_overlay_opacity,
                        theme_blur_default=theme_blur_radius,
                    )
            elif has_bg_image:
                image_view = ImageView(self.background_color, self.background_modifiers)
                image_view.build_background(
                    container_classes='absolute inset-0',
                    theme_overlay_opacity=theme_overlay_opacity,
                    theme_blur_default=theme_blur_radius,
                )
            
            # Content container positioning
            content_classes = 'relative w-full h-full z-10 flex flex-col'
            content_style = ''
            padding = f'padding: {config.margin_top}% {config.margin_right}% {config.margin_bottom}% {config.margin_left}%;'
            
            if position == 'left':
                content_classes = 'absolute right-0 top-0 w-1/2 h-full z-10 flex flex-col'
                content_style = f'background: {split_bg_color}; {padding}'
            elif position == 'right':
                content_classes = 'absolute left-0 top-0 w-1/2 h-full z-10 flex flex-col'
                content_style = f'background: {split_bg_color}; {padding}'
            elif position == 'top':
                content_classes = 'absolute left-0 bottom-0 w-full h-1/2 z-10 flex flex-col'
                content_style = f'background: {split_bg_color}; {padding}'
            elif position == 'bottom':
                content_classes = 'absolute left-0 top-0 w-full h-1/2 z-10 flex flex-col'
                content_style = f'background: {split_bg_color}; {padding}'
            else:
                content_style = padding
            
            with ui.element('div').classes(content_classes).style(content_style):
                # Title (if set)
                if self.title:
                    title_el = ui.label(self.title)
                    if title_style:
                        title_style.apply(title_el)
                    title_el.style('margin-bottom: 0.5rem;')
                
                # Subtitle (if set)
                if self.subtitle:
                    subtitle_el = ui.label(self.subtitle)
                    if subtitle_style:
                        subtitle_style.apply(subtitle_el)
                    subtitle_el.style('margin-bottom: 1rem;')
                
                # Call custom build_content (async)
                await self.build_content(step)
    
    def _build_default_content(
        self,
        step: int = 0,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> None:
        """🖼️ Build default slide content with automatic layout scaling.
        
        Uses the layout system from components.slide_layout which:
        - Maximizes space usage
        - Provides consistent sizing across slides
        - Supports animation-stable layouts via final_content
        """
        from .components.slide_layout import build_slide_layout
        
        # Get style from theme (cascade: slide → master → deck → default)
        style = self.get_style(master_slide, deck)
        
        # Build with automatic layout detection and scaling
        build_slide_layout(
            slide=self,
            step=step,
            style=style,
            final_content=self.get_sizing_content(),
        )
    
    def get_step_name(self, step: int) -> str:
        """🏷️ Get name for a specific step.
        
        Args:
            step: The step index (0-based).
            
        Returns:
            Step name, or auto-generated name if not specified.
        """
        if self.step_names is not None and step < len(self.step_names):
            return self.step_names[step]
        return f'step_{step}'
    
    def get_step_duration(self, step: int, default_duration: float) -> float:
        """⏱️ Get duration for a specific step.
        
        Args:
            step: The step index (0-based).
            default_duration: Default duration to use if not specified.
            
        Returns:
            Duration in seconds for the step.
        """
        if self.step_durations is None:
            return default_duration
        if step < len(self.step_durations):
            return self.step_durations[step]
        return default_duration
    
    def get_total_duration(self, default_step_duration: float) -> float:
        """⏱️ Get total duration of this slide including all steps and transition.
        
        Args:
            default_step_duration: Default duration per step if not specified.
            
        Returns:
            Total duration in seconds.
        """
        total = self.transition_duration
        for step in range(self.steps):
            total += self.get_step_duration(step, default_step_duration)
        return total
