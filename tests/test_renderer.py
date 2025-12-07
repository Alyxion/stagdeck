"""Tests for SlideRenderer and render endpoints."""

import io
import zipfile
from unittest.mock import Mock, patch, MagicMock

import pytest
from PIL import Image

from stagdeck.renderer import SlideRenderer


# =============================================================================
# Unit Tests - SlideRenderer class methods
# =============================================================================

class TestSlideRendererInit:
    """Test SlideRenderer initialization."""
    
    def test_default_values(self):
        """Test default initialization values."""
        renderer = SlideRenderer()
        assert renderer.base_url == 'http://localhost:8080'
        assert renderer.render_delay == 2.0
        assert renderer.chrome_driver_path is None
    
    def test_custom_base_url(self):
        """Test custom base URL."""
        renderer = SlideRenderer(base_url='http://example.com:3000/')
        assert renderer.base_url == 'http://example.com:3000'  # Trailing slash stripped
    
    def test_custom_render_delay(self):
        """Test custom render delay."""
        renderer = SlideRenderer(render_delay=5.0)
        assert renderer.render_delay == 5.0
    
    def test_custom_chrome_driver_path(self):
        """Test custom chromedriver path."""
        renderer = SlideRenderer(chrome_driver_path='/usr/local/bin/chromedriver')
        assert renderer.chrome_driver_path == '/usr/local/bin/chromedriver'


class TestSlideRendererContextManager:
    """Test SlideRenderer context manager support."""
    
    def test_sync_context_manager(self):
        """Test synchronous context manager."""
        with SlideRenderer() as renderer:
            assert isinstance(renderer, SlideRenderer)
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test asynchronous context manager."""
        async with SlideRenderer() as renderer:
            assert isinstance(renderer, SlideRenderer)


class TestRenderBatchZipProcessing:
    """Test render_batch_zip image processing logic."""
    
    def _create_test_png(self, width: int = 1920, height: int = 1080) -> bytes:
        """Create a test PNG image."""
        img = Image.new('RGB', (width, height), color=(100, 150, 200))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @pytest.mark.asyncio
    async def test_zip_contains_correct_files(self):
        """Test that ZIP contains expected files."""
        renderer = SlideRenderer()
        
        # Mock render_batch to return test images
        test_results = [
            ('slide_0_step_0.png', self._create_test_png()),
            ('slide_1_step_0.png', self._create_test_png()),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            zip_bytes = await renderer.render_batch_zip(
                slides=[0, 1],
                steps='first',
            )
        
        # Verify ZIP contents
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            names = zf.namelist()
            assert len(names) == 2
            assert 'slide_0_step_0.png' in names
            assert 'slide_1_step_0.png' in names
    
    @pytest.mark.asyncio
    async def test_zip_with_zoom_scaling(self):
        """Test that zoom parameter scales images correctly."""
        renderer = SlideRenderer()
        
        test_results = [
            ('slide_0_step_0.png', self._create_test_png(1920, 1080)),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            zip_bytes = await renderer.render_batch_zip(
                slides=[0],
                steps='first',
                zoom=0.5,
            )
        
        # Extract and verify image dimensions
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            img_data = zf.read('slide_0_step_0.png')
            img = Image.open(io.BytesIO(img_data))
            assert img.size == (960, 540)  # 1920*0.5, 1080*0.5
    
    @pytest.mark.asyncio
    async def test_zip_with_jpg_format(self):
        """Test that format=jpg produces JPEG files."""
        renderer = SlideRenderer()
        
        test_results = [
            ('slide_0_step_0.png', self._create_test_png()),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            zip_bytes = await renderer.render_batch_zip(
                slides=[0],
                steps='first',
                format='jpg',
                quality=85,
            )
        
        # Verify file extension and format
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            names = zf.namelist()
            assert 'slide_0_step_0.jpg' in names
            
            img_data = zf.read('slide_0_step_0.jpg')
            img = Image.open(io.BytesIO(img_data))
            assert img.format == 'JPEG'
    
    @pytest.mark.asyncio
    async def test_zip_uncompressed(self):
        """Test that ZIP uses no compression (ZIP_STORED)."""
        renderer = SlideRenderer()
        
        test_results = [
            ('slide_0_step_0.png', self._create_test_png()),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            zip_bytes = await renderer.render_batch_zip(slides=[0], steps='first')
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            for info in zf.infolist():
                assert info.compress_type == zipfile.ZIP_STORED


class TestRenderGridProcessing:
    """Test render_grid image processing logic."""
    
    def _create_test_png(self, width: int = 1920, height: int = 1080) -> bytes:
        """Create a test PNG image."""
        img = Image.new('RGB', (width, height), color=(100, 150, 200))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @pytest.mark.asyncio
    async def test_grid_dimensions_single_row(self):
        """Test grid dimensions with single row."""
        renderer = SlideRenderer()
        
        # 3 slides, 3 columns = 1 row
        test_results = [
            ('slide_0_step_0.png', self._create_test_png()),
            ('slide_1_step_0.png', self._create_test_png()),
            ('slide_2_step_0.png', self._create_test_png()),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            grid_bytes = await renderer.render_grid(
                slides=[0, 1, 2],
                steps='first',
                cols=3,
                zoom=0.25,
                padding=10,
            )
        
        img = Image.open(io.BytesIO(grid_bytes))
        # 3 thumbnails * 480px + 4 padding * 10px = 1440 + 40 = 1480
        # 1 row * 270px + 2 padding * 10px = 270 + 20 = 290
        thumb_width = int(1920 * 0.25)  # 480
        thumb_height = int(1080 * 0.25)  # 270
        expected_width = 3 * thumb_width + 4 * 10  # 1480
        expected_height = 1 * thumb_height + 2 * 10  # 290
        assert img.size == (expected_width, expected_height)
    
    @pytest.mark.asyncio
    async def test_grid_dimensions_multiple_rows(self):
        """Test grid dimensions with multiple rows."""
        renderer = SlideRenderer()
        
        # 5 slides, 2 columns = 3 rows
        test_results = [
            (f'slide_{i}_step_0.png', self._create_test_png())
            for i in range(5)
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            grid_bytes = await renderer.render_grid(
                slides=list(range(5)),
                steps='first',
                cols=2,
                zoom=0.25,
                padding=10,
            )
        
        img = Image.open(io.BytesIO(grid_bytes))
        thumb_width = int(1920 * 0.25)  # 480
        thumb_height = int(1080 * 0.25)  # 270
        expected_width = 2 * thumb_width + 3 * 10  # 990
        expected_height = 3 * thumb_height + 4 * 10  # 850
        assert img.size == (expected_width, expected_height)
    
    @pytest.mark.asyncio
    async def test_grid_jpg_format(self):
        """Test grid with JPEG output format."""
        renderer = SlideRenderer()
        
        test_results = [
            ('slide_0_step_0.png', self._create_test_png()),
        ]
        
        with patch.object(renderer, 'render_batch', return_value=test_results):
            grid_bytes = await renderer.render_grid(
                slides=[0],
                steps='first',
                format='jpg',
                quality=80,
            )
        
        img = Image.open(io.BytesIO(grid_bytes))
        assert img.format == 'JPEG'
    
    @pytest.mark.asyncio
    async def test_grid_empty_results(self):
        """Test grid with no slides returns minimal image."""
        renderer = SlideRenderer()
        
        with patch.object(renderer, 'render_batch', return_value=[]):
            grid_bytes = await renderer.render_grid(
                slides=[],
                steps='first',
                zoom=0.25,
            )
        
        img = Image.open(io.BytesIO(grid_bytes))
        # Empty grid returns single thumbnail-sized image
        assert img.size == (int(1920 * 0.25), int(1080 * 0.25))


class TestRenderBatchBuildList:
    """Test render_batch list building logic."""
    
    @pytest.mark.asyncio
    async def test_slides_all_with_steps_first(self):
        """Test slides='all' with steps='first'."""
        renderer = SlideRenderer()
        
        captured_args = {}
        
        async def mock_executor(executor, func, *args):
            captured_args['render_list'] = args[0]
            return []
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_in_executor = mock_executor
            await renderer.render_batch(slides='all', steps='first', max_slides=5)
        
        # Should create (slide, 0) for slides 0-4
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        assert captured_args['render_list'] == expected
    
    @pytest.mark.asyncio
    async def test_slides_list_with_steps_all(self):
        """Test specific slides with steps='all'."""
        renderer = SlideRenderer()
        
        captured_args = {}
        
        async def mock_executor(executor, func, *args):
            captured_args['render_list'] = args[0]
            return []
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_in_executor = mock_executor
            await renderer.render_batch(slides=[0, 1], steps='all')
        
        # Should create (slide, step) for steps 0-9 for each slide
        expected = []
        for slide in [0, 1]:
            for step in range(10):
                expected.append((slide, step))
        assert captured_args['render_list'] == expected
    
    @pytest.mark.asyncio
    async def test_slides_list_with_steps_list(self):
        """Test specific slides with specific steps."""
        renderer = SlideRenderer()
        
        captured_args = {}
        
        async def mock_executor(executor, func, *args):
            captured_args['render_list'] = args[0]
            return []
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_in_executor = mock_executor
            await renderer.render_batch(slides=[0, 2], steps=[0, 2])
        
        expected = [(0, 0), (0, 2), (2, 0), (2, 2)]
        assert captured_args['render_list'] == expected
    
    @pytest.mark.asyncio
    async def test_slides_with_names(self):
        """Test slides and steps can be names (strings)."""
        renderer = SlideRenderer()
        
        captured_args = {}
        
        async def mock_executor(executor, func, *args):
            captured_args['render_list'] = args[0]
            return []
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_in_executor = mock_executor
            await renderer.render_batch(
                slides=['intro', 'conclusion'],
                steps=['step_0', 'reveal'],
            )
        
        expected = [
            ('intro', 'step_0'), ('intro', 'reveal'),
            ('conclusion', 'step_0'), ('conclusion', 'reveal'),
        ]
        assert captured_args['render_list'] == expected


# =============================================================================
# Integration Tests - Render Endpoints (requires running server)
# =============================================================================

@pytest.mark.integration
class TestRenderEndpointsIntegration:
    """Integration tests for render endpoints.
    
    These tests use the stagdeck_server fixture which starts a real server.
    """
    
    @pytest.mark.asyncio
    async def test_render_single_slide_png(self, stagdeck_server):
        """Test /render endpoint returns valid PNG."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render',
                params={'slide': 0, 'step': 0},
                timeout=30.0,
            )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
        
        img = Image.open(io.BytesIO(response.content))
        assert img.format == 'PNG'
        assert img.size == (1920, 1080)
    
    @pytest.mark.asyncio
    async def test_render_grid_png(self, stagdeck_server):
        """Test /render/grid endpoint returns valid PNG grid."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render/grid',
                params={'cols': 3, 'zoom': 0.25},
                timeout=60.0,
            )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
        
        img = Image.open(io.BytesIO(response.content))
        assert img.format == 'PNG'
    
    @pytest.mark.asyncio
    async def test_render_grid_jpg(self, stagdeck_server):
        """Test /render/grid endpoint with JPEG format."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render/grid',
                params={'format': 'jpg', 'quality': 80},
                timeout=60.0,
            )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/jpeg'
        
        img = Image.open(io.BytesIO(response.content))
        assert img.format == 'JPEG'
    
    @pytest.mark.asyncio
    async def test_render_batch_zip(self, stagdeck_server):
        """Test /render/batch endpoint returns valid ZIP."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render/batch',
                params={'slides': '0,1', 'zoom': 0.5},
                timeout=60.0,
            )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'
        
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zf:
            names = zf.namelist()
            assert len(names) >= 1, f'Expected at least 1 file in ZIP, got {names}'
            assert all(name.endswith('.png') for name in names)
    
    @pytest.mark.asyncio
    async def test_render_batch_jpg_format(self, stagdeck_server):
        """Test /render/batch endpoint with JPEG format."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render/batch',
                params={'slides': '0', 'format': 'jpg', 'quality': 85},
                timeout=60.0,
            )
        
        assert response.status_code == 200
        
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zf:
            names = zf.namelist()
            assert len(names) >= 1, f'Expected at least 1 file in ZIP, got {names}'
            assert all(name.endswith('.jpg') for name in names)
            
            # Verify it's actually JPEG
            img_data = zf.read(names[0])
            img = Image.open(io.BytesIO(img_data))
            assert img.format == 'JPEG'
    
    @pytest.mark.asyncio
    async def test_render_with_step_name(self, stagdeck_server):
        """Test rendering with step name parameter."""
        import httpx
        
        base_url = stagdeck_server['base_url']
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{base_url}/render',
                params={'slide': '0', 'step': '0'},
                timeout=30.0,
            )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
