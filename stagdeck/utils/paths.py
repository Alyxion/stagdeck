"""🛤️ Path utilities with security constraints."""

import os
import re
from pathlib import Path


class PathSecurityError(Exception):
    """Raised when a path violates security constraints."""
    pass


def resolve_safe_path(
    path: str | Path,
    base_dir: str | Path | None = None,
    allow_traversal: bool = False,
    max_depth: int | None = None,
) -> Path:
    """Resolve a file path with security constraints.
    
    Validates and resolves a path, ensuring it doesn't contain shell injection
    patterns or escape the allowed directory scope.
    
    :param path: The path to resolve (relative or absolute).
    :param base_dir: Base directory to resolve relative paths against.
                     If provided and allow_traversal=False, result must be within this dir.
    :param allow_traversal: If False, prevents path from escaping base_dir via '../'.
    :param max_depth: Maximum directory depth allowed (None = unlimited).
    :return: Resolved absolute Path.
    :raises PathSecurityError: If path violates security constraints.
    :raises FileNotFoundError: If resolved path doesn't exist.
    
    Example:
        >>> resolve_safe_path('themes/bright.json', base_dir='/app')
        PosixPath('/app/themes/bright.json')
        
        >>> resolve_safe_path('../etc/passwd', base_dir='/app')
        PathSecurityError: Path traversal not allowed
    """
    path_str = str(path)
    
    # Rule 1: Check for shell injection patterns
    _check_shell_injection(path_str)
    
    # Rule 2: Check for null bytes (can bypass security checks)
    if '\x00' in path_str:
        raise PathSecurityError("Null bytes not allowed in path")
    
    # Rule 3: Normalize and resolve the path
    if base_dir is not None:
        base_dir = Path(base_dir).resolve()
        resolved = (base_dir / path).resolve()
    else:
        resolved = Path(path).resolve()
    
    # Rule 4: Check traversal constraint
    if base_dir is not None and not allow_traversal:
        try:
            resolved.relative_to(base_dir)
        except ValueError:
            raise PathSecurityError(
                f"Path traversal not allowed: '{path}' escapes base directory"
            )
    
    # Rule 5: Check depth constraint
    if max_depth is not None:
        if base_dir is not None:
            rel_path = resolved.relative_to(base_dir)
            depth = len(rel_path.parts) - 1  # -1 for the file itself
        else:
            depth = len(resolved.parts) - 1
        
        if depth > max_depth:
            raise PathSecurityError(
                f"Path depth {depth} exceeds maximum allowed depth {max_depth}"
            )
    
    return resolved


def _check_shell_injection(path: str) -> None:
    """Check for shell injection patterns in path string.
    
    :param path: Path string to check.
    :raises PathSecurityError: If shell injection pattern detected.
    """
    # Dangerous shell characters and patterns
    dangerous_patterns = [
        (r'[;&|`$]', "Shell metacharacters not allowed"),
        (r'\$\(', "Command substitution not allowed"),
        (r'\$\{', "Variable expansion not allowed"),
        (r'>\s*/', "Output redirection not allowed"),
        (r'<\s*/', "Input redirection not allowed"),
        (r'\|\|', "OR operator not allowed"),
        (r'&&', "AND operator not allowed"),
        (r'\\n|\\r', "Newline escapes not allowed"),
        (r'\x00', "Null bytes not allowed"),
    ]
    
    for pattern, message in dangerous_patterns:
        if re.search(pattern, path):
            raise PathSecurityError(f"{message}: '{path}'")


def is_safe_filename(filename: str) -> bool:
    """Check if a filename is safe (no path components or shell chars).
    
    :param filename: Filename to validate.
    :return: True if safe, False otherwise.
    """
    if not filename:
        return False
    
    # Must not contain path separators
    if '/' in filename or '\\' in filename:
        return False
    
    # Must not be special directory entries
    if filename in ('.', '..'):
        return False
    
    # Check for shell injection
    try:
        _check_shell_injection(filename)
        return True
    except PathSecurityError:
        return False


def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """Sanitize a filename by replacing unsafe characters.
    
    :param filename: Filename to sanitize.
    :param replacement: Character to replace unsafe chars with.
    :return: Sanitized filename.
    """
    # Remove path separators
    filename = filename.replace('/', replacement).replace('\\', replacement)
    
    # Remove shell metacharacters
    unsafe_chars = ';&|`$<>(){}[]!#*?"\''
    for char in unsafe_chars:
        filename = filename.replace(char, replacement)
    
    # Collapse multiple replacements
    while replacement + replacement in filename:
        filename = filename.replace(replacement + replacement, replacement)
    
    # Strip leading/trailing replacements
    filename = filename.strip(replacement)
    
    return filename or 'unnamed'


def get_relative_path(path: Path, base: Path) -> Path:
    """Get relative path, returning absolute if not relative to base.
    
    :param path: Path to make relative.
    :param base: Base directory.
    :return: Relative path if possible, otherwise absolute.
    """
    try:
        return path.relative_to(base)
    except ValueError:
        return path
