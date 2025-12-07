"""Tests for theme loading and inheritance."""

import pytest
from pathlib import Path

from stagdeck.theme import Theme, ThemeLoader, ThemeLoadError, get_theme_loader
from stagdeck.utils.paths import PathSecurityError


class TestThemeLoading:
    """Test theme file loading."""
    
    def test_load_aurora_theme(self):
        """Load aurora theme from default symbol."""
        theme = Theme.from_reference('default:aurora.json')
        assert theme.name == 'aurora'
        assert theme.version == '1.0'
    
    def test_load_midnight_theme(self):
        """Load midnight theme (extends aurora)."""
        theme = Theme.from_reference('default:midnight.json')
        assert theme.name == 'midnight'
        assert theme.version == '1.0'
    
    def test_theme_has_palette(self):
        """Theme should have palette variables."""
        theme = Theme.from_reference('default:aurora.json')
        assert 'primary' in theme.variables
        assert 'bg' in theme.variables
        assert 'text' in theme.variables
    
    def test_theme_has_constants(self):
        """Theme should have constants."""
        theme = Theme.from_reference('default:aurora.json')
        assert 'spacing_base' in theme.variables
        assert 'font_size_base' in theme.variables
        assert 'border_radius' in theme.variables


class TestThemeInheritance:
    """Test theme inheritance via extends."""
    
    def test_midnight_extends_aurora(self):
        """Midnight theme should inherit from aurora."""
        aurora = Theme.from_reference('default:aurora.json')
        midnight = Theme.from_reference('default:midnight.json')
        
        # Midnight should override bg colors
        assert midnight.variables['bg'] != aurora.variables['bg']
        assert midnight.variables['bg'] == '#0f172a'  # Dark background
        
        # Midnight should inherit constants from aurora
        assert midnight.variables['spacing_base'] == aurora.variables['spacing_base']
    
    def test_midnight_inherits_chart_colors(self):
        """Midnight should inherit chart colors from aurora."""
        aurora = Theme.from_reference('default:aurora.json')
        midnight = Theme.from_reference('default:midnight.json')
        
        # Chart colors should be inherited (not overridden in midnight)
        assert midnight.variables.get('chart_1') == aurora.variables.get('chart_1')
    
    def test_midnight_overrides_text_colors(self):
        """Midnight should override text colors for dark mode."""
        aurora = Theme.from_reference('default:aurora.json')
        midnight = Theme.from_reference('default:midnight.json')
        
        # Text colors should be different (light text on dark bg)
        assert midnight.variables['text'] != aurora.variables['text']
        assert midnight.variables['heading'] != aurora.variables['heading']


class TestThemeLoaderSecurity:
    """Test theme loader security constraints."""
    
    def test_reject_path_traversal(self):
        """Should reject path traversal attempts."""
        loader = get_theme_loader()
        
        with pytest.raises(PathSecurityError):
            loader.resolve_theme_path('../etc/passwd', current_dir=Path('/app'))
    
    def test_reject_absolute_path_in_filename(self):
        """Should reject absolute paths in filename."""
        loader = get_theme_loader()
        
        with pytest.raises(PathSecurityError):
            loader.resolve_theme_path('/etc/passwd', current_dir=Path('/app'))
    
    def test_reject_shell_characters(self):
        """Should reject shell metacharacters."""
        loader = get_theme_loader()
        
        with pytest.raises(PathSecurityError):
            loader.resolve_theme_path('theme;rm -rf /', current_dir=Path('/app'))
    
    def test_reject_non_json_extension(self):
        """Should reject files without .json extension."""
        loader = get_theme_loader()
        
        with pytest.raises(PathSecurityError):
            loader.resolve_theme_path('theme.txt', current_dir=Path('/app'))
    
    def test_reject_unknown_symbol(self):
        """Should reject unknown symbol references."""
        loader = get_theme_loader()
        
        with pytest.raises(ThemeLoadError):
            loader.resolve_theme_path('unknown:theme.json')
    
    def test_valid_symbol_reference(self):
        """Should accept valid symbol references."""
        loader = get_theme_loader()
        path = loader.resolve_theme_path('default:aurora.json')
        assert path.exists()
        assert path.name == 'aurora.json'


class TestCircularInheritance:
    """Test circular inheritance detection."""
    
    def test_detect_circular_inheritance(self, tmp_path: Path):
        """Should detect circular theme inheritance."""
        # Create two themes that reference each other
        theme_a = tmp_path / 'theme_a.json'
        theme_b = tmp_path / 'theme_b.json'
        
        theme_a.write_text('{"name": "a", "extends": "theme_b.json"}')
        theme_b.write_text('{"name": "b", "extends": "theme_a.json"}')
        
        loader = ThemeLoader()
        loader.add_search_path('test', tmp_path)
        
        with pytest.raises(ThemeLoadError, match='Circular'):
            loader.load_theme_data('test:theme_a.json')
    
    def test_max_inheritance_depth(self, tmp_path: Path):
        """Should enforce maximum inheritance depth."""
        # Create a chain of 8 themes (exceeds depth of 3)
        for i in range(8):
            theme_file = tmp_path / f'theme_{i}.json'
            if i < 7:
                theme_file.write_text(f'{{"name": "t{i}", "extends": "theme_{i+1}.json"}}')
            else:
                theme_file.write_text(f'{{"name": "t{i}"}}')
        
        loader = ThemeLoader()
        loader.add_search_path('test', tmp_path)
        loader._max_inheritance_depth = 3  # Set low limit
        
        with pytest.raises(ThemeLoadError, match='depth'):
            loader.load_theme_data('test:theme_0.json')
