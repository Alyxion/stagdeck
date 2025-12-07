"""🚀 App - Application lifecycle management for StagDeck."""

from typing import Callable

from nicegui import ui

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
        def presentation_page():
            deck = deck_factory()
            viewer = DeckViewer(deck=deck)
            viewer.build()
        
        # Render-only page (no navbar, for screenshot capture)
        @ui.page('/_render_frame')
        def render_frame_page():
            deck = deck_factory()
            viewer = DeckViewer(deck=deck)
            viewer.build_render_frame()
        
        if enable_render:
            from .renderer import setup_render_endpoint
            setup_render_endpoint(path=render_path)
        
        ui.run(title=title, show=kwargs.pop('show', False), **kwargs)
    
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
        def presentation_page():
            deck = deck_factory()
            viewer = DeckViewer(deck=deck)
            viewer.build()
        
        if enable_render_frame:
            @ui.page('/_render_frame')
            def render_frame_page():
                deck = deck_factory()
                viewer = DeckViewer(deck=deck)
                viewer.build_render_frame()
