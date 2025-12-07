"""🎬 DeckViewer - UI component for presenting slide decks."""

from nicegui import ui

from .slide import Slide
from .slide_deck import SlideDeck


class DeckViewer:
    """🖥️ UI viewer for presenting a SlideDeck.
    
    Separates presentation logic from deck data.
    
    :ivar deck: The SlideDeck to display.
    :ivar current_index: Index of the currently displayed slide.
    :ivar current_step: Current step within the slide (0-indexed).
    """
    
    _static_assets_initialized: bool = False
    
    def __init__(self, deck: SlideDeck, current_index: int = 0, current_step: int = 0) -> None:
        """
        Initialize the viewer.
        
        :param deck: The SlideDeck to display.
        :param current_index: Starting slide index.
        :param current_step: Starting step index.
        """
        self.deck = deck
        self.current_index = current_index
        self.current_step = current_step
        self._slide_frame: ui.element | None = None
        self._slide_counter: ui.label | None = None
    
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
    
    def next_slide(self) -> None:
        """⏭️ Go to the next slide."""
        if self.current_index < len(self.deck.slides) - 1:
            self.current_index += 1
            self.current_step = 0
            self._update_view()
    
    def previous_slide(self) -> None:
        """⏮️ Go to the previous slide."""
        if self.current_index > 0:
            self.current_index -= 1
            self.current_step = 0
            self._update_view()
    
    def next_step(self) -> None:
        """▶️ Go to the next step, or next slide if no more steps."""
        slide = self.current_slide
        if slide and self.current_step < slide.steps - 1:
            self.current_step += 1
            self._update_view()
        else:
            self.next_slide()
    
    def previous_step(self) -> None:
        """◀️ Go to the previous step, or previous slide if at first step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_view()
        elif self.current_index > 0:
            self.current_index -= 1
            prev_slide = self.deck.slides[self.current_index]
            self.current_step = prev_slide.steps - 1
            self._update_view()
    
    def go_to_slide(self, index: int, step: int = 0) -> None:
        """🎯 Go to a specific slide by index and optionally step."""
        if 0 <= index < len(self.deck.slides):
            self.current_index = index
            slide = self.deck.slides[index]
            self.current_step = max(0, min(step, slide.steps - 1))
            self._update_view()
    
    def go_to_slide_by_name(self, slide_name: str, step_name: str | None = None) -> bool:
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
        
        self.go_to_slide(index, step)
        return True
    
    # 🎨 UI rendering methods
    
    def _update_view(self) -> None:
        """🔄 Update the slide view, counter, and URL."""
        if self._slide_frame is None:
            return
        self._slide_frame.clear()
        with self._slide_frame:
            self._build_slide_content()
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
    
    def _build_slide_content(self) -> None:
        """🏗️ Build the current slide content."""
        slide = self.current_slide
        if not slide:
            ui.label('📭 No slides').classes('text-2xl text-gray-400')
            return
        
        # Get master layout if specified
        master_slide = self.deck.get_layout(slide.layout) if slide.layout else None
        
        # Let the slide build itself (with optional master layer)
        slide.build(step=self.current_step, master_slide=master_slide)
    
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
                self.next_slide()
            elif e.key.arrow_left:
                self.previous_slide()
            elif e.key.space and e.modifiers.shift:
                self.previous_step()
            elif e.key.space:
                self.next_step()
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
    
    def build(self) -> None:
        """🚀 Build the complete presentation UI."""
        self._init_from_query_params()
        self._setup_static_assets()
        
        ui.query('.nicegui-content').classes('p-0 h-screen')
        
        with ui.column().classes('w-full h-screen'):
            with ui.element('div').classes('slide-wrapper flex-grow'):
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
        self._update_view()
    
    # =========================================================================
    # 🚀 App Entry Points
    # =========================================================================
    
    @classmethod
    def run(
        cls,
        deck: SlideDeck,
        title: str | None = None,
        path: str = '/',
        **kwargs,
    ) -> None:
        """🚀 Run the presentation app.
        
        Creates a page at the specified path and starts the NiceGUI server.
        
        :param deck: SlideDeck to present.
        :param title: Browser window title (defaults to deck title).
        :param path: URL path for the presentation (default: '/').
        :param kwargs: Additional arguments passed to ui.run().
        
        Example:
            >>> deck = SlideDeck(title='My Talk')
            >>> deck.add(title='Hello', content='World')
            >>> DeckViewer.run(deck)
        """
        window_title = title or deck.title
        
        @ui.page(path)
        def presentation_page():
            viewer = cls(deck=deck)
            viewer.build()
        
        ui.run(title=window_title, show=kwargs.pop('show', False), **kwargs)
    
    @classmethod
    def create_page(
        cls,
        deck: SlideDeck,
        path: str = '/',
    ) -> None:
        """📄 Register a presentation page without starting the server.
        
        Use this when you need custom routes or multiple presentations.
        Call ui.run() separately after setting up all pages.
        
        :param deck: SlideDeck to present.
        :param path: URL path for the presentation.
        
        Example:
            >>> DeckViewer.create_page(deck1, path='/')
            >>> DeckViewer.create_page(deck2, path='/backup')
            >>> ui.run()
        """
        @ui.page(path)
        def presentation_page():
            viewer = cls(deck=deck)
            viewer.build()
