"""Tests for ElementStyle and LayoutStyle."""

import pytest

from stagdeck.theme import ElementStyle, LayoutStyle


class TestElementStyle:
    """Test ElementStyle class."""
    
    def test_create_empty_style(self):
        """Create empty element style."""
        style = ElementStyle()
        assert style.color == ''
        assert style.opacity == 1.0
    
    def test_create_with_color(self):
        """Create style with color."""
        style = ElementStyle(color='#ff0000')
        assert style.color == '#ff0000'
    
    def test_to_tailwind_hex_color(self):
        """Convert hex color to Tailwind class."""
        style = ElementStyle(color='#ff0000')
        classes = style.to_tailwind()
        assert 'text-[#ff0000]' in classes
    
    def test_to_tailwind_existing_class(self):
        """Pass through existing Tailwind class."""
        style = ElementStyle(color='text-white')
        classes = style.to_tailwind()
        assert 'text-white' in classes
    
    def test_to_tailwind_weight(self):
        """Convert weight to Tailwind class."""
        style = ElementStyle(weight='bold')
        classes = style.to_tailwind()
        assert 'font-bold' in classes
    
    def test_to_tailwind_size(self):
        """Convert size to Tailwind class."""
        style = ElementStyle(size=24)
        classes = style.to_tailwind()
        assert 'text-2xl' in classes
    
    def test_to_tailwind_opacity(self):
        """Convert opacity to Tailwind class."""
        style = ElementStyle(opacity=0.5)
        classes = style.to_tailwind()
        assert 'opacity-50' in classes
    
    def test_to_css_color(self):
        """Convert to CSS style string."""
        style = ElementStyle(color='#ff0000')
        css = style.to_css()
        assert 'color: #ff0000' in css
    
    def test_from_dict(self):
        """Create from dictionary."""
        style = ElementStyle.from_dict({
            'color': '#ff0000',
            'weight': 'bold',
            'size': 24,
        })
        assert style.color == '#ff0000'
        assert style.weight == 'bold'
        assert style.size == 24


class TestLayoutStyle:
    """Test LayoutStyle class."""
    
    def test_create_empty_layout(self):
        """Create empty layout style."""
        layout = LayoutStyle()
        assert layout.name == ''
        assert layout.background == ''
    
    def test_create_with_background(self):
        """Create layout with background."""
        layout = LayoutStyle(
            name='title',
            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        )
        assert layout.name == 'title'
        assert 'gradient' in layout.background
    
    def test_create_with_element_styles(self):
        """Create layout with element styles."""
        layout = LayoutStyle(
            name='content',
            title=ElementStyle(color='#111827', weight='bold'),
            subtitle=ElementStyle(color='#6b7280'),
            text=ElementStyle(color='#1f2937'),
        )
        assert layout.title.color == '#111827'
        assert layout.subtitle.color == '#6b7280'
        assert layout.text.color == '#1f2937'
    
    def test_background_style_gradient(self):
        """Generate background style for gradient."""
        layout = LayoutStyle(
            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        )
        style = layout.background_style()
        assert 'background:' in style
        assert 'gradient' in style
    
    def test_background_style_color(self):
        """Generate background style for solid color."""
        layout = LayoutStyle(background='#ffffff')
        style = layout.background_style()
        assert 'background-color:' in style or 'background:' in style
    
    def test_to_tailwind_element(self):
        """Get Tailwind classes for specific element."""
        layout = LayoutStyle(
            title=ElementStyle(color='#ffffff', weight='bold'),
            text=ElementStyle(color='#cccccc'),
        )
        
        title_classes = layout.to_tailwind('title')
        text_classes = layout.to_tailwind('text')
        
        assert 'text-[#ffffff]' in title_classes
        assert 'font-bold' in title_classes
        assert 'text-[#cccccc]' in text_classes
    
    def test_to_tailwind_unknown_element(self):
        """Return empty for unknown element."""
        layout = LayoutStyle()
        classes = layout.to_tailwind('unknown')
        assert classes == ''
    
    def test_from_dict(self):
        """Create from dictionary."""
        layout = LayoutStyle.from_dict('title', {
            'background': '#ffffff',
            'title': {'color': '#111827', 'weight': 'bold'},
            'text': {'color': '#1f2937'},
        })
        
        assert layout.name == 'title'
        assert layout.background == '#ffffff'
        assert layout.title.color == '#111827'
        assert layout.text.color == '#1f2937'
