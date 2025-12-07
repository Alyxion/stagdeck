"""🎨 Theme context for cascading theme resolution with overrides."""

from dataclasses import dataclass, field
from typing import Any

from .theme import Theme


@dataclass
class ThemeOverrides:
    """🎨 Theme property overrides.
    
    Stores overrides that can be applied on top of a theme.
    Supports both palette-level changes (affecting all components)
    and component-specific changes.
    
    :ivar palette: Palette color overrides (e.g., {'primary': '#ff0000'}).
    :ivar components: Component-specific overrides (e.g., {'pie_chart.colors': [...]}).
    """
    palette: dict[str, Any] = field(default_factory=dict)
    components: dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """Check if there are no overrides."""
        return not self.palette and not self.components
    
    def merge(self, other: 'ThemeOverrides') -> 'ThemeOverrides':
        """Merge another override set on top of this one.
        
        :param other: Overrides to merge (takes precedence).
        :return: New merged ThemeOverrides.
        """
        return ThemeOverrides(
            palette={**self.palette, **other.palette},
            components={**self.components, **other.components},
        )
    
    def set(self, key: str, value: Any) -> 'ThemeOverrides':
        """Set an override value. Returns self for chaining.
        
        Key format:
        - Palette: 'primary', 'bg', 'text', etc.
        - Component: 'pie_chart.colors', 'button.primary.bg', etc.
        
        :param key: Override key.
        :param value: Override value.
        :return: Self for chaining.
        """
        if '.' in key:
            self.components[key] = value
        else:
            self.palette[key] = value
        return self
    
    def get(self, key: str) -> Any | None:
        """Get an override value.
        
        :param key: Override key.
        :return: Override value or None.
        """
        if '.' in key:
            return self.components.get(key)
        return self.palette.get(key)
    
    def clear(self) -> 'ThemeOverrides':
        """Clear all overrides. Returns self for chaining."""
        self.palette.clear()
        self.components.clear()
        return self
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'palette': self.palette.copy(),
            'components': self.components.copy(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ThemeOverrides':
        """Create from dictionary."""
        return cls(
            palette=data.get('palette', {}),
            components=data.get('components', {}),
        )


@dataclass
class ThemeContext:
    """🎨 Theme context with cascading resolution.
    
    Manages a stack of themes with overrides at each level:
    1. Base themes (first is default, others are fallbacks)
    2. Deck-level overrides
    3. Slide-level overrides
    
    Resolution order (highest priority first):
    - Slide overrides
    - Deck overrides  
    - First theme with the value
    
    :ivar themes: List of themes (first is primary).
    :ivar deck_overrides: Deck-level overrides.
    :ivar slide_overrides: Slide-level overrides.
    """
    themes: list[Theme] = field(default_factory=list)
    deck_overrides: ThemeOverrides = field(default_factory=ThemeOverrides)
    slide_overrides: ThemeOverrides = field(default_factory=ThemeOverrides)
    
    _resolved_cache: dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_theme(cls, theme: Theme | str) -> 'ThemeContext':
        """Create context from a single theme.
        
        :param theme: Theme instance or reference string.
        :return: New ThemeContext.
        """
        if isinstance(theme, str):
            theme = Theme.from_reference(theme)
        return cls(themes=[theme])
    
    @classmethod
    def from_themes(cls, *themes: Theme | str) -> 'ThemeContext':
        """Create context from multiple themes.
        
        :param themes: Theme instances or reference strings.
        :return: New ThemeContext.
        """
        resolved = []
        for t in themes:
            if isinstance(t, str):
                resolved.append(Theme.from_reference(t))
            else:
                resolved.append(t)
        return cls(themes=resolved)
    
    @property
    def primary_theme(self) -> Theme | None:
        """Get the primary (first) theme."""
        return self.themes[0] if self.themes else None
    
    def add_theme(self, theme: Theme | str) -> 'ThemeContext':
        """Add a fallback theme. Returns self for chaining.
        
        :param theme: Theme to add.
        :return: Self for chaining.
        """
        if isinstance(theme, str):
            theme = Theme.from_reference(theme)
        self.themes.append(theme)
        self._resolved_cache.clear()
        return self
    
    # =========================================================================
    # 🎨 Deck-level overrides
    # =========================================================================
    
    def override(self, key: str, value: Any) -> 'ThemeContext':
        """Set a deck-level override. Returns self for chaining.
        
        :param key: Property key (e.g., 'primary', 'pie_chart.colors').
        :param value: Override value.
        :return: Self for chaining.
        
        Example:
            >>> ctx.override('primary', '#ff0000')
            >>> ctx.override('pie_chart.colors', ['#f00', '#0f0', '#00f'])
        """
        self.deck_overrides.set(key, value)
        self._resolved_cache.clear()
        return self
    
    def override_palette(self, **kwargs) -> 'ThemeContext':
        """Set multiple palette overrides. Returns self for chaining.
        
        Example:
            >>> ctx.override_palette(primary='#ff0000', accent='#00ff00')
        """
        for key, value in kwargs.items():
            self.deck_overrides.palette[key] = value
        self._resolved_cache.clear()
        return self
    
    def clear_deck_overrides(self) -> 'ThemeContext':
        """Clear all deck-level overrides. Returns self for chaining."""
        self.deck_overrides.clear()
        self._resolved_cache.clear()
        return self
    
    # =========================================================================
    # 🎴 Slide-level overrides (temporary, cleared per slide)
    # =========================================================================
    
    def push_slide_override(self, key: str, value: Any) -> 'ThemeContext':
        """Set a slide-level override. Returns self for chaining.
        
        These are typically cleared after each slide renders.
        
        :param key: Property key.
        :param value: Override value.
        :return: Self for chaining.
        """
        self.slide_overrides.set(key, value)
        self._resolved_cache.clear()
        return self
    
    def push_slide_overrides(self, overrides: ThemeOverrides) -> 'ThemeContext':
        """Apply a set of slide overrides. Returns self for chaining.
        
        :param overrides: Overrides to apply.
        :return: Self for chaining.
        """
        self.slide_overrides = self.slide_overrides.merge(overrides)
        self._resolved_cache.clear()
        return self
    
    def clear_slide_overrides(self) -> 'ThemeContext':
        """Clear slide-level overrides. Returns self for chaining."""
        self.slide_overrides.clear()
        self._resolved_cache.clear()
        return self
    
    # =========================================================================
    # 🔍 Value resolution
    # =========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a resolved theme value with overrides applied.
        
        Resolution order:
        1. Slide overrides
        2. Deck overrides
        3. Theme variables (first theme with value)
        
        :param key: Property key (e.g., 'primary', 'text.h1.color').
        :param default: Default value if not found.
        :return: Resolved value.
        """
        # Check cache
        cache_key = f'{key}:{id(self.slide_overrides)}:{id(self.deck_overrides)}'
        if cache_key in self._resolved_cache:
            return self._resolved_cache[cache_key]
        
        # Check slide overrides
        value = self.slide_overrides.get(key)
        if value is not None:
            self._resolved_cache[cache_key] = value
            return value
        
        # Check deck overrides
        value = self.deck_overrides.get(key)
        if value is not None:
            self._resolved_cache[cache_key] = value
            return value
        
        # Check themes (first match wins)
        for theme in self.themes:
            # Use theme.get() which handles variables, computed, and layouts
            value = theme.get(key)
            if value is not None:
                self._resolved_cache[cache_key] = value
                return value
        
        return default
    
    def _get_nested(self, theme: Theme, path: str) -> Any | None:
        """Get a nested value from theme data.
        
        :param theme: Theme to search.
        :param path: Dot-separated path (e.g., 'text.h1.color').
        :return: Value or None.
        """
        # This would need theme to expose raw data
        # For now, return None - can be enhanced later
        return None
    
    def get_palette(self) -> dict[str, Any]:
        """Get the merged palette with all overrides applied.
        
        :return: Complete palette dictionary.
        """
        palette = {}
        
        # Start with themes (reverse order so first theme wins)
        for theme in reversed(self.themes):
            palette.update(theme.variables)
        
        # Apply deck overrides
        palette.update(self.deck_overrides.palette)
        
        # Apply slide overrides
        palette.update(self.slide_overrides.palette)
        
        return palette
    
    def resolve_variables(self, text: str) -> str:
        """Resolve ${variable} references in text.
        
        :param text: Text with variable references.
        :return: Text with variables resolved.
        """
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = self.get(var_name)
            return str(value) if value is not None else match.group(0)
        
        return re.sub(r'\$\{(\w+)\}', replace_var, text)


# Convenience functions for creating override sets
def overrides(**kwargs) -> ThemeOverrides:
    """Create a ThemeOverrides from keyword arguments.
    
    Example:
        >>> slide_overrides = overrides(primary='#ff0000', accent='#00ff00')
    """
    result = ThemeOverrides()
    for key, value in kwargs.items():
        result.set(key, value)
    return result
