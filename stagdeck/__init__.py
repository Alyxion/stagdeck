"""🎬 StagDeck - A NiceGUI-based presentation tool."""

from .slide import Slide
from .slide_deck import SlideDeck
from .viewer import DeckViewer
from .registry import DeckRegistry, registry, register_deck, get_deck
from .theme import Theme, DEFAULT_THEME, ElementStyle, LayoutStyle


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
    'DeckRegistry',
    'registry',
    'register_deck',
    'get_deck',
    'format_duration',
    'Theme',
    'DEFAULT_THEME',
    'ElementStyle',
    'LayoutStyle',
]
