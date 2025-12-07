"""Tests for SlideDeck and Slide theme integration."""

import pytest

from stagdeck import SlideDeck, Slide
from stagdeck.theme import Theme, ThemeOverrides, overrides


class TestSlideDeckTheme:
    """Test SlideDeck theme management."""
    
    def test_use_theme_by_reference(self):
        """Set theme using reference string."""
        deck = SlideDeck(title='Test')
        deck.use_theme('default:aurora.json')
        
        assert deck.theme_context is not None
        assert deck.theme_context.primary_theme.name == 'aurora'
    
    def test_use_theme_instance(self):
        """Set theme using Theme instance."""
        theme = Theme.from_reference('default:aurora.json')
        deck = SlideDeck(title='Test')
        deck.use_theme(theme)
        
        assert deck.theme_context.primary_theme == theme
    
    def test_use_multiple_themes(self):
        """Set multiple themes."""
        deck = SlideDeck(title='Test')
        deck.use_themes('default:aurora.json', 'default:midnight.json')
        
        assert len(deck.theme_context.themes) == 2
    
    def test_deck_override(self):
        """Set deck-level override."""
        deck = SlideDeck(title='Test')
        deck.use_theme('default:aurora.json')
        deck.override('primary', '#ff0000')
        
        assert deck.get_theme_value('primary') == '#ff0000'
    
    def test_deck_override_palette(self):
        """Set multiple palette overrides."""
        deck = SlideDeck(title='Test')
        deck.use_theme('default:aurora.json')
        deck.override_palette(primary='#ff0000', accent='#00ff00')
        
        assert deck.get_theme_value('primary') == '#ff0000'
        assert deck.get_theme_value('accent') == '#00ff00'
    
    def test_chaining(self):
        """Test method chaining."""
        deck = (SlideDeck(title='Test')
                .use_theme('default:aurora.json')
                .override('primary', '#ff0000')
                .override_palette(accent='#00ff00'))
        
        assert deck.get_theme_value('primary') == '#ff0000'
        assert deck.get_theme_value('accent') == '#00ff00'
    
    def test_auto_create_theme_context(self):
        """Theme context should be auto-created on first override."""
        deck = SlideDeck(title='Test')
        deck.override('primary', '#ff0000')
        
        assert deck.theme_context is not None
    
    def test_get_theme_value_without_context(self):
        """get_theme_value should return default if no context."""
        deck = SlideDeck(title='Test')
        
        assert deck.get_theme_value('primary') is None
        assert deck.get_theme_value('primary', '#default') == '#default'


class TestSlideThemeOverrides:
    """Test Slide theme overrides."""
    
    def test_slide_override(self):
        """Set slide-level override."""
        slide = Slide(title='Test')
        slide.override('primary', '#ff0000')
        
        assert slide.theme_overrides is not None
        assert slide.theme_overrides.get('primary') == '#ff0000'
    
    def test_slide_override_palette(self):
        """Set multiple palette overrides on slide."""
        slide = Slide(title='Test')
        slide.override_palette(primary='#ff0000', accent='#00ff00')
        
        assert slide.theme_overrides.get('primary') == '#ff0000'
        assert slide.theme_overrides.get('accent') == '#00ff00'
    
    def test_slide_override_component(self):
        """Set component override on slide."""
        slide = Slide(title='Test')
        slide.override('pie_chart.colors', ['#f00', '#0f0', '#00f'])
        
        assert slide.theme_overrides.get('pie_chart.colors') == ['#f00', '#0f0', '#00f']
    
    def test_slide_chaining(self):
        """Test method chaining on slide."""
        slide = (Slide(title='Test')
                 .override('primary', '#ff0000')
                 .override('pie_chart.colors', ['#f00']))
        
        assert slide.theme_overrides.get('primary') == '#ff0000'
        assert slide.theme_overrides.get('pie_chart.colors') == ['#f00']


class TestDeckAddWithOverrides:
    """Test adding slides with theme overrides."""
    
    def test_add_slide_with_overrides(self):
        """Add slide with theme_overrides parameter."""
        deck = SlideDeck(title='Test')
        deck.add(
            title='Slide 1',
            theme_overrides=overrides(primary='#ff0000'),
        )
        
        slide = deck.slides[0]
        assert slide.theme_overrides.get('primary') == '#ff0000'
    
    def test_add_slide_with_component_overrides(self):
        """Add slide with component overrides."""
        deck = SlideDeck(title='Test')
        deck.add(
            title='Chart Slide',
            theme_overrides=overrides(**{
                'pie_chart.colors': ['#ff6384', '#36a2eb'],
                'pie_chart.stroke': '#ffffff',
            }),
        )
        
        slide = deck.slides[0]
        assert slide.theme_overrides.get('pie_chart.colors') == ['#ff6384', '#36a2eb']
        assert slide.theme_overrides.get('pie_chart.stroke') == '#ffffff'
    
    def test_modify_slide_after_add(self):
        """Modify slide overrides after adding to deck."""
        deck = SlideDeck(title='Test')
        deck.add(title='Slide 1')
        
        deck.slides[0].override('primary', '#ff0000')
        
        assert deck.slides[0].theme_overrides.get('primary') == '#ff0000'


class TestThemeResolutionOrder:
    """Test theme value resolution order."""
    
    def test_slide_overrides_deck(self):
        """Slide override should take precedence over deck."""
        deck = SlideDeck(title='Test')
        deck.use_theme('default:aurora.json')
        deck.override('primary', '#deck_color')
        
        deck.add(
            title='Slide 1',
            theme_overrides=overrides(primary='#slide_color'),
        )
        
        # Apply slide overrides to context
        slide = deck.slides[0]
        if slide.theme_overrides:
            deck.theme_context.push_slide_overrides(slide.theme_overrides)
        
        assert deck.theme_context.get('primary') == '#slide_color'
    
    def test_deck_overrides_theme(self):
        """Deck override should take precedence over theme."""
        deck = SlideDeck(title='Test')
        deck.use_theme('default:aurora.json')
        
        original = deck.get_theme_value('primary')
        deck.override('primary', '#custom')
        
        assert deck.get_theme_value('primary') == '#custom'
        assert deck.get_theme_value('primary') != original
