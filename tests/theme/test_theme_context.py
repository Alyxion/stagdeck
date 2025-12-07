"""Tests for ThemeContext and cascading overrides."""

import pytest

from stagdeck.theme import (
    Theme, 
    ThemeContext, 
    ThemeOverrides, 
    overrides,
)


class TestThemeOverrides:
    """Test ThemeOverrides class."""
    
    def test_create_empty_overrides(self):
        """Create empty overrides."""
        ovr = ThemeOverrides()
        assert ovr.is_empty()
        assert ovr.palette == {}
        assert ovr.components == {}
    
    def test_set_palette_override(self):
        """Set palette-level override."""
        ovr = ThemeOverrides()
        ovr.set('primary', '#ff0000')
        
        assert not ovr.is_empty()
        assert ovr.palette['primary'] == '#ff0000'
    
    def test_set_component_override(self):
        """Set component-level override with dot notation."""
        ovr = ThemeOverrides()
        ovr.set('pie_chart.colors', ['#f00', '#0f0', '#00f'])
        
        assert not ovr.is_empty()
        assert ovr.components['pie_chart.colors'] == ['#f00', '#0f0', '#00f']
    
    def test_set_nested_component_override(self):
        """Set deeply nested component override."""
        ovr = ThemeOverrides()
        ovr.set('bar_chart.axis.color', '#333333')
        
        assert ovr.components['bar_chart.axis.color'] == '#333333'
    
    def test_get_palette_override(self):
        """Get palette override."""
        ovr = ThemeOverrides()
        ovr.set('primary', '#ff0000')
        
        assert ovr.get('primary') == '#ff0000'
        assert ovr.get('nonexistent') is None
    
    def test_get_component_override(self):
        """Get component override."""
        ovr = ThemeOverrides()
        ovr.set('pie_chart.colors', ['#f00'])
        
        assert ovr.get('pie_chart.colors') == ['#f00']
    
    def test_merge_overrides(self):
        """Merge two override sets."""
        base = ThemeOverrides()
        base.set('primary', '#ff0000')
        base.set('pie_chart.colors', ['#f00'])
        
        override = ThemeOverrides()
        override.set('primary', '#00ff00')  # Override
        override.set('accent', '#0000ff')   # New
        
        merged = base.merge(override)
        
        assert merged.get('primary') == '#00ff00'  # Overridden
        assert merged.get('accent') == '#0000ff'   # New
        assert merged.get('pie_chart.colors') == ['#f00']  # Inherited
    
    def test_chaining(self):
        """Test method chaining."""
        ovr = (ThemeOverrides()
               .set('primary', '#ff0000')
               .set('accent', '#00ff00')
               .set('pie_chart.colors', ['#f00']))
        
        assert ovr.get('primary') == '#ff0000'
        assert ovr.get('accent') == '#00ff00'
        assert ovr.get('pie_chart.colors') == ['#f00']
    
    def test_clear(self):
        """Test clearing overrides."""
        ovr = ThemeOverrides()
        ovr.set('primary', '#ff0000')
        ovr.set('pie_chart.colors', ['#f00'])
        
        ovr.clear()
        
        assert ovr.is_empty()


class TestOverridesHelper:
    """Test the overrides() helper function."""
    
    def test_create_overrides_from_kwargs(self):
        """Create overrides from keyword arguments."""
        ovr = overrides(primary='#ff0000', accent='#00ff00')
        
        assert ovr.get('primary') == '#ff0000'
        assert ovr.get('accent') == '#00ff00'
    
    def test_create_component_overrides(self):
        """Create component overrides using dict unpacking."""
        ovr = overrides(**{
            'pie_chart.colors': ['#f00', '#0f0'],
            'bar_chart.axis.color': '#333',
        })
        
        assert ovr.get('pie_chart.colors') == ['#f00', '#0f0']
        assert ovr.get('bar_chart.axis.color') == '#333'


class TestThemeContext:
    """Test ThemeContext cascading resolution."""
    
    def test_create_from_single_theme(self):
        """Create context from single theme."""
        theme = Theme.from_reference('default:aurora.json')
        ctx = ThemeContext.from_theme(theme)
        
        assert ctx.primary_theme == theme
        assert len(ctx.themes) == 1
    
    def test_create_from_theme_reference(self):
        """Create context from theme reference string."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        
        assert ctx.primary_theme is not None
        assert ctx.primary_theme.name == 'aurora'
    
    def test_create_from_multiple_themes(self):
        """Create context from multiple themes."""
        ctx = ThemeContext.from_themes(
            'default:aurora.json',
            'default:midnight.json',
        )
        
        assert len(ctx.themes) == 2
        assert ctx.primary_theme.name == 'aurora'
    
    def test_get_palette_value(self):
        """Get palette value from theme."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        
        primary = ctx.get('primary')
        assert primary == '#667eea'
    
    def test_deck_override_takes_precedence(self):
        """Deck override should take precedence over theme."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')
        
        assert ctx.get('primary') == '#ff0000'
    
    def test_slide_override_takes_precedence(self):
        """Slide override should take precedence over deck override."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')  # Deck level
        ctx.push_slide_override('primary', '#00ff00')  # Slide level
        
        assert ctx.get('primary') == '#00ff00'
    
    def test_clear_slide_overrides(self):
        """Clearing slide overrides should fall back to deck."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')
        ctx.push_slide_override('primary', '#00ff00')
        
        ctx.clear_slide_overrides()
        
        assert ctx.get('primary') == '#ff0000'
    
    def test_override_palette_method(self):
        """Test override_palette convenience method."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override_palette(primary='#ff0000', accent='#00ff00')
        
        assert ctx.get('primary') == '#ff0000'
        assert ctx.get('accent') == '#00ff00'
    
    def test_fallback_to_second_theme(self):
        """Should fall back to second theme if first doesn't have value."""
        # Create a minimal theme without chart colors
        ctx = ThemeContext.from_themes(
            'default:midnight.json',  # Has overridden palette
            'default:aurora.json',    # Has full palette
        )
        
        # Both should have primary (midnight overrides it)
        assert ctx.get('primary') is not None
    
    def test_get_merged_palette(self):
        """Get complete merged palette."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')
        
        palette = ctx.get_palette()
        
        assert palette['primary'] == '#ff0000'  # Overridden
        assert 'bg' in palette  # From theme
        assert 'text' in palette  # From theme
    
    def test_add_theme_as_fallback(self):
        """Add theme as fallback."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.add_theme('default:midnight.json')
        
        assert len(ctx.themes) == 2
    
    def test_resolve_variables_in_text(self):
        """Resolve ${variable} references in text."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')
        
        result = ctx.resolve_variables('Color is ${primary}')
        
        assert result == 'Color is #ff0000'


class TestThemeContextCaching:
    """Test ThemeContext caching behavior."""
    
    def test_cache_cleared_on_override(self):
        """Cache should be cleared when override is set."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        
        # First access - populates cache
        _ = ctx.get('primary')
        
        # Override - should clear cache
        ctx.override('primary', '#ff0000')
        
        # Should get new value
        assert ctx.get('primary') == '#ff0000'
    
    def test_cache_cleared_on_slide_override(self):
        """Cache should be cleared when slide override is set."""
        ctx = ThemeContext.from_theme('default:aurora.json')
        ctx.override('primary', '#ff0000')
        
        _ = ctx.get('primary')
        
        ctx.push_slide_override('primary', '#00ff00')
        
        assert ctx.get('primary') == '#00ff00'
