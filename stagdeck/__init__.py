"""🎬 StagDeck - A NiceGUI-based presentation tool."""

from .slide import Slide
from .slide_deck import SlideDeck
from .viewer import DeckViewer
from .app import App
from .file_watcher import FileWatcher
from .registry import DeckRegistry, registry, register_deck, get_deck
from .theme import Theme, ElementStyle, LayoutStyle
from .renderer import SlideRenderer, setup_render_endpoint


def format_duration(seconds: float) -> str:
    """⏱️ Format duration in seconds to MM:SS or HH:MM:SS string."""
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    return f'{minutes}:{secs:02d}'


__all__ = [
    'Slide',
    'SlideDeck',
    'DeckViewer',
    'App',
    'FileWatcher',
    'DeckRegistry',
    'registry',
    'register_deck',
    'get_deck',
    'format_duration',
    'Theme',
    'ElementStyle',
    'LayoutStyle',
    'SlideRenderer',
    'setup_render_endpoint',
]
