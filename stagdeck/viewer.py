"""🎬 DeckViewer - UI component for presenting slide decks."""

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from nicegui import ui

from .slide import Slide
from .slide_deck import SlideDeck

if TYPE_CHECKING:
    from .file_watcher import FileWatcher


class DeckViewer:
    """🖥️ UI viewer for presenting a SlideDeck.
    
    Separates presentation logic from deck data.
    
    :ivar deck: The SlideDeck to display.
    :ivar current_index: Index of the currently displayed slide.
    :ivar current_step: Current step within the slide (0-indexed).
    """
    
    _static_assets_initialized: bool = False
    
    def __init__(
        self,
        deck: SlideDeck,
        current_index: int = 0,
        current_step: int = 0,
        deck_factory: Callable[[], SlideDeck] | None = None,
    ) -> None:
        """
        Initialize the viewer.
        
        :param deck: The SlideDeck to display.
        :param current_index: Starting slide index.
        :param current_step: Starting step index.
        :param deck_factory: Optional factory for hot-reload support.
        """
        self.deck = deck
        self.current_index = current_index
        self.current_step = current_step
        self._slide_frame: ui.element | None = None
        self._slide_counter: ui.label | None = None
        self._deck_factory = deck_factory
        self._file_watcher: 'FileWatcher | None' = None
    
    @property
    def current_slide(self) -> Slide | None:
        """Get the current slide."""
        if not self.deck.slides:
            return None
        return self.deck.slides[self.current_index]
    
    @property
    def total_slides(self) -> int:
        """Get total number of slides."""
        return self.deck.total_slides
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next slide."""
        return self.current_index < len(self.deck.slides) - 1
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous slide."""
        return self.current_index > 0
    
    @property
    def has_next_step(self) -> bool:
        """Check if there's a next step in current slide."""
        slide = self.current_slide
        return slide is not None and self.current_step < slide.steps - 1
    
    @property
    def has_previous_step(self) -> bool:
        """Check if there's a previous step in current slide."""
        return self.current_step > 0
    
    @property
    def current_slide_name(self) -> str:
        """Get the name of the current slide."""
        slide = self.current_slide
        return slide.name if slide else ''
    
    @property
    def current_step_name(self) -> str:
        """Get the name of the current step."""
        slide = self.current_slide
        if slide is None:
            return ''
        return slide.get_step_name(self.current_step)
    
    @property
    def current_elapsed(self) -> float:
        """Get elapsed duration up to current position."""
        return self.deck.get_duration_at(self.current_index, self.current_step)
    
    # 🎯 Navigation methods
    
    async def next_slide(self) -> None:
        """⏭️ Go to the next slide."""
        if self.current_index < len(self.deck.slides) - 1:
            self.current_index += 1
            self.current_step = 0
            await self._update_view()
    
    async def previous_slide(self) -> None:
        """⏮️ Go to the previous slide."""
        if self.current_index > 0:
            self.current_index -= 1
            self.current_step = 0
            await self._update_view()
    
    async def next_step(self) -> None:
        """▶️ Go to the next step, or next slide if no more steps."""
        slide = self.current_slide
        if slide and self.current_step < slide.steps - 1:
            self.current_step += 1
            await self._update_view()
        else:
            await self.next_slide()
    
    async def previous_step(self) -> None:
        """◀️ Go to the previous step, or previous slide if at first step."""
        if self.current_step > 0:
            self.current_step -= 1
            await self._update_view()
        elif self.current_index > 0:
            self.current_index -= 1
            prev_slide = self.deck.slides[self.current_index]
            self.current_step = prev_slide.steps - 1
            await self._update_view()
    
    async def go_to_slide(self, index: int, step: int = 0) -> None:
        """🎯 Go to a specific slide by index and optionally step."""
        if 0 <= index < len(self.deck.slides):
            self.current_index = index
            slide = self.deck.slides[index]
            self.current_step = max(0, min(step, slide.steps - 1))
            await self._update_view()
    
    async def go_to_slide_by_name(self, slide_name: str, step_name: str | None = None) -> bool:
        """🔗 Navigate to a slide by name, optionally to a specific step."""
        index = self.deck.get_slide_index(slide_name)
        if index is None:
            return False
        
        step = 0
        if step_name is not None:
            slide = self.deck.slides[index]
            for s in range(slide.steps):
                if slide.get_step_name(s) == step_name:
                    step = s
                    break
        
        await self.go_to_slide(index, step)
        return True
    
    async def reload(self) -> None:
        """🔄 Reload the deck from source files and refresh the view.
        
        Used for hot-reload when markdown files change.
        Preserves the current slide position if possible.
        """
        if self._deck_factory is None:
            return
        
        # Remember current position
        current_name = self.current_slide.name if self.current_slide else None
        current_step = self.current_step
        
        # Reload deck
        self.deck = self._deck_factory()
        
        # Try to restore position by slide name
        if current_name:
            index = self.deck.get_slide_index(current_name)
            if index is not None:
                self.current_index = index
                slide = self.deck.slides[index]
                self.current_step = min(current_step, slide.steps - 1)
            else:
                # Slide was removed, clamp to valid range
                self.current_index = min(self.current_index, len(self.deck.slides) - 1)
                self.current_step = 0
        
        await self._update_view()
    
    # 🎨 UI rendering methods
    
    async def _update_view(self) -> None:
        """🔄 Update the slide view, counter, and URL."""
        if self._slide_frame is None:
            return
        self._slide_frame.clear()
        with self._slide_frame:
            await self._build_slide_content()
        if self._slide_counter:
            slide = self.current_slide
            if slide and slide.steps > 1:
                self._slide_counter.text = f'{self.current_index + 1}.{self.current_step + 1} / {self.total_slides}'
            else:
                self._slide_counter.text = f'{self.current_index + 1} / {self.total_slides}'
        self._update_url()
    
    def _update_url(self) -> None:
        """🔗 Update browser URL with current slide and step names."""
        slide_name = self.current_slide_name
        step_name = self.current_step_name
        ui.run_javascript(f'''
            const url = new URL(window.location);
            url.searchParams.set('slide', '{slide_name}');
            url.searchParams.set('step', '{step_name}');
            window.history.replaceState({{}}, '', url);
        ''')
    
    async def _build_slide_content(self) -> None:
        """🏗️ Build the current slide content."""
        slide = self.current_slide
        if not slide:
            ui.label('📭 No slides').classes('text-2xl text-gray-400')
            return
        
        # Get master layout if specified
        master_slide = self.deck.get_layout(slide.layout) if slide.layout else None
        
        # Let the slide build itself (with optional master layer and deck for style cascade)
        await slide.build(step=self.current_step, master_slide=master_slide, deck=self.deck)
    
    # ⌨️ Event handlers
    
    async def _toggle_fullscreen(self) -> None:
        """🖥️ Toggle browser fullscreen mode."""
        await ui.run_javascript('''
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        ''')
    
    async def _handle_key(self, e) -> None:
        """⌨️ Handle keyboard navigation."""
        if e.action.keydown:
            if e.key.arrow_right:
                await self.next_slide()
            elif e.key.arrow_left:
                await self.previous_slide()
            elif e.key.space and e.modifiers.shift:
                await self.previous_step()
            elif e.key.space:
                await self.next_step()
            elif e.key == 'f':
                await self._toggle_fullscreen()
    
    def _build_deck_menu(self) -> None:
        """📋 Build the deck switcher menu."""
        from .registry import registry
        
        deck_names = registry.deck_names
        if len(deck_names) <= 1:
            return
        
        with ui.button(icon='layers').props('flat').classes('opacity-30 hover:opacity-100'):
            with ui.menu().classes('bg-white dark:bg-gray-700'):
                for name in deck_names:
                    is_current = name == self.deck.title
                    ui.menu_item(
                        f'{"📌 " if is_current else "📄 "}{name}',
                        on_click=lambda n=name: ui.navigate.to(f'/?deck={n}'),
                    ).classes('font-bold' if is_current else '')
    
    # Track registered media folders to avoid duplicates
    _registered_media_folders: set[str] = set()
    
    @classmethod
    def _setup_static_assets(cls) -> None:
        """📦 Setup static CSS and JS assets (once per application)."""
        from pathlib import Path
        from nicegui import app
        
        # Always register static files (NiceGUI handles duplicates)
        static_dir = Path(__file__).parent / 'static'
        if not cls._static_assets_initialized:
            app.add_static_files('/stagdeck/static', static_dir)
            cls._static_assets_initialized = True
        
        # Add CSS and JS to head for this page
        ui.add_head_html('<link rel="stylesheet" href="/stagdeck/static/styles.css">')
        ui.add_head_html('<script src="/stagdeck/static/scaling.js"></script>')
    
    def _setup_media_folders(self) -> None:
        """📁 Register deck's media folders as static file routes."""
        from nicegui import app
        
        for url_path, local_path in self.deck.media_folders.items():
            # Only register each folder once
            if url_path not in DeckViewer._registered_media_folders:
                app.add_static_files(url_path, local_path)
                DeckViewer._registered_media_folders.add(url_path)
                # Also add to map for blur endpoint
                DeckViewer._registered_media_folders_map[url_path] = local_path
        
        # Register blurred image endpoint
        self._setup_blur_endpoint()
    
    @classmethod
    def _setup_blur_endpoint(cls) -> None:
        """📷 Setup endpoint for serving blurred images."""
        from nicegui import app
        from starlette.responses import Response
        from pathlib import Path
        
        # Only register once
        if hasattr(cls, '_blur_endpoint_registered') and cls._blur_endpoint_registered:
            return
        cls._blur_endpoint_registered = True
        
        @app.get('/stagdeck/blur')
        async def serve_blurred_image(path: str, radius: float = 4.0):
            """Serve a blurred version of an image."""
            from .utils.image_processing import apply_gaussian_blur
            
            # Security: resolve the path and check it's within a registered media folder
            image_path = cls._resolve_media_path(path)
            
            if image_path is None:
                return Response(content="Image not found", status_code=404)
            
            # Note: Hot-reload registration happens in ImageView._register_for_hot_reload()
            
            try:
                blurred_bytes = apply_gaussian_blur(image_path, blur_radius=radius)
                return Response(content=blurred_bytes, media_type="image/jpeg")
            except Exception as e:
                return Response(content=f"Error processing image: {e}", status_code=500)
    
    # Map of URL paths to local paths for blur endpoint
    _registered_media_folders_map: dict[str, Path] = {}
    
    @classmethod
    def _resolve_media_path(cls, url_path: str) -> Path | None:
        """Resolve a URL path to a local file path.
        
        :param url_path: URL path (e.g., '/media/image.jpg').
        :return: Resolved local Path or None if not found.
        """
        for url_prefix, local_dir in cls._registered_media_folders_map.items():
            if url_path.startswith(url_prefix):
                relative = url_path[len(url_prefix):].lstrip('/')
                candidate = Path(local_dir) / relative
                if candidate.exists() and candidate.is_file():
                    return candidate
        return None
    
    def register_watched_file(self, url_path: str) -> None:
        """Register a media file for hot-reload watching.
        
        Components should call this when they use a media file.
        
        :param url_path: URL path to the media file.
        """
        if self._file_watcher is None:
            return
        
        resolved = self._resolve_media_path(url_path)
        if resolved:
            self._file_watcher.watch(resolved)
    
    @classmethod
    def get_current(cls) -> 'DeckViewer | None':
        """Get the current DeckViewer from NiceGUI context.
        
        Components can use this to register files for hot-reload.
        
        :return: Current viewer or None if not in a viewer context.
        """
        try:
            client = ui.context.client
            return getattr(client, '_stagdeck_viewer', None)
        except Exception:
            return None
    
    def _set_as_current(self) -> None:
        """Set this viewer as the current one in NiceGUI context."""
        try:
            client = ui.context.client
            client._stagdeck_viewer = self
        except Exception:
            pass
    
    def _init_from_query_params(self) -> None:
        """🔍 Initialize slide and step from URL query parameters."""
        client = ui.context.client
        
        slide_param = client.request.query_params.get('slide')
        step_param = client.request.query_params.get('step')
        
        if slide_param is not None:
            index = self.deck.get_slide_index(slide_param)
            if index is not None:
                self.current_index = index
            else:
                try:
                    slide_index = int(slide_param)
                    if 0 <= slide_index < len(self.deck.slides):
                        self.current_index = slide_index
                except ValueError:
                    pass
        
        if step_param is not None:
            slide = self.current_slide
            if slide:
                found = False
                for s in range(slide.steps):
                    if slide.get_step_name(s) == step_param:
                        self.current_step = s
                        found = True
                        break
                if not found:
                    try:
                        step_index = int(step_param)
                        if 0 <= step_index < slide.steps:
                            self.current_step = step_index
                    except ValueError:
                        pass
    
    async def build(self) -> None:
        """🚀 Build the complete presentation UI."""
        self._set_as_current()
        self._init_from_query_params()
        self._setup_static_assets()
        self._setup_media_folders()
        
        ui.query('.nicegui-content').classes('p-0')
        
        with ui.column().classes('w-full h-screen overflow-hidden').style('height: 100vh; height: 100dvh;'):
            with ui.element('div').classes('slide-wrapper').style('flex: 1 1 0; min-height: 0; height: 100%;'):
                with ui.element('div').classes('slide-scaler'):
                    self._slide_frame = (
                        ui.element('div')
                        .classes('slide-frame')
                        .style(f'width: {self.deck.width}px; height: {self.deck.height}px;')
                    )
                    # Store dimensions for JS scaling
                    self._slide_frame._props['data-width'] = str(self.deck.width)
                    self._slide_frame._props['data-height'] = str(self.deck.height)
            
            with ui.row().classes('nav-bar w-full items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-800'):
                ui.button(icon='arrow_back', on_click=self.previous_slide).props('flat')
                self._slide_counter = ui.label().classes('text-lg')
                with ui.row().classes('gap-2'):
                    ui.button(icon='arrow_forward', on_click=self.next_slide).props('flat')
                    ui.button(icon='fullscreen', on_click=self._toggle_fullscreen).props('flat')
                    self._build_deck_menu()
        
        ui.keyboard(on_key=self._handle_key)
        await self._update_view()
    
    async def build_render_frame(self) -> None:
        """📸 Build just the slide frame for rendering (no navbar, no scaling).
        
        Used by the render endpoint to capture clean slide images.
        Always renders at deck's native resolution for consistent output.
        """
        self._init_from_query_params()
        self._setup_static_assets()  # Load CSS for proper styling
        self._setup_media_folders()  # Register media folders
        
        # No padding, exact slide dimensions
        ui.query('.nicegui-content').classes('p-0 m-0')
        ui.query('body').style('margin: 0; padding: 0; overflow: hidden;')
        
        # Slide frame at deck's native dimensions (never override)
        # Add 'scaled' class immediately since we don't use JS scaling for render
        self._slide_frame = (
            ui.element('div')
            .classes('slide-frame scaled')
            .style(f'width: {self.deck.width}px; height: {self.deck.height}px;')
        )
        
        await self._update_view()
