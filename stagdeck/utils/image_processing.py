"""🖼️ Image processing utilities for StagDeck."""

import hashlib
import io
from pathlib import Path
from typing import Optional

from PIL import Image, ImageFilter


# Cache for processed images (in-memory)
_image_cache: dict[str, bytes] = {}


def get_cache_key(image_path: str, blur_radius: float) -> str:
    """Generate a cache key for a processed image."""
    return hashlib.md5(f"{image_path}:blur:{blur_radius}".encode()).hexdigest()


def apply_gaussian_blur(
    image_path: Path | str,
    blur_radius: float = 4.0,
) -> bytes:
    """Apply Gaussian blur to an image and return as bytes.
    
    :param image_path: Path to the source image.
    :param blur_radius: Blur radius (default 4.0).
    :return: Blurred image as PNG bytes.
    """
    path = Path(image_path)
    cache_key = get_cache_key(str(path), blur_radius)
    
    # Check cache
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    # Load and process image
    with Image.open(path) as img:
        # Convert to RGB if necessary (for PNG with alpha)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Apply Gaussian blur
        blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Save to bytes
        output = io.BytesIO()
        blurred.save(output, format='JPEG', quality=85)
        result = output.getvalue()
    
    # Cache result
    _image_cache[cache_key] = result
    
    return result


def clear_cache() -> None:
    """Clear the image processing cache."""
    _image_cache.clear()
