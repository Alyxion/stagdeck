"""📊 PowerPoint (PPTX) loader for StagDeck.

Converts PPTX slides to images using LibreOffice for full fidelity rendering.
Requires LibreOffice to be installed.
"""

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stagdeck import SlideDeck

def _compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]  # First 16 chars is enough


def _get_cache_dir(pptx_path: Path) -> Path:
    """Get cache directory for a PPTX file (next to the PPTX).
    
    Uses .pptx_cache suffix so it can be globally gitignored with *.pptx_cache
    """
    return pptx_path.parent / f"{pptx_path.stem}.pptx_cache"


def _is_cache_valid(cache_dir: Path, pptx_path: Path) -> bool:
    """Check if cached images are valid for the given PPTX."""
    meta_file = cache_dir / '.meta.json'
    if not meta_file.exists():
        return False
    
    try:
        meta = json.loads(meta_file.read_text())
        cached_hash = meta.get('hash')
        current_hash = _compute_file_hash(pptx_path)
        return cached_hash == current_hash
    except (json.JSONDecodeError, OSError):
        return False


def _write_cache_meta(cache_dir: Path, pptx_path: Path) -> None:
    """Write cache metadata."""
    meta = {
        'hash': _compute_file_hash(pptx_path),
        'source': pptx_path.name,
    }
    (cache_dir / '.meta.json').write_text(json.dumps(meta, indent=2))


def _find_libreoffice() -> str | None:
    """Find LibreOffice executable."""
    # Try common command names
    for cmd in ['soffice', 'libreoffice']:
        path = shutil.which(cmd)
        if path:
            return path
    
    # Try common macOS paths
    mac_paths = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '/Applications/LibreOffice.app/Contents/MacOS/libreoffice',
    ]
    for path in mac_paths:
        if Path(path).exists():
            return path
    
    return None


def convert_pptx_to_images(
    pptx_path: Path | str,
    force: bool = False,
) -> tuple[Path, list[Path]]:
    """Convert PPTX slides to PNG images using LibreOffice.
    
    Results are cached in {pptx_dir}/{pptx_stem}_slides/ for git tracking.
    Images are only regenerated when the PPTX file content changes.
    LibreOffice is only required when cache is missing or invalid.
    
    :param pptx_path: Path to the PPTX file.
    :param force: Force re-conversion even if cached images exist.
    :return: Tuple of (cache_dir, list of image paths).
    :raises FileNotFoundError: If PPTX file doesn't exist.
    :raises RuntimeError: If LibreOffice is not available and cache is invalid.
    """
    pptx_path = Path(pptx_path).resolve()
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX file not found: {pptx_path}")
    
    # Get cache directory (next to PPTX file)
    cache_dir = _get_cache_dir(pptx_path)
    
    # Check for valid cached images - LibreOffice not needed if cache is valid
    if not force and cache_dir.exists():
        existing_images = sorted(cache_dir.glob('slide_*.png'))
        if existing_images and _is_cache_valid(cache_dir, pptx_path):
            return cache_dir, existing_images
    
    # Need to regenerate - check for LibreOffice
    soffice = _find_libreoffice()
    if not soffice:
        # Check if we have any cached images at all (even if outdated)
        if cache_dir.exists():
            existing_images = sorted(cache_dir.glob('slide_*.png'))
            if existing_images:
                import warnings
                warnings.warn(
                    f"LibreOffice not found. Using existing cached slides for {pptx_path.name}. "
                    "Install LibreOffice to regenerate: brew install --cask libreoffice"
                )
                return cache_dir, existing_images
        
        raise RuntimeError(
            "LibreOffice not found and no cached slides exist.\n"
            "Install LibreOffice to convert PPTX to images:\n"
            "  macOS: brew install --cask libreoffice\n"
            "  Linux: apt install libreoffice\n"
            "  Windows: Download from https://www.libreoffice.org/"
        )
    
    # Clear old cache and regenerate
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # LibreOffice exports to a temp directory, then we move files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Convert to PDF first (most reliable for multi-slide)
        result = subprocess.run([
            soffice,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', tmpdir,
            str(pptx_path),
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        pdf_file = tmp_path / f"{pptx_path.stem}.pdf"
        if not pdf_file.exists():
            raise RuntimeError("LibreOffice did not produce a PDF file")
        
        # Convert PDF pages to images
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(str(pdf_file), dpi=150)
            
            image_paths = []
            for i, image in enumerate(images, 1):
                img_path = cache_dir / f"slide_{i:03d}.png"
                image.save(str(img_path), 'PNG')
                image_paths.append(img_path)
            
            # Write cache metadata
            _write_cache_meta(cache_dir, pptx_path)
            
            return cache_dir, image_paths
            
        except ImportError:
            raise RuntimeError(
                "pdf2image is required for PPTX conversion.\n"
                "Install with: pip install pdf2image\n"
                "Also requires poppler:\n"
                "  macOS: brew install poppler\n"
                "  Linux: apt install poppler-utils"
            )
