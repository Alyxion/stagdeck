"""📸 SlideRenderer - Render slides to images using Selenium."""

import asyncio
import base64
import io
import zipfile
from typing import Callable

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from .slide_deck import SlideDeck


class SlideRenderer:
    """📸 Renders slides to images using headless Chrome.
    
    Creates a fresh WebDriver per render request to support concurrent
    requests with different resolutions.
    
    Example:
        >>> renderer = SlideRenderer()
        >>> png_bytes = await renderer.render_slide(
        ...     slide=0,
        ...     step=0,
        ...     width=1920,
        ...     height=1080,
        ... )
    """
    
    def __init__(
        self,
        base_url: str = 'http://localhost:8080',
        render_delay: float = 2.0,
        chrome_driver_path: str | None = None,
    ):
        """Initialize the renderer.
        
        :param base_url: Base URL of the running StagDeck server.
        :param render_delay: Seconds to wait for slide to render.
        :param chrome_driver_path: Path to chromedriver (uses system default if None).
        """
        self.base_url = base_url.rstrip('/')
        self.render_delay = render_delay
        self.chrome_driver_path = chrome_driver_path
    
    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome WebDriver instance."""
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--hide-scrollbars')
        
        if self.chrome_driver_path:
            service = Service(self.chrome_driver_path)
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
    
    def close(self) -> None:
        """Close any resources (no-op, drivers are per-request now)."""
        pass
    
    async def render_slide(
        self,
        slide: int | str = 0,
        step: int | str = 0,
        width: int = 1920,
        height: int = 1080,
        render_delay: float | None = None,
        path: str = '/',
    ) -> bytes:
        """Render a specific slide to PNG bytes.
        
        :param slide: Slide index or name.
        :param step: Step index or name.
        :param width: Output image width in pixels.
        :param height: Output image height in pixels.
        :param render_delay: Override default render delay.
        :param path: URL path to the presentation.
        :return: PNG image as bytes.
        """
        delay = render_delay if render_delay is not None else self.render_delay
        
        # Build URL with query params - use render frame page
        url = f'{self.base_url}/_render_frame?slide={slide}&step={step}'
        
        # Run Selenium in thread pool to not block async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._capture_screenshot,
            url,
            width,
            height,
            delay,
        )
    
    def _capture_screenshot(
        self,
        url: str,
        width: int,
        height: int,
        delay: float,
    ) -> bytes:
        """Capture screenshot synchronously (runs in thread pool)."""
        driver = self._create_driver()
        
        try:
            # Set viewport size (not window size) to exact dimensions
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': width,
                'height': height,
                'deviceScaleFactor': 1,
                'mobile': False,
            })
            
            # Navigate to render frame page
            driver.get(url)
            
            # Wait for slide frame to be present
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'slide-frame'))
                )
            except Exception:
                pass  # Continue anyway, might still render
            
            # Additional delay for animations/content to load
            import time
            time.sleep(delay)
            
            # Capture full page screenshot (render frame page has no navbar)
            png_bytes = driver.get_screenshot_as_png()
            
            return png_bytes
        finally:
            driver.quit()
    
    async def render_slide_base64(
        self,
        slide: int | str = 0,
        step: int | str = 0,
        width: int = 1920,
        height: int = 1080,
        render_delay: float | None = None,
        path: str = '/',
    ) -> str:
        """Render a specific slide to base64-encoded PNG.
        
        :param slide: Slide index or name.
        :param step: Step index or name.
        :param width: Output image width in pixels.
        :param height: Output image height in pixels.
        :param render_delay: Override default render delay.
        :param path: URL path to the presentation.
        :return: Base64-encoded PNG string.
        """
        png_bytes = await self.render_slide(
            slide=slide,
            step=step,
            width=width,
            height=height,
            render_delay=render_delay,
            path=path,
        )
        return base64.b64encode(png_bytes).decode('utf-8')
    
    async def render_batch(
        self,
        slides: list[int | str] | str = 'all',
        steps: list[int | str] | str = 'first',
        width: int = 1920,
        height: int = 1080,
        render_delay: float | None = None,
        max_slides: int = 50,
    ) -> list[tuple[str, bytes]]:
        """Render multiple slides to PNG images.
        
        :param slides: List of slide indices/names, or 'all' for all slides.
        :param steps: List of step indices/names, 'first' (step 0), or 'all' for all steps.
        :param width: Output image width in pixels.
        :param height: Output image height in pixels.
        :param render_delay: Override default render delay.
        :param max_slides: Maximum slides to render when using 'all' (default 50).
        :return: List of (filename, png_bytes) tuples.
        """
        delay = render_delay if render_delay is not None else self.render_delay
        
        # Build list of (slide, step) pairs to render
        render_list: list[tuple[int | str, int | str]] = []
        
        if slides == 'all':
            # Use max_slides limit
            slide_indices = list(range(max_slides))
        else:
            slide_indices = slides
        
        for slide in slide_indices:
            if steps == 'first':
                render_list.append((slide, 0))
            elif steps == 'all':
                # Render steps 0-9 (reasonable max)
                for step in range(10):
                    render_list.append((slide, step))
            else:
                for step in steps:
                    render_list.append((slide, step))
        
        # Run in thread pool to not block event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._capture_batch,
            render_list,
            slides,
            width,
            height,
            delay,
        )
    
    def _capture_batch(
        self,
        render_list: list[tuple[int | str, int | str]],
        slides_mode: list | str,
        width: int,
        height: int,
        delay: float,
    ) -> list[tuple[str, bytes]]:
        """Capture multiple screenshots synchronously (runs in thread pool)."""
        import time
        import hashlib
        
        results: list[tuple[str, bytes]] = []
        driver = self._create_driver()
        last_screenshot_hash = None
        consecutive_same = 0
        
        try:
            # Set viewport size
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': width,
                'height': height,
                'deviceScaleFactor': 1,
                'mobile': False,
            })
            
            for slide, step in render_list:
                url = f'{self.base_url}/_render_frame?slide={slide}&step={step}'
                driver.get(url)
                
                # Wait for slide frame
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'slide-frame'))
                    )
                except Exception:
                    # No more slides or invalid slide
                    if slides_mode == 'all':
                        break
                    continue
                
                time.sleep(delay)
                
                png_bytes = driver.get_screenshot_as_png()
                
                # For 'all' mode, detect when we've gone past the last slide
                # by checking if screenshots are identical (same "no slide" page)
                if slides_mode == 'all':
                    current_hash = hashlib.md5(png_bytes).hexdigest()
                    if current_hash == last_screenshot_hash:
                        consecutive_same += 1
                        if consecutive_same >= 2:
                            # Same screenshot twice = we've gone past the end
                            break
                    else:
                        consecutive_same = 0
                        last_screenshot_hash = current_hash
                
                filename = f'slide_{slide}_step_{step}.png'
                results.append((filename, png_bytes))
        finally:
            driver.quit()
        
        return results
    
    async def render_batch_zip(
        self,
        slides: list[int | str] | str = 'all',
        steps: list[int | str] | str = 'first',
        zoom: float = 1.0,
        render_delay: float | None = None,
        format: str = 'png',
        quality: int = 90,
        native_width: int = 1920,
        native_height: int = 1080,
    ) -> bytes:
        """Render multiple slides and return as uncompressed ZIP.
        
        :param slides: List of slide indices/names, or 'all' for all slides.
        :param steps: List of step indices/names, 'first' (step 0), or 'all' for all steps.
        :param zoom: Scale factor for output images (1.0 = native resolution).
        :param render_delay: Override default render delay.
        :param format: Output format ('png' or 'jpg').
        :param quality: JPEG quality (1-100, only for jpg).
        :param native_width: Native slide width for rendering.
        :param native_height: Native slide height for rendering.
        :return: ZIP file bytes containing images.
        """
        # Always render at native resolution for quality
        results = await self.render_batch(
            slides=slides,
            steps=steps,
            width=native_width,
            height=native_height,
            render_delay=render_delay,
        )
        
        # Calculate output size from zoom
        out_width = int(native_width * zoom)
        out_height = int(native_height * zoom)
        ext = 'jpg' if format.lower() == 'jpg' else 'png'
        
        # Create uncompressed ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zf:
            for filename, png_bytes in results:
                # Scale if zoom != 1.0
                if zoom != 1.0:
                    img = Image.open(io.BytesIO(png_bytes))
                    img = img.resize((out_width, out_height), Image.Resampling.LANCZOS)
                else:
                    img = Image.open(io.BytesIO(png_bytes))
                
                # Convert to output format
                img_buffer = io.BytesIO()
                if format.lower() == 'jpg':
                    img = img.convert('RGB')  # JPEG doesn't support alpha
                    img.save(img_buffer, format='JPEG', quality=quality)
                else:
                    img.save(img_buffer, format='PNG')
                
                # Update filename extension
                base_name = filename.rsplit('.', 1)[0]
                zf.writestr(f'{base_name}.{ext}', img_buffer.getvalue())
        
        return zip_buffer.getvalue()
    
    async def render_grid(
        self,
        slides: list[int | str] | str = 'all',
        steps: list[int | str] | str = 'first',
        cols: int = 3,
        zoom: float = 0.25,
        render_delay: float | None = None,
        padding: int = 10,
        bg_color: tuple[int, int, int] = (40, 40, 40),
        format: str = 'png',
        quality: int = 90,
        native_width: int = 1920,
        native_height: int = 1080,
    ) -> bytes:
        """Render slides as a grid image for quick overview.
        
        Renders at native resolution then scales down with Lanczos for quality.
        
        :param slides: List of slide indices/names, or 'all' for all slides.
        :param steps: List of step indices/names, 'first' (step 0), or 'all' for all steps.
        :param cols: Number of columns in grid.
        :param zoom: Scale factor for thumbnails (0.25 = 25% of native).
        :param render_delay: Override default render delay.
        :param padding: Padding between thumbnails.
        :param bg_color: Background color RGB tuple.
        :param format: Output format ('png' or 'jpg').
        :param quality: JPEG quality (1-100, only for jpg).
        :param native_width: Native slide width for rendering.
        :param native_height: Native slide height for rendering.
        :return: Image bytes in requested format.
        """
        # Render at native resolution
        results = await self.render_batch(
            slides=slides,
            steps=steps,
            width=native_width,
            height=native_height,
            render_delay=render_delay,
        )
        
        # Calculate thumbnail size from zoom
        thumb_width = int(native_width * zoom)
        thumb_height = int(native_height * zoom)
        
        if not results:
            # Return empty image
            img = Image.new('RGB', (thumb_width, thumb_height), bg_color)
            buffer = io.BytesIO()
            img.save(buffer, format=format.upper())
            return buffer.getvalue()
        
        # Calculate grid dimensions
        num_images = len(results)
        rows = (num_images + cols - 1) // cols
        
        grid_width = cols * thumb_width + (cols + 1) * padding
        grid_height = rows * thumb_height + (rows + 1) * padding
        
        # Create grid image
        grid = Image.new('RGB', (grid_width, grid_height), bg_color)
        
        for i, (filename, png_bytes) in enumerate(results):
            row = i // cols
            col = i % cols
            
            # Load and resize thumbnail with Lanczos
            thumb = Image.open(io.BytesIO(png_bytes))
            thumb = thumb.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            
            # Calculate position
            x = padding + col * (thumb_width + padding)
            y = padding + row * (thumb_height + padding)
            
            grid.paste(thumb, (x, y))
        
        # Save to bytes
        buffer = io.BytesIO()
        if format.lower() == 'jpg':
            grid.save(buffer, format='JPEG', quality=quality)
        else:
            grid.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        self.close()


def setup_render_endpoint(
    path: str = '/render',
    require_auth: bool = False,
) -> None:
    """Setup a render endpoint on the NiceGUI app.
    
    Creates an endpoint at `{path}` that renders slides to PNG images.
    Each request creates a fresh WebDriver for concurrent safety.
    
    Query parameters:
        - slide: Slide index or name (default: 0)
        - step: Step index or name (default: 0)
        - width: Image width (default: 1920)
        - height: Image height (default: 1080)
        - delay: Render delay in seconds (default: 2.0)
        - format: 'png' or 'base64' (default: 'png')
    
    :param path: URL path for the render endpoint.
    :param require_auth: If True, require authentication (not implemented).
    
    Example:
        >>> App.create_page(create_deck, path='/')
        >>> setup_render_endpoint(path='/render')
        >>> ui.run()
        
        # Then access:
        # GET /render?slide=0&step=0&width=1920&height=1080
    """
    from nicegui import app
    from fastapi import Response, Query
    
    # Renderer instance (drivers are created per-request)
    renderer = SlideRenderer()
    
    @app.get(path)
    async def render_slide_endpoint(
        slide: str = Query(default='0', description='Slide index or name'),
        step: str = Query(default='0', description='Step index or name'),
        width: int = Query(default=1920, ge=100, le=7680, description='Image width'),
        height: int = Query(default=1080, ge=100, le=4320, description='Image height'),
        delay: float = Query(default=2.0, ge=0.1, le=30.0, description='Render delay'),
        format: str = Query(default='png', pattern='^(png|base64)$', description='Output format'),
    ) -> Response:
        """Render a slide to an image."""
        try:
            png_bytes = await renderer.render_slide(
                slide=slide,
                step=step,
                width=width,
                height=height,
                render_delay=delay,
            )
            
            if format == 'base64':
                b64 = base64.b64encode(png_bytes).decode('utf-8')
                return Response(
                    content=b64,
                    media_type='text/plain',
                )
            else:
                return Response(
                    content=png_bytes,
                    media_type='image/png',
                    headers={
                        'Content-Disposition': f'inline; filename="slide_{slide}_step_{step}.png"'
                    },
                )
        except Exception as e:
            return Response(
                content=f'Render error: {str(e)}',
                status_code=500,
                media_type='text/plain',
            )
    
    @app.get(f'{path}/batch')
    async def render_batch_endpoint(
        slides: str = Query(default='all', description='Comma-separated slide indices/names or "all"'),
        steps: str = Query(default='first', description='Comma-separated step indices/names, "first", or "all"'),
        zoom: float = Query(default=1.0, ge=0.1, le=1.0, description='Zoom factor (1.0 = native resolution)'),
        delay: float = Query(default=1.0, ge=0.1, le=30.0, description='Render delay per slide'),
        format: str = Query(default='png', pattern='^(png|jpg)$', description='Output format'),
        quality: int = Query(default=90, ge=1, le=100, description='JPEG quality'),
    ) -> Response:
        """Render multiple slides as uncompressed ZIP file."""
        try:
            # Parse slides parameter (supports indices and names)
            if slides == 'all':
                slide_list = 'all'
            else:
                slide_list = [int(s) if s.isdigit() else s for s in slides.split(',')]
            
            # Parse steps parameter (supports indices and names like 'step_0', 'reveal_1')
            if steps == 'first':
                step_list = 'first'
            elif steps == 'all':
                step_list = 'all'
            else:
                # Keep as strings - viewer handles both indices and names
                step_list = [int(s) if s.isdigit() else s for s in steps.split(',')]
            
            zip_bytes = await renderer.render_batch_zip(
                slides=slide_list,
                steps=step_list,
                zoom=zoom,
                render_delay=delay,
                format=format,
                quality=quality,
            )
            
            ext = 'jpg' if format == 'jpg' else 'png'
            return Response(
                content=zip_bytes,
                media_type='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename="slides_{ext}.zip"'
                },
            )
        except Exception as e:
            return Response(
                content=f'Render error: {str(e)}',
                status_code=500,
                media_type='text/plain',
            )
    
    @app.get(f'{path}/grid')
    async def render_grid_endpoint(
        slides: str = Query(default='all', description='Comma-separated slide indices/names or "all"'),
        steps: str = Query(default='first', description='Comma-separated step indices/names, "first", or "all"'),
        cols: int = Query(default=3, ge=1, le=10, description='Number of columns'),
        zoom: float = Query(default=0.25, ge=0.1, le=1.0, description='Zoom factor (0.25 = 25%)'),
        delay: float = Query(default=1.0, ge=0.1, le=30.0, description='Render delay per slide'),
        format: str = Query(default='png', pattern='^(png|jpg)$', description='Output format'),
        quality: int = Query(default=90, ge=1, le=100, description='JPEG quality'),
    ) -> Response:
        """Render slides as a grid image for quick overview."""
        try:
            # Parse slides parameter (supports indices and names)
            if slides == 'all':
                slide_list = 'all'
            else:
                slide_list = [int(s) if s.isdigit() else s for s in slides.split(',')]
            
            # Parse steps parameter (supports indices and names like 'step_0', 'reveal_1')
            if steps == 'first':
                step_list = 'first'
            elif steps == 'all':
                step_list = 'all'
            else:
                # Keep as strings - viewer handles both indices and names
                step_list = [int(s) if s.isdigit() else s for s in steps.split(',')]
            
            grid_bytes = await renderer.render_grid(
                slides=slide_list,
                steps=step_list,
                cols=cols,
                zoom=zoom,
                render_delay=delay,
                format=format,
                quality=quality,
            )
            
            media_type = 'image/jpeg' if format == 'jpg' else 'image/png'
            ext = 'jpg' if format == 'jpg' else 'png'
            
            return Response(
                content=grid_bytes,
                media_type=media_type,
                headers={
                    'Content-Disposition': f'inline; filename="slides_grid.{ext}"'
                },
            )
        except Exception as e:
            return Response(
                content=f'Render error: {str(e)}',
                status_code=500,
                media_type='text/plain',
            )
