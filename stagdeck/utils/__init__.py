"""🛠️ StagDeck utilities."""

from .paths import (
    PathSecurityError,
    resolve_safe_path,
    is_safe_filename,
    sanitize_filename,
    get_relative_path,
)

# PPTX loader - convert_pptx_to_images is the core function
# Prefer using SlideDeck.add_from_file() or insert_from_file() instead
from .pptx_loader import convert_pptx_to_images

__all__ = [
    'PathSecurityError',
    'resolve_safe_path',
    'is_safe_filename',
    'sanitize_filename',
    'get_relative_path',
    'convert_pptx_to_images',
]
