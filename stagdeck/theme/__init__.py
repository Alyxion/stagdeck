"""🎨 StagDeck Theme System.

JSON-based styling with variables, computed values, and caching.
"""

from .theme import Theme
from .styles import ElementStyle, SlideStyle, LayoutStyle, get_default_style
from .evaluator import SafeExpressionEvaluator, ExpressionError
from .cache import ThemeCache, LRUCache
from .loader import ThemeLoader, ThemeLoadError, get_theme_loader, load_theme
from .context import ThemeContext, ThemeOverrides, overrides

__all__ = [
    'Theme',
    'ElementStyle',
    'SlideStyle',
    'LayoutStyle',  # Backwards compatibility alias for SlideStyle
    'get_default_style',
    'SafeExpressionEvaluator',
    'ExpressionError',
    'ThemeCache',
    'LRUCache',
    'ThemeLoader',
    'ThemeLoadError',
    'get_theme_loader',
    'load_theme',
    'ThemeContext',
    'ThemeOverrides',
    'overrides',
]
