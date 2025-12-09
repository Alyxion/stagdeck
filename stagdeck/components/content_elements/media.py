"""Media view classes for displaying images and other media."""

import re
from dataclasses import dataclass, field
from typing import Any

from nicegui import ui

from .base import ContentElement


@dataclass
class MediaStyle:
    """Style configuration for media elements.
    
    All properties can be set via modifier string parsing or directly.
    Use None to indicate "not set", -1 for "use theme default".
    """
    blur: float | None = None  # Blur radius in pixels, None = no blur, -1 = theme default
    overlay: float | None = None  # Overlay opacity 0-1, None = no overlay, -1 = theme default
    position: str = ''  # 'left', 'right', 'top', 'bottom', '' for center
    border_radius: str = '0'  # CSS border-radius
    object_fit: str = 'cover'  # CSS object-fit: cover, contain, fill, etc.
    extra: dict[str, Any] = field(default_factory=dict)  # Future/custom properties
    
    @classmethod
    def from_modifiers(cls, modifiers: str) -> 'MediaStyle':
        """Parse modifier string into MediaStyle.
        
        Supported modifiers:
        - blur, blur:N - Gaussian blur (N = radius in pixels)
        - overlay, overlay:N - Dark overlay (N = opacity 0-1)
        - left, right, top, bottom - Position hints
        - Any future key:value pairs
        
        :param modifiers: Space-separated modifier string (e.g., "blur:8 overlay:0.5 left").
        :return: Parsed MediaStyle instance.
        """
        style = cls()
        
        if not modifiers:
            return style
        
        mod_list = modifiers.lower().split()
        
        for mod in mod_list:
            # Position modifiers
            if mod in ('left', 'right', 'top', 'bottom', 'center'):
                style.position = mod if mod != 'center' else ''
            
            # Blur modifier
            elif mod == 'blur':
                style.blur = -1.0  # Use theme default
            elif mod.startswith('blur:'):
                try:
                    style.blur = float(mod.split(':')[1])
                except (ValueError, IndexError):
                    style.blur = -1.0
            
            # Overlay modifier
            elif mod == 'overlay':
                style.overlay = -1.0  # Use theme default
            elif mod.startswith('overlay:'):
                try:
                    style.overlay = float(mod.split(':')[1])
                except (ValueError, IndexError):
                    style.overlay = -1.0
            
            # Border radius
            elif mod.startswith('radius:'):
                style.border_radius = mod.split(':')[1]
            
            # Object fit
            elif mod.startswith('fit:'):
                style.object_fit = mod.split(':')[1]
            
            # Inline modifier (skip, handled by mode)
            elif mod == 'inline':
                pass
            
            # Background modifier (skip, handled by mode)
            elif mod == 'background':
                pass
            
            # Future/unknown modifiers with values go to extra
            elif ':' in mod:
                key, _, value = mod.partition(':')
                # Try to parse as number
                try:
                    style.extra[key] = float(value)
                except ValueError:
                    style.extra[key] = value
            
            # Future/unknown flag modifiers
            else:
                style.extra[mod] = True
        
        return style


class MediaView(ContentElement):
    """Base class for media content elements.
    
    Handles common media properties like blur, overlay, positioning.
    Parses modifier strings for extensibility.
    """
    
    def __init__(
        self,
        src: str,
        modifiers: str = '',
        *,
        mode: str = 'background',
        **kwargs: Any,
    ):
        """Initialize media view.
        
        :param src: Media source URL or path.
        :param modifiers: Space-separated modifier string (e.g., "blur:8 overlay:0.5 left").
        :param mode: Display mode - 'background', 'inline', or 'region'.
        :param kwargs: Direct style overrides (blur, overlay, position, etc.).
        """
        super().__init__(content=src, font_size=1.0)
        self.src = src
        self.mode = mode
        
        # Parse modifiers string
        self.style = MediaStyle.from_modifiers(modifiers)
        
        # Apply direct kwargs overrides
        if 'blur' in kwargs:
            self.style.blur = kwargs['blur']
        if 'overlay' in kwargs:
            self.style.overlay = kwargs['overlay']
        if 'position' in kwargs:
            self.style.position = kwargs['position']
        if 'border_radius' in kwargs:
            self.style.border_radius = kwargs['border_radius']
        if 'object_fit' in kwargs:
            self.style.object_fit = kwargs['object_fit']
        
        # Store remaining kwargs in extra
        for key, value in kwargs.items():
            if key not in ('blur', 'overlay', 'position', 'border_radius', 'object_fit'):
                self.style.extra[key] = value
    
    @property
    def has_blur(self) -> bool:
        """Check if blur effect is requested."""
        return self.style.blur is not None
    
    @property
    def has_overlay(self) -> bool:
        """Check if overlay effect is requested."""
        return self.style.overlay is not None
    
    def get_blur_radius(self, theme_default: float = 4.0) -> float:
        """Get effective blur radius.
        
        :param theme_default: Default blur radius from theme.
        :return: Blur radius in pixels.
        """
        if self.style.blur is None:
            return 0
        if self.style.blur < 0:
            return theme_default
        return self.style.blur
    
    def get_overlay_opacity(self, theme_default: float = 0.5) -> float:
        """Get effective overlay opacity.
        
        :param theme_default: Default overlay opacity from theme.
        :return: Overlay opacity 0-1.
        """
        if self.style.overlay is None:
            return 0
        if self.style.overlay < 0:
            return theme_default
        return self.style.overlay
    
    def get_background_position(self) -> str:
        """Get CSS background-position based on position hint."""
        pos = self.style.position
        if pos == 'left':
            return 'left center'
        elif pos == 'right':
            return 'right center'
        elif pos == 'top':
            return 'center top'
        elif pos == 'bottom':
            return 'center bottom'
        return 'center'
    
    async def build(self) -> None:
        """Build the media element UI. Override in subclasses."""
        pass


class ImageView(MediaView):
    """Image content element for all image display scenarios.
    
    Supports:
    - Background images (full slide)
    - Split layouts (left, right, top, bottom)
    - Inline images within content
    - Blur and overlay effects
    - Seamless panorama positioning
    
    Example usage:
        # From modifier string (preferred)
        ImageView('/media/photo.jpg', 'blur:8 overlay:0.5 left')
        
        # With direct overrides
        ImageView('/media/photo.jpg', 'left', blur=10)
        
        # Inline mode
        ImageView('/media/photo.jpg', 'inline radius:8px')
    """
    
    def __init__(
        self,
        src: str,
        modifiers: str = '',
        *,
        width: str = '100%',
        height: str = '100%',
        **kwargs: Any,
    ):
        """Initialize image view.
        
        :param src: Image source URL or path.
        :param modifiers: Space-separated modifier string (e.g., "blur:8 overlay:0.5 left").
        :param width: CSS width for the image container.
        :param height: CSS height for the image container.
        :param kwargs: Direct style overrides (blur, overlay, position, etc.).
        """
        # Determine mode from modifiers
        mode = 'background'
        if 'inline' in modifiers.lower():
            mode = 'inline'
        elif any(pos in modifiers.lower() for pos in ('left', 'right', 'top', 'bottom')):
            mode = 'region'
        
        super().__init__(
            src=src,
            modifiers=modifiers,
            mode=mode,
            **kwargs,
        )
        self.mode = mode
        self.width = width
        self.height = height
        
        # Apply additional style properties from kwargs
        if 'border_radius' in kwargs:
            self.style.border_radius = kwargs['border_radius']
        if 'object_fit' in kwargs:
            self.style.object_fit = kwargs['object_fit']
    
    def get_image_url(self, blur_endpoint: str = '/stagdeck/blur') -> str:
        """Get the image URL, applying blur endpoint if needed.
        
        :param blur_endpoint: URL endpoint for server-side blur.
        :return: Image URL (possibly with blur processing).
        """
        if not self.has_blur:
            return self.src
        
        # Extract path from url(...) if present
        src = self.src
        if src.startswith('url(') and src.endswith(')'):
            src = src[4:-1].strip('"\'')
        
        radius = self.get_blur_radius()
        return f'{blur_endpoint}?path={src}&radius={radius}'
    
    def get_background_css(
        self,
        blur_endpoint: str = '/stagdeck/blur',
        theme_blur_default: float = 4.0,
        region_index: int = 0,
        region_count: int = 1,
        region_direction: str = 'horizontal',
    ) -> str:
        """Get CSS for background image display.
        
        :param blur_endpoint: URL endpoint for server-side blur.
        :param theme_blur_default: Default blur radius from theme.
        :param region_index: Index of this region (0-based) for seamless tiling.
        :param region_count: Total number of regions sharing this image.
        :param region_direction: 'horizontal' or 'vertical' for seamless tiling.
        :return: CSS background property value.
        """
        # Handle colors and gradients
        if self.src.startswith('#') or 'gradient' in self.src.lower():
            return f'background: {self.src};'
        
        # Calculate background-size and background-position for seamless tiling
        if region_count > 1:
            # For seamless panorama: size image to cover full slide, position to show this region's slice
            # Each region is 1/N of the slide, so image needs to be N times wider/taller
            if region_direction == 'horizontal':
                # Image width = N * 100% to span all regions when each region is 1/N wide
                bg_size = f'{region_count * 100}% auto'
                # Position: region 0 shows left edge (0%), region N-1 shows right edge (100%)
                pos_percent = (region_index * 100 / (region_count - 1)) if region_count > 1 else 0
                bg_position = f'{pos_percent}% center'
            else:
                # Vertical: image height spans all regions
                bg_size = f'auto {region_count * 100}%'
                pos_percent = (region_index * 100 / (region_count - 1)) if region_count > 1 else 0
                bg_position = f'center {pos_percent}%'
        else:
            # Single region - use cover and position from modifiers
            bg_size = 'cover'
            bg_position = self.get_background_position()
        
        # Get image URL (with blur if needed)
        if self.has_blur:
            src = self.src
            if src.startswith('url(') and src.endswith(')'):
                src = src[4:-1].strip('"\'')
            radius = self.get_blur_radius(theme_blur_default)
            img_url = f'{blur_endpoint}?path={src}&radius={radius}'
        else:
            if self.src.startswith('url('):
                img_url = self.src[4:-1].strip('"\'')
            else:
                img_url = self.src
        
        return f'background: url({img_url}) {bg_position}/{bg_size} no-repeat;'
    
    def _register_for_hot_reload(self) -> None:
        """Register this image's source file for hot-reload watching."""
        # Skip non-file sources
        if (self.src.startswith(('#', 'http://', 'https://', 'data:')) or
            'gradient' in self.src.lower()):
            return
        
        # Extract path from url(...) if present
        src = self.src
        if src.startswith('url(') and src.endswith(')'):
            src = src[4:-1].strip('"\'')
        
        # Register via current DeckViewer (has access to media folder mappings)
        from ..viewer import DeckViewer
        viewer = DeckViewer.get_current()
        if viewer:
            viewer.register_watched_file(src)
    
    def build_background(
        self,
        container_classes: str = 'absolute inset-0',
        theme_overlay_opacity: float = 0.5,
        theme_blur_default: float = 4.0,
        region_index: int = 0,
        region_count: int = 1,
        region_direction: str = 'horizontal',
    ) -> None:
        """Build background image with optional overlay.
        
        :param container_classes: CSS classes for the container.
        :param theme_overlay_opacity: Default overlay opacity from theme.
        :param theme_blur_default: Default blur radius from theme.
        :param region_index: Index of this region (0-based) for seamless tiling.
        :param region_count: Total number of regions sharing this image.
        :param region_direction: 'horizontal' or 'vertical' for seamless tiling.
        """
        self._register_for_hot_reload()
        
        bg_css = self.get_background_css(
            theme_blur_default=theme_blur_default,
            region_index=region_index,
            region_count=region_count,
            region_direction=region_direction,
        )
        ui.element('div').classes(container_classes).style(bg_css)
        
        # Add overlay if requested
        if self.has_overlay:
            opacity = self.get_overlay_opacity(theme_overlay_opacity)
            ui.element('div').classes(container_classes).style(
                f'background: rgba(0, 0, 0, {opacity}); pointer-events: none;'
            )
    
    def build_inline(self, max_height: str = '60%') -> None:
        """Build inline image for content display.
        
        :param max_height: Maximum height CSS value. Default '60%' adapts to
            the parent container, working correctly in split layouts (top/bottom,
            left/right) and different region counts.
        """
        self._register_for_hot_reload()
        
        ui.image(self.src).style(
            f'max-width: 100%; '
            f'max-height: {max_height}; '
            f'height: auto; '
            f'border-radius: {self.style.border_radius}; '
            f'margin: 0.5em auto; '
            f'display: block; '
            f'object-fit: {self.style.object_fit};'
        )
    
    async def build(self) -> None:
        """Build the image element based on mode."""
        if self.mode == 'inline':
            self.build_inline()
        else:
            self.build_background()
