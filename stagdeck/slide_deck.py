"""📊 SlideDeck - Data model for presentation decks."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .slide import Slide

if TYPE_CHECKING:
    from .theme import LayoutStyle, Theme, ThemeContext, ThemeOverrides


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
    
    def add(
        self,
        name: str = '',
        layout: str = '',
        title: str = '',
        content: str = '',
        subtitle: str = '',
        notes: str = '',
        builder=None,
        background_color: str = '',
        style: 'LayoutStyle | None' = None,
        theme_overrides: 'ThemeOverrides | None' = None,
        steps: int = 1,
        step_names: list[str] | None = None,
        step_durations: list[float] | None = None,
        transition_duration: float | None = None,
        **kwargs,
    ) -> 'SlideDeck':
        """➕ Convenience method to create and add a slide.
        
        :param name: Slide name (auto-generated if empty).
        :param layout: Master layout name.
        :param title: Slide title.
        :param content: Slide content (markdown supported).
        :param subtitle: Slide subtitle.
        :param notes: Speaker notes.
        :param builder: Custom builder function.
        :param background_color: Background color/gradient.
        :param style: LayoutStyle for this slide.
        :param theme_overrides: Slide-specific theme overrides.
        :param steps: Number of incremental steps.
        :param step_names: Names for each step.
        :param step_durations: Duration for each step.
        :param transition_duration: Transition animation duration.
        :param kwargs: Additional data for layout elements (e.g., body, left, right, image).
        :return: Self for chaining.
        """
        slide_name = name if name else f'slide_{len(self.slides)}'
        slide_layout = layout if layout else self.default_layout
        
        # Build data dict from explicit params and kwargs
        data = dict(kwargs)
        if title:
            data['title'] = title
        if subtitle:
            data['subtitle'] = subtitle
        if content:
            data['body'] = content  # Map content to body for layouts
        
        self.slides.append(Slide(
            name=slide_name,
            layout=slide_layout,
            title=title,
            content=content,
            subtitle=subtitle,
            notes=notes,
            builder=builder,
            background_color=background_color,
            style=style,
            theme_overrides=theme_overrides,
            steps=steps,
            step_names=step_names,
            step_durations=step_durations,
            transition_duration=transition_duration if transition_duration is not None else self.default_transition_duration,
            data=data,
        ))
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
