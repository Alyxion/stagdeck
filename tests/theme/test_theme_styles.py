"""Tests for ElementStyle and SlideStyle."""

import pytest

from stagdeck.theme import ElementStyle, SlideStyle


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
    
    def test_to_css_includes_color(self):
        """CSS output includes color."""
        style = ElementStyle(color='#ff0000')
        css = style.to_css()
        assert 'color: #ff0000' in css
    
    def test_to_css_includes_weight(self):
        """CSS output includes font-weight."""
        style = ElementStyle(weight='bold')
        css = style.to_css()
        assert 'font-weight: bold' in css
    
    def test_to_css_includes_size_px(self):
        """CSS output includes font-size in px."""
        style = ElementStyle(size=24)
        css = style.to_css()
        assert 'font-size: 24px' in css
    
    def test_to_css_includes_size_string(self):
        """CSS output includes font-size as string."""
        style = ElementStyle(size='2rem')
        css = style.to_css()
        assert 'font-size: 2rem' in css
    
    def test_to_tailwind_opacity(self):
        """Convert opacity to Tailwind class."""
        style = ElementStyle(opacity=0.5)
        classes = style.to_tailwind()
        assert 'opacity-50' in classes
    
    def test_to_tailwind_with_classes(self):
        """Tailwind output includes user classes."""
        style = ElementStyle(classes='text-center mt-4')
        classes = style.to_tailwind()
        assert 'text-center' in classes
        assert 'mt-4' in classes
    
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
    
    def test_merge_other_takes_precedence(self):
        """Merge styles with other taking precedence."""
        base = ElementStyle(color='#ff0000', weight='normal')
        override = ElementStyle(color='#00ff00')
        merged = base.merge(override)
        assert merged.color == '#00ff00'
        assert merged.weight == 'normal'


class TestSlideStyle:
    """Test SlideStyle class."""
    
    def test_create_empty_style(self):
        """Create empty slide style."""
        style = SlideStyle()
        assert style.name == ''
        assert style.background == ''
    
    def test_create_with_background(self):
        """Create style with background."""
        style = SlideStyle(
            name='title',
            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        )
        assert style.name == 'title'
        assert 'gradient' in style.background
    
    def test_create_with_element_styles(self):
        """Create style with element styles via kwargs."""
        style = SlideStyle(
            name='content',
            title=ElementStyle(color='#111827', weight='bold'),
            subtitle=ElementStyle(color='#6b7280'),
            text=ElementStyle(color='#1f2937'),
        )
        assert style.get('title').color == '#111827'
        assert style.get('subtitle').color == '#6b7280'
        assert style.get('text').color == '#1f2937'
    
    def test_background_style_gradient(self):
        """Generate background style for gradient."""
        style = SlideStyle(
            background='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        )
        css = style.background_style()
        assert 'background:' in css
        assert 'gradient' in css
    
    def test_background_style_color(self):
        """Generate background style for solid color."""
        style = SlideStyle(background='#ffffff')
        css = style.background_style()
        assert 'background-color:' in css or 'background:' in css
    
    def test_get_element_style(self):
        """Get ElementStyle by name."""
        style = SlideStyle(
            title=ElementStyle(color='#ffffff', weight='bold'),
            text=ElementStyle(color='#cccccc'),
        )
        
        title_style = style.get('title')
        text_style = style.get('text')
        
        assert title_style.color == '#ffffff'
        assert title_style.weight == 'bold'
        assert text_style.color == '#cccccc'
    
    def test_get_unknown_element_returns_empty(self):
        """Get unknown element returns empty ElementStyle."""
        style = SlideStyle()
        unknown = style.get('unknown')
        assert unknown.color == ''
    
    def test_set_element_style(self):
        """Set ElementStyle by name."""
        style = SlideStyle()
        style.set('custom', ElementStyle(color='#ff0000'))
        assert style.get('custom').color == '#ff0000'
    
    def test_to_css_element(self):
        """Get CSS for specific element."""
        style = SlideStyle(
            title=ElementStyle(color='#ffffff', size=80),
        )
        css = style.to_css('title')
        assert 'color: #ffffff' in css
        assert 'font-size: 80px' in css
    
    def test_merge_styles(self):
        """Merge two SlideStyles."""
        base = SlideStyle(
            name='base',
            background='#000000',
            title=ElementStyle(color='#ff0000', size=80),
        )
        override = SlideStyle(
            name='override',
            title=ElementStyle(color='#00ff00'),
        )
        merged = base.merge(override)
        
        assert merged.name == 'override'
        assert merged.background == '#000000'  # From base
        assert merged.get('title').color == '#00ff00'  # Overridden
        assert merged.get('title').size == 80  # From base
