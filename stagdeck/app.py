"""🚀 App - Application lifecycle management for StagDeck."""

import asyncio
from pathlib import Path
from typing import Callable

from nicegui import ui, app

from .file_watcher import FileWatcher
from .slide_deck import SlideDeck
from .viewer import DeckViewer


class App:
    """🚀 Application lifecycle manager for StagDeck presentations.
    
    Handles server startup, page routing, and per-user deck creation.
    Separates application concerns from the DeckViewer which only handles viewing.
    
    Example:
        >>> def create_deck():
        ...     deck = SlideDeck(title='My Talk')
        ...     deck.add(title='Hello', content='World!')
        ...     return deck
        >>> App.run(create_deck)
    """
    
    @classmethod
    def run(
        cls,
        deck_factory: Callable[[], SlideDeck],
        title: str = 'Presentation',
        path: str = '/',
        enable_render: bool = True,
        render_path: str = '/render',
        hot_reload: bool = True,
        **kwargs,
    ) -> None:
        """🚀 Run the presentation app.
        
        Creates a page at the specified path and starts the NiceGUI server.
        The deck_factory is called for each user request, ensuring isolated state.
        
        :param deck_factory: Factory function that creates a SlideDeck per request.
        :param title: Browser window title.
        :param path: URL path for the presentation (default: '/').
        :param enable_render: Enable slide rendering endpoint (requires Selenium).
        :param render_path: URL path for render endpoint (default: '/render').
        :param hot_reload: Auto-reload when markdown source files change (default: True).
        :param kwargs: Additional arguments passed to ui.run().
        
        Example:
            >>> def create_deck():
            ...     deck = SlideDeck(title='My Talk')
            ...     deck.add(title='Hello')
            ...     return deck
            >>> App.run(create_deck, title='My Presentation')
            
            # With render endpoint:
            >>> App.run(create_deck, enable_render=True)
            # GET /render?slide=0&step=0&width=1920&height=1080
        """
        @ui.page(path)
        async def presentation_page():
            deck = deck_factory()
            viewer = DeckViewer(
                deck=deck,
                deck_factory=deck_factory if hot_reload else None,
            )
            
            # Setup hot-reload for this viewer
            if hot_reload and deck.source_files:
                watcher = FileWatcher()
                viewer._file_watcher = watcher
                viewer._needs_reload = False
                
                for source_file in deck.source_files:
                    watcher.watch(source_file)
                
                # FileWatcher sets flag, timer checks it from UI context
                def on_file_change(path):
                    viewer._needs_reload = True
                
                async def check_reload():
                    if viewer._needs_reload:
                        viewer._needs_reload = False
                        await viewer.reload()
                
                watcher.on_change(on_file_change)
                asyncio.create_task(watcher.start())
                
                # Timer runs in UI context and can safely call reload
                ui.timer(0.5, check_reload)
            
            await viewer.build()
        
        # Render-only page (no navbar, for screenshot capture)
        @ui.page('/_render_frame')
        async def render_frame_page():
            deck = deck_factory()
            viewer = DeckViewer(deck=deck)
            await viewer.build_render_frame()
        
        if enable_render:
            from .renderer import setup_render_endpoint
            setup_render_endpoint(path=render_path)
        
        ui.run(title=title, reload=True, show=kwargs.pop('show', False), **kwargs)
    
    @classmethod
    def create_page(
        cls,
        deck_factory: Callable[[], SlideDeck],
        path: str = '/',
        enable_render_frame: bool = True,
    ) -> None:
        """📄 Register a presentation page without starting the server.
        
        Use this when you need custom routes or multiple presentations.
        Call ui.run() separately after setting up all pages.
        
        :param deck_factory: Factory function that creates a SlideDeck per request.
        :param path: URL path for the presentation.
        :param enable_render_frame: If True, also create /_render_frame endpoint for rendering.
        
        Example:
            >>> App.create_page(create_main_deck, path='/')
            >>> App.create_page(create_backup_deck, path='/backup')
            >>> ui.run(title='My Presentations')
        """
        @ui.page(path)
        async def presentation_page():
            deck = deck_factory()
            viewer = DeckViewer(deck=deck)
            await viewer.build()
        
        if enable_render_frame:
            @ui.page('/_render_frame')
            async def render_frame_page():
                deck = deck_factory()
                viewer = DeckViewer(deck=deck)
                await viewer.build_render_frame()
