"""🎨 Theme loader with inheritance and security constraints."""

import json
from pathlib import Path
from typing import Any

from ..utils.paths import PathSecurityError, is_safe_filename


class ThemeLoadError(Exception):
    """Raised when theme loading fails."""
    pass


class ThemeLoader:
    """Secure theme loader with inheritance support.
    
    Supports:
    - Theme inheritance via "extends" key
    - Symbol paths for package-provided themes (e.g., "default:")
    - Security constraints on file paths
    
    :ivar search_paths: Mapping of symbol names to directories.
    """
    
    # Default symbol pointing to package templates
    PACKAGE_THEMES_DIR = Path(__file__).parent.parent / 'templates' / 'themes'
    
    def __init__(self) -> None:
        """Initialize loader with default search paths."""
        self._search_paths: dict[str, Path] = {
            'default': self.PACKAGE_THEMES_DIR,
        }
        self._max_inheritance_depth = 5
        self._loading_stack: list[str] = []  # Circular reference detection
    
    def add_search_path(self, symbol: str, path: str | Path) -> None:
        """Register a symbol for theme path resolution.
        
        :param symbol: Symbol name (e.g., 'custom', 'corporate').
        :param path: Directory path for this symbol.
        :raises ValueError: If symbol contains invalid characters.
        """
        if not symbol.isalnum() and symbol != '_':
            # Allow alphanumeric and underscore only
            if not all(c.isalnum() or c == '_' for c in symbol):
                raise ValueError(f"Invalid symbol name: '{symbol}'")
        
        resolved = Path(path).resolve()
        if not resolved.is_dir():
            raise ValueError(f"Search path must be a directory: '{path}'")
        
        self._search_paths[symbol] = resolved
    
    def remove_search_path(self, symbol: str) -> None:
        """Remove a registered symbol.
        
        :param symbol: Symbol to remove.
        """
        if symbol != 'default':  # Protect default symbol
            self._search_paths.pop(symbol, None)
    
    @property
    def search_paths(self) -> dict[str, Path]:
        """Get registered search paths (read-only copy)."""
        return dict(self._search_paths)
    
    def resolve_theme_path(
        self,
        reference: str,
        current_dir: Path | None = None,
    ) -> Path:
        """Resolve a theme reference to an absolute path.
        
        Supports:
        - Symbol references: "default:bright.json" or "corporate:main.json"
        - Same-folder references: "bright.json" (requires current_dir)
        
        :param reference: Theme reference string.
        :param current_dir: Current theme's directory (for relative refs).
        :return: Resolved absolute path.
        :raises ThemeLoadError: If reference is invalid or path not found.
        :raises PathSecurityError: If path violates security constraints.
        """
        # Check for symbol prefix (e.g., "default:bright.json")
        if ':' in reference:
            symbol, filename = reference.split(':', 1)
            
            if symbol not in self._search_paths:
                raise ThemeLoadError(
                    f"Unknown theme symbol '{symbol}'. "
                    f"Available: {list(self._search_paths.keys())}"
                )
            
            base_dir = self._search_paths[symbol]
        elif current_dir is not None:
            # Same-folder reference
            base_dir = current_dir
            filename = reference
        else:
            raise ThemeLoadError(
                f"Cannot resolve relative reference '{reference}' without current directory"
            )
        
        # Security: filename must be safe (no path components)
        if not is_safe_filename(filename):
            raise PathSecurityError(
                f"Invalid theme filename: '{filename}'. "
                "Must be a simple filename without path separators or shell characters."
            )
        
        # Security: must end with .json
        if not filename.endswith('.json'):
            raise PathSecurityError(
                f"Theme files must have .json extension: '{filename}'"
            )
        
        resolved = (base_dir / filename).resolve()
        
        # Security: verify resolved path is within base_dir
        try:
            resolved.relative_to(base_dir)
        except ValueError:
            raise PathSecurityError(
                f"Theme path escapes allowed directory: '{reference}'"
            )
        
        if not resolved.exists():
            raise ThemeLoadError(f"Theme file not found: '{resolved}'")
        
        return resolved
    
    def load_theme_data(
        self,
        reference: str,
        current_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Load theme data with inheritance resolution.
        
        :param reference: Theme reference (symbol:file or filename).
        :param current_dir: Current directory for relative references.
        :return: Merged theme data dictionary.
        :raises ThemeLoadError: If loading fails.
        :raises PathSecurityError: If path is invalid.
        """
        path = self.resolve_theme_path(reference, current_dir)
        return self._load_with_inheritance(path)
    
    def _load_with_inheritance(
        self,
        path: Path,
        depth: int = 0,
    ) -> dict[str, Any]:
        """Load theme with inheritance chain resolution.
        
        :param path: Absolute path to theme file.
        :param depth: Current inheritance depth.
        :return: Merged theme data.
        """
        path_str = str(path)
        
        # Check circular reference
        if path_str in self._loading_stack:
            chain = ' -> '.join(self._loading_stack + [path_str])
            raise ThemeLoadError(f"Circular theme inheritance detected: {chain}")
        
        # Check max depth
        if depth > self._max_inheritance_depth:
            raise ThemeLoadError(
                f"Theme inheritance depth exceeds maximum ({self._max_inheritance_depth})"
            )
        
        self._loading_stack.append(path_str)
        
        try:
            # Load this theme's data
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for parent theme
            extends = data.pop('extends', None)
            
            if extends:
                # Load parent theme (increment depth)
                parent_path = self.resolve_theme_path(extends, current_dir=path.parent)
                parent_data = self._load_with_inheritance(parent_path, depth=depth + 1)
                # Merge: child overrides parent
                data = self._deep_merge(parent_data, data)
            
            return data
            
        finally:
            self._loading_stack.pop()
    
    def _deep_merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        """Deep merge two dictionaries, override takes precedence.
        
        :param base: Base dictionary.
        :param override: Override dictionary.
        :return: Merged dictionary.
        """
        result = base.copy()
        
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result


# Global loader instance
_loader = ThemeLoader()


def get_theme_loader() -> ThemeLoader:
    """Get the global theme loader instance."""
    return _loader


def load_theme(reference: str, current_dir: Path | None = None) -> dict[str, Any]:
    """Convenience function to load theme data.
    
    :param reference: Theme reference (e.g., "default:bright.json").
    :param current_dir: Current directory for relative references.
    :return: Theme data dictionary.
    """
    return _loader.load_theme_data(reference, current_dir)
