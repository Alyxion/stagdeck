"""💾 Caching layer for computed theme values."""

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable
import hashlib


class LRUCache:
    """🗄️ Least Recently Used cache with size limit.
    
    :ivar max_size: Maximum number of entries before eviction.
    """
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache.
        
        :param max_size: Maximum entries before LRU eviction.
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache, updating access order.
        
        :param key: Cache key.
        :param default: Default if not found.
        :return: Cached value or default.
        """
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        :param key: Cache key.
        :param value: Value to cache.
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        
        # Evict oldest if over limit
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    
    def has(self, key: str) -> bool:
        """Check if key exists in cache.
        
        :param key: Cache key.
        :return: True if key exists.
        """
        return key in self._cache
    
    def delete(self, key: str) -> bool:
        """Remove key from cache.
        
        :param key: Cache key.
        :return: True if key was removed.
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key in cache."""
        return key in self._cache


@dataclass
class ThemeCache:
    """🎨 Specialized cache for theme values.
    
    Organizes cached values by category for efficient invalidation.
    
    Categories:
    - var: Raw variable values
    - computed: Computed/resolved values
    - layout: Layout style objects
    - expr: Expression evaluation results
    """
    
    max_expr_cache: int = 1000
    _variables: dict[str, Any] = field(default_factory=dict)
    _computed: dict[str, Any] = field(default_factory=dict)
    _layouts: dict[str, Any] = field(default_factory=dict)
    _expressions: LRUCache = field(default_factory=lambda: LRUCache(1000))
    
    def __post_init__(self):
        """Initialize expression cache with correct size."""
        self._expressions = LRUCache(self.max_expr_cache)
    
    # Variable cache
    
    def get_var(self, name: str, default: Any = None) -> Any:
        """Get cached variable value."""
        return self._variables.get(name, default)
    
    def set_var(self, name: str, value: Any) -> None:
        """Cache variable value."""
        self._variables[name] = value
    
    def has_var(self, name: str) -> bool:
        """Check if variable is cached."""
        return name in self._variables
    
    # Computed cache
    
    def get_computed(self, name: str, default: Any = None) -> Any:
        """Get cached computed value."""
        return self._computed.get(name, default)
    
    def set_computed(self, name: str, value: Any) -> None:
        """Cache computed value."""
        self._computed[name] = value
    
    def has_computed(self, name: str) -> bool:
        """Check if computed value is cached."""
        return name in self._computed
    
    # Layout cache
    
    def get_layout(self, name: str, element: str | None = None, default: Any = None) -> Any:
        """Get cached layout or element style."""
        key = f"{name}.{element}" if element else name
        return self._layouts.get(key, default)
    
    def set_layout(self, name: str, value: Any, element: str | None = None) -> None:
        """Cache layout or element style."""
        key = f"{name}.{element}" if element else name
        self._layouts[key] = value
    
    def has_layout(self, name: str, element: str | None = None) -> bool:
        """Check if layout is cached."""
        key = f"{name}.{element}" if element else name
        return key in self._layouts
    
    # Expression cache
    
    @staticmethod
    def _expr_key(expression: str) -> str:
        """Generate cache key for expression."""
        return hashlib.md5(expression.encode()).hexdigest()[:16]
    
    def get_expr(self, expression: str, default: Any = None) -> Any:
        """Get cached expression result."""
        return self._expressions.get(self._expr_key(expression), default)
    
    def set_expr(self, expression: str, value: Any) -> None:
        """Cache expression result."""
        self._expressions.set(self._expr_key(expression), value)
    
    def has_expr(self, expression: str) -> bool:
        """Check if expression result is cached."""
        return self._expressions.has(self._expr_key(expression))
    
    # Bulk operations
    
    def clear(self) -> None:
        """Clear all caches."""
        self._variables.clear()
        self._computed.clear()
        self._layouts.clear()
        self._expressions.clear()
    
    def clear_computed(self) -> None:
        """Clear computed and expression caches (after variable change)."""
        self._computed.clear()
        self._expressions.clear()
    
    def clear_layouts(self) -> None:
        """Clear layout cache."""
        self._layouts.clear()
    
    def stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            'variables': len(self._variables),
            'computed': len(self._computed),
            'layouts': len(self._layouts),
            'expressions': len(self._expressions),
        }
