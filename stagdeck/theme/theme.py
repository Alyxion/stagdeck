"""🎨 Theme - JSON-based styling system with variables and computed values."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .cache import ThemeCache
from .evaluator import SafeExpressionEvaluator, ExpressionError
from .loader import load_theme, get_theme_loader, ThemeLoader
from .styles import LayoutStyle, ElementStyle


@dataclass
class Theme:
    """🎨 Theme definition with variables, computed values, and layouts.
    
    Provides a JSON-based styling system with:
    - Reusable variables
    - Computed values with basic operators
    - Layout-specific styles
    - Cached value resolution
    
    :ivar name: Theme name.
    :ivar version: Theme version string.
    :ivar variables: Raw variable definitions.
    :ivar computed: Computed value expressions.
    :ivar layouts: Layout style definitions.
    """
    name: str = 'default'
    version: str = '1.0'
    variables: dict[str, Any] = field(default_factory=dict)
    computed: dict[str, str] = field(default_factory=dict)
    layouts: dict[str, LayoutStyle] = field(default_factory=dict)
    
    _cache: ThemeCache = field(default_factory=ThemeCache, repr=False)
    _resolving: set[str] = field(default_factory=set, repr=False)  # Circular reference detection
    
    @classmethod
    def from_json(cls, path: str | Path) -> 'Theme':
        """Load theme from JSON file (legacy method).
        
        For new code, prefer from_reference() which supports inheritance.
        
        :param path: Path to JSON theme file.
        :return: New Theme instance.
        :raises FileNotFoundError: If file doesn't exist.
        :raises json.JSONDecodeError: If JSON is invalid.
        """
        path = Path(path).resolve()
        data = load_theme(path.name, current_dir=path.parent)
        return cls.from_dict(data)
    
    @classmethod
    def from_reference(cls, reference: str) -> 'Theme':
        """Load theme from a reference string with inheritance support.
        
        Supports:
        - Symbol references: "default:bright.json", "default:dark.json"
        - Custom symbols registered via get_theme_loader().add_search_path()
        
        :param reference: Theme reference (e.g., "default:bright.json").
        :return: New Theme instance with inheritance resolved.
        
        Example:
            >>> theme = Theme.from_reference('default:dark.json')
            >>> # dark.json extends bright.json, values are merged
        """
        data = load_theme(reference)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Theme':
        """Create theme from dictionary.
        
        Supports both old format (variables/computed/layouts) and new format
        (constants/palette/component groups).
        
        :param data: Theme definition dictionary.
        :return: New Theme instance.
        """
        # Build variables from constants + palette (new format) or variables (old format)
        variables = {}
        variables.update(data.get('constants', {}))
        variables.update(data.get('palette', {}))
        variables.update(data.get('variables', {}))  # Old format fallback
        
        # Computed values (old format)
        computed = data.get('computed', {})
        
        # Parse layouts - check for 'layouts' key or 'slide' key (new format)
        layouts = {}
        if 'layouts' in data:
            for name, layout_data in data['layouts'].items():
                layouts[name] = LayoutStyle.from_dict(name, layout_data)
        
        # In new format, 'slide' defines the default layout
        if 'slide' in data:
            layouts['content'] = LayoutStyle.from_dict('content', data['slide'])
        
        return cls(
            name=data.get('name', 'default'),
            version=data.get('version', '1.0'),
            variables=variables,
            computed=computed,
            layouts=layouts,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Export theme to dictionary.
        
        :return: Theme as dictionary (for JSON serialization).
        """
        return {
            'name': self.name,
            'version': self.version,
            'variables': self.variables,
            'computed': self.computed,
            'layouts': {
                name: self._layout_to_dict(layout)
                for name, layout in self.layouts.items()
            },
        }
    
    def _layout_to_dict(self, layout: LayoutStyle) -> dict[str, Any]:
        """Convert LayoutStyle to dictionary."""
        result = {'background': layout.background}
        
        # Export all elements from the layout
        for name in ['title', 'subtitle', 'text', 'heading', 'link', 'bullet']:
            elem = layout.get(name)
            if elem and (elem.color or elem.size or elem.weight):
                result[name] = self._element_to_dict(elem)
        
        return result
    
    def _element_to_dict(self, element: ElementStyle) -> dict[str, Any]:
        """Convert ElementStyle to dictionary."""
        result = {}
        if element.color:
            result['color'] = element.color
        if element.size:
            result['size'] = element.size
        if element.weight:
            result['weight'] = element.weight
        if element.opacity != 1.0:
            result['opacity'] = element.opacity
        if element.font:
            result['font'] = element.font
        if element.classes:
            result['classes'] = element.classes
        if element.css:
            result['css'] = element.css
        return result
    
    # =========================================================================
    # Value Resolution
    # =========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a resolved value by key.
        
        Supports dot notation for nested access:
        - 'primary' -> variables['primary']
        - 'spacing_lg' -> computed['spacing_lg'] (resolved)
        - 'layouts.title.title.color' -> layouts['title'].title.color
        
        :param key: Key to look up (supports dot notation).
        :param default: Default value if not found.
        :return: Resolved value.
        """
        # Check cache first
        if self._cache.has_computed(key):
            return self._cache.get_computed(key)
        
        # Parse dot notation
        parts = key.split('.')
        
        # Try layouts path
        if parts[0] == 'layouts' and len(parts) >= 2:
            return self._get_layout_value(parts[1:], default)
        
        # Try computed
        if key in self.computed:
            value = self.resolve(self.computed[key])
            self._cache.set_computed(key, value)
            return value
        
        # Try variables
        if key in self.variables:
            return self.variables[key]
        
        return default
    
    def _get_layout_value(self, parts: list[str], default: Any) -> Any:
        """Get value from layout path.
        
        :param parts: Path parts after 'layouts'.
        :param default: Default value.
        :return: Resolved value.
        """
        if not parts:
            return default
        
        layout_name = parts[0]
        if layout_name not in self.layouts:
            return default
        
        layout = self.layouts[layout_name]
        
        if len(parts) == 1:
            return layout
        
        # Get element
        element_name = parts[1]
        element = layout.get_element(element_name)
        
        if len(parts) == 2:
            return element
        
        # Get element property
        prop = parts[2]
        return getattr(element, prop, default)
    
    def resolve(self, value: Any) -> Any:
        """Resolve a value with variable substitution and operators.
        
        :param value: Value to resolve (may contain ${var} references).
        :return: Resolved value.
        :raises ExpressionError: If resolution fails.
        """
        if not isinstance(value, str):
            return value
        
        # Check expression cache
        if self._cache.has_expr(value):
            return self._cache.get_expr(value)
        
        # Build variable context (variables + computed)
        context = dict(self.variables)
        
        # Resolve computed values that are referenced
        for name, expr in self.computed.items():
            if name not in context:
                context[name] = self._resolve_computed(name)
        
        # Evaluate expression
        evaluator = SafeExpressionEvaluator(context)
        result = evaluator.evaluate(value)
        
        # Cache result
        self._cache.set_expr(value, result)
        
        return result
    
    def _resolve_computed(self, name: str) -> Any:
        """Resolve a computed value by name.
        
        :param name: Computed value name.
        :return: Resolved value.
        :raises ExpressionError: If circular reference detected.
        """
        # Check cache
        if self._cache.has_computed(name):
            return self._cache.get_computed(name)
        
        # Circular reference detection
        if name in self._resolving:
            raise ExpressionError(f"Circular reference detected: {name}")
        
        if name not in self.computed:
            return self.variables.get(name)
        
        self._resolving.add(name)
        try:
            # Build context with variables and already-resolved computed
            context = dict(self.variables)
            for cname in self.computed:
                if cname != name and self._cache.has_computed(cname):
                    context[cname] = self._cache.get_computed(cname)
            
            evaluator = SafeExpressionEvaluator(context)
            
            # Recursively resolve dependencies
            expr = self.computed[name]
            result = evaluator.evaluate(expr)
            
            self._cache.set_computed(name, result)
            return result
        finally:
            self._resolving.discard(name)
    
    # =========================================================================
    # Layout Access
    # =========================================================================
    
    def get_layout(self, name: str) -> LayoutStyle | None:
        """Get a layout style by name.
        
        :param name: Layout name.
        :return: LayoutStyle or None if not found.
        """
        return self.layouts.get(name)
    
    def get_layout_resolved(self, name: str) -> LayoutStyle | None:
        """Get a layout with all values resolved.
        
        :param name: Layout name.
        :return: LayoutStyle with resolved values.
        """
        # Check cache
        cache_key = f'resolved_{name}'
        if self._cache.has_layout(cache_key):
            return self._cache.get_layout(cache_key)
        
        layout = self.layouts.get(name)
        if not layout:
            return None
        
        # Resolve all string values in layout elements
        resolved_elements: dict[str, ElementStyle] = {}
        for elem_name in ['title', 'subtitle', 'text', 'heading', 'link', 'bullet']:
            elem = layout.get(elem_name)
            if elem:
                resolved_elements[elem_name] = self._resolve_element(elem)
        
        resolved = LayoutStyle(
            name=layout.name,
            background=self._resolve_str(layout.background),
            elements=resolved_elements,
        )
        
        self._cache.set_layout(cache_key, resolved)
        return resolved
    
    def _resolve_str(self, value: str) -> str:
        """Resolve a string value."""
        if not value or '${' not in value:
            return value
        result = self.resolve(value)
        return str(result) if result is not None else ''
    
    def _resolve_element(self, element: ElementStyle) -> ElementStyle:
        """Resolve all values in an ElementStyle."""
        return ElementStyle(
            color=self._resolve_str(element.color),
            size=self.resolve(element.size) if isinstance(element.size, str) and '${' in element.size else element.size,
            weight=self._resolve_str(element.weight),
            opacity=element.opacity,
            font=self._resolve_str(element.font),
            classes=self._resolve_str(element.classes),
            css=self._resolve_str(element.css),
        )
    
    # =========================================================================
    # Variable Management
    # =========================================================================
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value.
        
        Clears computed cache since values may have changed.
        
        :param name: Variable name.
        :param value: Variable value.
        """
        self.variables[name] = value
        self._cache.clear_computed()
    
    def set_computed(self, name: str, expression: str) -> None:
        """Set a computed expression.
        
        :param name: Computed value name.
        :param expression: Expression string.
        """
        self.computed[name] = expression
        self._cache.clear_computed()
    
    # =========================================================================
    # Cache Management
    # =========================================================================
    
    def clear_cache(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    def cache_stats(self) -> dict[str, int]:
        """Get cache statistics.
        
        :return: Dictionary with cache counts.
        """
        return self._cache.stats()


