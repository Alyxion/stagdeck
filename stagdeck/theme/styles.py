"""🎯 Style definitions for theme elements."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ElementStyle:
    """🎯 Style definition for a specific element type.
    
    Represents styling for elements like titles, subtitles, text, etc.
    Can be converted to Tailwind classes or inline CSS.
    
    :ivar color: Text/foreground color (CSS value or Tailwind class).
    :ivar size: Font size (number in px, rem string, or Tailwind class).
    :ivar weight: Font weight (CSS value or Tailwind class).
    :ivar opacity: Opacity value 0.0 to 1.0.
    :ivar font: Font family.
    :ivar classes: Additional Tailwind classes to apply.
    :ivar style: Additional inline CSS styles.
    """
    color: str = ''
    size: str | int | float = ''
    weight: str = ''
    opacity: float = 1.0
    font: str = ''
    classes: str = ''
    style: str = ''
    
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
            style=data.get('style', ''),
        )
    
    def to_tailwind(self) -> str:
        """Convert to Tailwind CSS classes.
        
        :return: Space-separated Tailwind classes.
        """
        classes = []
        
        # Color - convert to Tailwind class
        if self.color:
            if self.color.startswith('text-'):
                classes.append(self.color)
            elif self.color.startswith('#') or self.color.startswith('rgb'):
                # Use Tailwind arbitrary value syntax for CSS colors
                classes.append(f'text-[{self.color}]')
            else:
                classes.append(f'text-[{self.color}]')
        
        # Size - convert to Tailwind if numeric
        if self.size:
            if isinstance(self.size, str) and self.size.startswith('text-'):
                classes.append(self.size)
            elif isinstance(self.size, (int, float)):
                # Map common sizes to Tailwind
                size_map = {
                    12: 'text-xs', 14: 'text-sm', 16: 'text-base',
                    18: 'text-lg', 20: 'text-xl', 24: 'text-2xl',
                    30: 'text-3xl', 36: 'text-4xl', 48: 'text-5xl',
                    60: 'text-6xl', 72: 'text-7xl', 96: 'text-8xl',
                }
                tw_size = size_map.get(int(self.size), f'text-[{int(self.size)}px]')
                classes.append(tw_size)
        
        # Weight
        if self.weight:
            if self.weight.startswith('font-'):
                classes.append(self.weight)
            else:
                weight_map = {
                    '100': 'font-thin', '200': 'font-extralight',
                    '300': 'font-light', '400': 'font-normal',
                    '500': 'font-medium', '600': 'font-semibold',
                    '700': 'font-bold', '800': 'font-extrabold',
                    '900': 'font-black',
                    'thin': 'font-thin', 'light': 'font-light',
                    'normal': 'font-normal', 'medium': 'font-medium',
                    'semibold': 'font-semibold', 'bold': 'font-bold',
                }
                classes.append(weight_map.get(str(self.weight), f'font-[{self.weight}]'))
        
        # Opacity
        if self.opacity < 1.0:
            opacity_pct = int(self.opacity * 100)
            classes.append(f'opacity-{opacity_pct}')
        
        # Additional classes
        if self.classes:
            classes.append(self.classes)
        
        return ' '.join(classes)
    
    def to_css(self) -> str:
        """Convert to inline CSS style string.
        
        :return: CSS style string.
        """
        styles = []
        
        # Color - if CSS value
        if self.color and not self.color.startswith('text-'):
            styles.append(f'color: {self.color}')
        
        # Size
        if self.size:
            if isinstance(self.size, (int, float)):
                styles.append(f'font-size: {self.size}px')
            elif not str(self.size).startswith('text-'):
                styles.append(f'font-size: {self.size}')
        
        # Weight
        if self.weight and not self.weight.startswith('font-'):
            styles.append(f'font-weight: {self.weight}')
        
        # Opacity
        if self.opacity < 1.0:
            styles.append(f'opacity: {self.opacity}')
        
        # Font
        if self.font:
            styles.append(f'font-family: {self.font}')
        
        # Additional styles
        if self.style:
            styles.append(self.style)
        
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
            style=f'{self.style}; {other.style}'.strip('; '),
        )


@dataclass
class LayoutStyle:
    """🖼️ Complete style definition for a layout.
    
    Contains ElementStyles for different element types within a layout.
    
    :ivar name: Layout name.
    :ivar background: Background CSS (color, gradient, image).
    :ivar title: Style for titles.
    :ivar subtitle: Style for subtitles.
    :ivar text: Style for body text.
    :ivar heading: Style for headings.
    :ivar link: Style for links.
    :ivar code_bg: Background for code blocks.
    :ivar code_text: Text style for code.
    :ivar bullet: Style for bullet points.
    :ivar accent: Accent color.
    """
    name: str = ''
    background: str = ''
    title: ElementStyle = field(default_factory=ElementStyle)
    subtitle: ElementStyle = field(default_factory=ElementStyle)
    text: ElementStyle = field(default_factory=ElementStyle)
    heading: ElementStyle = field(default_factory=ElementStyle)
    link: ElementStyle = field(default_factory=ElementStyle)
    code_bg: str = ''
    code_text: ElementStyle = field(default_factory=ElementStyle)
    bullet: ElementStyle = field(default_factory=ElementStyle)
    accent: str = ''
    
    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> 'LayoutStyle':
        """Create LayoutStyle from dictionary.
        
        :param name: Layout name.
        :param data: Dictionary with layout properties.
        :return: New LayoutStyle instance.
        """
        def parse_element(key: str) -> ElementStyle:
            val = data.get(key, {})
            if isinstance(val, dict):
                return ElementStyle.from_dict(val)
            elif isinstance(val, str):
                # Simple string = just color
                return ElementStyle(color=val)
            return ElementStyle()
        
        return cls(
            name=name,
            background=data.get('background', ''),
            title=parse_element('title'),
            subtitle=parse_element('subtitle'),
            text=parse_element('text'),
            heading=parse_element('heading'),
            link=parse_element('link'),
            code_bg=data.get('code_bg', ''),
            code_text=parse_element('code_text'),
            bullet=parse_element('bullet'),
            accent=data.get('accent', ''),
        )
    
    def get_element(self, element: str) -> ElementStyle:
        """Get ElementStyle by name.
        
        :param element: Element name (title, subtitle, text, etc.).
        :return: ElementStyle for the element.
        """
        element_map = {
            'title': self.title,
            'subtitle': self.subtitle,
            'text': self.text,
            'heading': self.heading,
            'link': self.link,
            'code_text': self.code_text,
            'bullet': self.bullet,
        }
        return element_map.get(element, ElementStyle())
    
    def get_color(self, element: str) -> str:
        """Get color for an element.
        
        :param element: Element name.
        :return: Color value.
        """
        return self.get_element(element).color
    
    def to_tailwind(self, element: str) -> str:
        """Get Tailwind classes for an element.
        
        :param element: Element name.
        :return: Tailwind classes.
        """
        return self.get_element(element).to_tailwind()
    
    def to_css(self, element: str) -> str:
        """Get CSS styles for an element.
        
        :param element: Element name.
        :return: CSS style string.
        """
        return self.get_element(element).to_css()
    
    def background_style(self) -> str:
        """Get background as CSS style.
        
        :return: CSS background style.
        """
        if not self.background:
            return ''
        if 'gradient' in self.background or self.background.startswith('linear') or self.background.startswith('radial'):
            return f'background: {self.background};'
        if self.background.startswith('url('):
            return f'background-image: {self.background}; background-size: cover; background-position: center;'
        return f'background-color: {self.background};'
