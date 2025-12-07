"""🎴 Slide component for presentations."""

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .theme import LayoutStyle, ThemeOverrides, ThemeContext
    from .slide_deck import SlideDeck


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
    :ivar builder: Optional custom builder function for complex layouts.
    :ivar background_color: CSS color/gradient for background (if no layout).
    :ivar style: LayoutStyle defining element colors for this slide.
    :ivar theme_overrides: Slide-specific theme overrides.
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
    builder: Callable[[int], None] | Callable[[], None] | None = None
    background_color: str = ''
    style: 'LayoutStyle | None' = None
    theme_overrides: 'ThemeOverrides | None' = None
    steps: int = 1
    step_names: list[str] | None = None
    step_durations: list[float] | None = None
    transition_duration: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)  # Parsed/resolved content for elements
    
    def get_sizing_content(self) -> str:
        """Get content used for layout sizing (final_content or content)."""
        return self.final_content if self.final_content is not None else self.content
    
    def has_custom_builder(self) -> bool:
        """🔧 Check if slide uses a custom builder function."""
        return self.builder is not None
    
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
        self._ensure_overrides()
        self.theme_overrides.set(key, value)
        return self
    
    def override_palette(self, **kwargs) -> 'Slide':
        """Set multiple palette overrides. Returns self for chaining.
        
        Example:
            >>> slide.override_palette(primary='#ff0000', accent='#00ff00')
        """
        self._ensure_overrides()
        for key, value in kwargs.items():
            self.theme_overrides.palette[key] = value
        return self
    
    def _ensure_overrides(self) -> None:
        """Ensure theme_overrides exists."""
        if self.theme_overrides is None:
            from .theme import ThemeOverrides
            self.theme_overrides = ThemeOverrides()
    
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
        
        # Use slide's own style if set
        if self.style is not None:
            return self.style
        
        # Use master layout's style if available
        if master_slide is not None and master_slide.style is not None:
            return master_slide.style
        
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
    
    def build(
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
        import inspect
        
        if master_slide is not None:
            # Layered mode: master below, content on top
            with ui.element('div').classes('w-full h-full relative'):
                # Layer 0: Master slide
                with ui.element('div').classes('absolute inset-0 z-0'):
                    master_slide.build(step=step, master_slide=None, deck=deck)
                
                # Layer 1: This slide's content
                with ui.element('div').classes('absolute inset-0 z-10'):
                    self._build_content(step, master_slide, deck)
        else:
            # Simple mode: just render content directly
            self._build_content(step, None, deck)
    
    def _build_content(
        self,
        step: int = 0,
        master_slide: 'Slide | None' = None,
        deck: 'SlideDeck | None' = None,
    ) -> None:
        """🏗️ Build slide content (custom builder or default)."""
        import inspect
        
        if self.has_custom_builder():
            sig = inspect.signature(self.builder)
            if len(sig.parameters) > 0:
                self.builder(step)
            else:
                self.builder()
        else:
            self._build_default_content(step, master_slide, deck)
    
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
