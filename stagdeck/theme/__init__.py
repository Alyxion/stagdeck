"""🎨 StagDeck Theme System.

JSON-based styling with variables, computed values, and caching.
"""

from .theme import Theme, DEFAULT_THEME
from .styles import ElementStyle, LayoutStyle
from .evaluator import SafeExpressionEvaluator, ExpressionError
from .cache import ThemeCache, LRUCache
from .loader import ThemeLoader, ThemeLoadError, get_theme_loader, load_theme
from .context import ThemeContext, ThemeOverrides, overrides

__all__ = [
    'Theme',
    'DEFAULT_THEME',
    'ElementStyle',
    'LayoutStyle',
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
