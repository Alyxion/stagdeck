"""🎯 Style definitions for theme elements."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nicegui.element import Element


@dataclass
class ElementStyle:
    """🎯 Style definition for a specific element type.
    
    Represents styling for any element (titles, text, table headers, chart labels, etc.).
    Supports both Tailwind classes AND inline CSS - they are additive, not alternatives.
    
    :ivar color: Text/foreground color (CSS value).
    :ivar size: Font size (number in px or string like '5rem').
    :ivar weight: Font weight (CSS value like 'bold', '600').
    :ivar opacity: Opacity value 0.0 to 1.0.
    :ivar font: Font family.
    :ivar classes: Tailwind classes (always applied alongside CSS).
    :ivar css: Additional inline CSS (always applied alongside classes).
    """
    color: str = ''
    size: str | int | float = ''
    weight: str = ''
    opacity: float = 1.0
    font: str = ''
    classes: str = ''
    css: str = ''
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ElementStyle':
        """Create ElementStyle from dictionary.
        
        :param data: Dictionary with style properties.
        :return: New ElementStyle instance.
        """
        return cls(
            color=data.get('color', ''),
            size=data.get('size', ''),
            weight=data.get('weight', ''),
            opacity=data.get('opacity', 1.0),
            font=data.get('font', ''),
            classes=data.get('classes', ''),
            css=data.get('css', data.get('style', '')),  # Support both 'css' and legacy 'style'
        )
    
    def apply(self, element: 'Element') -> 'Element':
        """Apply both Tailwind classes AND CSS to a NiceGUI element.
        
        This is the preferred method - it applies classes and CSS additively.
        
        :param element: NiceGUI element to style.
        :return: The element (for chaining).
        """
        # Apply Tailwind classes
        tailwind = self.to_tailwind()
        if tailwind:
            element.classes(tailwind)
        
        # Apply CSS
        css = self.to_css()
        if css:
            element.style(css)
        
        return element
    
    def to_tailwind(self) -> str:
        """Get Tailwind CSS classes only.
        
        Note: Prefer apply() which uses both classes AND CSS.
        
        :return: Space-separated Tailwind classes.
        """
        parts = []
        
        # Opacity via Tailwind
        if self.opacity < 1.0:
            opacity_pct = int(self.opacity * 100)
            parts.append(f'opacity-{opacity_pct}')
        
        # User-provided classes
        if self.classes:
            parts.append(self.classes)
        
        return ' '.join(parts)
    
    def to_css(self) -> str:
        """Get inline CSS style string.
        
        Note: Prefer apply() which uses both classes AND CSS.
        
        :return: CSS style string.
        """
        styles = []
        
        if self.color:
            styles.append(f'color: {self.color}')
        
        if self.size:
            if isinstance(self.size, (int, float)):
                styles.append(f'font-size: {self.size}px')
            else:
                styles.append(f'font-size: {self.size}')
        
        if self.weight:
            styles.append(f'font-weight: {self.weight}')
        
        if self.opacity < 1.0:
            styles.append(f'opacity: {self.opacity}')
        
        if self.font:
            styles.append(f'font-family: {self.font}')
        
        if self.css:
            styles.append(self.css)
        
        return '; '.join(styles)
    
    def merge(self, other: 'ElementStyle') -> 'ElementStyle':
        """Merge with another style, other takes precedence.
        
        :param other: Style to merge with.
        :return: New merged ElementStyle.
        """
        return ElementStyle(
            color=other.color or self.color,
            size=other.size or self.size,
            weight=other.weight or self.weight,
            opacity=other.opacity if other.opacity != 1.0 else self.opacity,
            font=other.font or self.font,
            classes=f'{self.classes} {other.classes}'.strip(),
            css=f'{self.css}; {other.css}'.strip('; '),
        )


# Default styles loaded from midnight.json theme
# Cached after first load
_default_style: 'SlideStyle | None' = None


def get_default_style() -> 'SlideStyle':
    """Get the default SlideStyle from midnight.json theme.
    
    Loads and caches the default style on first call.
    """
    global _default_style
    if _default_style is None:
        _default_style = SlideStyle.from_theme('midnight')
    return _default_style


class SlideStyle:
    """🎨 Dict-based style container for slides.
    
    Stores ElementStyles by name (e.g., 'title', 'subtitle', 'text', 'table.header').
    Supports any element name from the theme JSON files.
    User-provided styles are merged with defaults from midnight.json.
    
    :ivar name: Style/theme name.
    :ivar background: Background CSS (color, gradient, image).
    :ivar _elements: Dict mapping element names to ElementStyle.
    """
    
    def __init__(
        self,
        name: str = '',
        background: str = '',
        elements: dict[str, ElementStyle] | None = None,
        **kwargs: ElementStyle,
    ):
        """Create a SlideStyle.
        
        :param name: Style name.
        :param background: Background CSS.
        :param elements: Dict of element name -> ElementStyle.
        :param kwargs: Element styles as keyword args (e.g., title=ElementStyle(...)).
        """
        self.name = name
        self.background = background
        self._elements: dict[str, ElementStyle] = elements.copy() if elements else {}
        
        # Support keyword args for common elements
        for key, value in kwargs.items():
            if isinstance(value, ElementStyle):
                self._elements[key] = value
    
    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> 'SlideStyle':
        """Create SlideStyle from dictionary.
        
        :param name: Style name.
        :param data: Dictionary with style properties.
        :return: New SlideStyle instance.
        """
        elements: dict[str, ElementStyle] = {}
        background = data.get('background', '')
        
        for key, value in data.items():
            if key == 'background':
                continue
            if isinstance(value, dict):
                elements[key] = ElementStyle.from_dict(value)
        
        return cls(name=name, background=background, elements=elements)
    
    @classmethod
    def from_theme(cls, theme_name: str) -> 'SlideStyle':
        """Load SlideStyle from a theme JSON file.
        
        Loads all element styles from the theme, not just title/subtitle/text.
        
        :param theme_name: Theme name (e.g., 'midnight', 'aurora').
        :return: SlideStyle with all elements from theme.
        """
        import json
        themes_dir = Path(__file__).parent.parent / 'templates' / 'themes'
        theme_path = themes_dir / f'{theme_name}.json'
        
        if not theme_path.exists():
            # Fallback to hardcoded defaults if theme not found
            return cls(
                name=theme_name,
                elements={
                    'title': ElementStyle(color='#ffffff', size=80, weight='bold'),
                    'subtitle': ElementStyle(color='#94a3b8', size=40),
                    'text': ElementStyle(color='#e2e8f0', size=32),
                },
            )
        
        with open(theme_path) as f:
            data = json.load(f)
        
        # Handle theme inheritance
        if 'extends' in data:
            base = cls.from_theme(data['extends'].replace('.json', ''))
        else:
            base = None
        
        # Build palette for variable resolution
        palette = {}
        palette.update(data.get('constants', {}))
        palette.update(data.get('palette', {}))
        
        def resolve_value(val: Any) -> Any:
            """Resolve ${var} references in values."""
            if isinstance(val, str) and val.startswith('${') and val.endswith('}'):
                key = val[2:-1]
                return palette.get(key, val)
            return val
        
        def parse_element(elem_data: dict) -> ElementStyle:
            """Parse element dict to ElementStyle."""
            if not elem_data or not isinstance(elem_data, dict):
                return ElementStyle()
            return ElementStyle(
                color=resolve_value(elem_data.get('color', '')),
                size=resolve_value(elem_data.get('size', '')),
                weight=resolve_value(elem_data.get('weight', '')),
                opacity=elem_data.get('opacity', 1.0),
                classes=elem_data.get('classes', ''),
                css=elem_data.get('css', elem_data.get('style', '')),
            )
        
        # Parse all element sections from theme
        elements: dict[str, ElementStyle] = {}
        
        # Get slide section (primary for presentations)
        slide_data = data.get('slide', {})
        background = resolve_value(slide_data.get('background', ''))
        
        # Parse slide elements
        for key, value in slide_data.items():
            if key != 'background' and isinstance(value, dict):
                elements[key] = parse_element(value)
        
        # Parse other sections (text, table, chart, etc.)
        for section_name in ['text', 'list', 'table', 'code', 'container', 'badge', 'stat']:
            section = data.get(section_name, {})
            for key, value in section.items():
                if isinstance(value, dict):
                    elements[f'{section_name}.{key}'] = parse_element(value)
        
        style = cls(name=theme_name, background=background, elements=elements)
        
        # Merge with base theme if extending
        if base:
            style = base.merge(style)
        
        return style
    
    def get(self, element_name: str) -> ElementStyle:
        """Get ElementStyle by name, merged with defaults.
        
        :param element_name: Element name (e.g., 'title', 'text.h1', 'table.header').
        :return: ElementStyle with defaults applied.
        """
        # Get user style (may be empty)
        user_style = self._elements.get(element_name, ElementStyle())
        
        # Get default style (avoid recursion if we ARE the default)
        if self is _default_style:
            return user_style
        
        defaults = get_default_style()
        default_style = defaults._elements.get(element_name, ElementStyle())
        
        return default_style.merge(user_style)
    
    def set(self, element_name: str, style: ElementStyle) -> None:
        """Set ElementStyle for an element.
        
        :param element_name: Element name.
        :param style: ElementStyle to set.
        """
        self._elements[element_name] = style
    
    def merge(self, other: 'SlideStyle') -> 'SlideStyle':
        """Merge with another style, other takes precedence.
        
        :param other: Style to merge with.
        :return: New merged SlideStyle.
        """
        merged_elements = dict(self._elements)
        for name, style in other._elements.items():
            if name in merged_elements:
                merged_elements[name] = merged_elements[name].merge(style)
            else:
                merged_elements[name] = style
        
        return SlideStyle(
            name=other.name or self.name,
            background=other.background or self.background,
            elements=merged_elements,
        )
    
    # Compatibility methods for existing code
    def get_element(self, element: str) -> ElementStyle:
        """Alias for get() - compatibility with old LayoutStyle API."""
        return self.get(element)
    
    def to_tailwind(self, element: str) -> str:
        """Get Tailwind classes for an element."""
        return self.get(element).to_tailwind()
    
    def to_css(self, element: str) -> str:
        """Get CSS styles for an element."""
        return self.get(element).to_css()
    
    def apply(self, element_name: str, ui_element: 'Element') -> 'Element':
        """Apply style to a NiceGUI element.
        
        :param element_name: Style element name (e.g., 'title').
        :param ui_element: NiceGUI element to style.
        :return: The element (for chaining).
        """
        return self.get(element_name).apply(ui_element)
    
    def background_style(self) -> str:
        """Get background as CSS style."""
        if not self.background:
            return ''
        if 'gradient' in self.background or self.background.startswith('linear') or self.background.startswith('radial'):
            return f'background: {self.background};'
        if self.background.startswith('url('):
            return f'background-image: {self.background}; background-size: cover; background-position: center;'
        return f'background-color: {self.background};'


# Backwards compatibility alias
LayoutStyle = SlideStyle
