"""📋 Deck registry for managing multiple presentation decks."""

from typing import Callable

from .slide_deck import SlideDeck


class DeckRegistry:
    """📋 Central registry for managing multiple presentation decks.
    
    Allows registering multiple decks and switching between them via URL.
    
    Attributes:
        _decks: Dictionary mapping deck names to deck factories.
        _default: Name of the default deck.
    """
    
    _instance: 'DeckRegistry | None' = None
    
    def __init__(self) -> None:
        self._decks: dict[str, Callable[[], SlideDeck]] = {}
        self._default: str = ''
    
    @classmethod
    def get_instance(cls) -> 'DeckRegistry':
        """🔍 Get the singleton registry instance."""
        if cls._instance is None:
            cls._instance = DeckRegistry()
        return cls._instance
    
    def register(
        self,
        name: str,
        factory: Callable[[], SlideDeck],
        default: bool = False,
    ) -> 'DeckRegistry':
        """➕ Register a deck factory.
        
        Args:
            name: Unique name for the deck.
            factory: Callable that creates and returns a SlideDeck.
            default: If True, set this as the default deck.
            
        Returns:
            Self for chaining.
        """
        self._decks[name] = factory
        if default or not self._default:
            self._default = name
        return self
    
    def get(self, name: str | None = None) -> SlideDeck | None:
        """🔍 Get a deck by name.
        
        Args:
            name: Deck name, or None to get the default deck.
            
        Returns:
            The SlideDeck instance, or None if not found.
        """
        deck_name = name if name else self._default
        factory = self._decks.get(deck_name)
        if factory is None:
            return None
        return factory()
    
    def get_default(self) -> SlideDeck | None:
        """Get the default deck."""
        return self.get(self._default)
    
    @property
    def default_name(self) -> str:
        """Get the name of the default deck."""
        return self._default
    
    @default_name.setter
    def default_name(self, name: str) -> None:
        """Set the default deck name."""
        if name in self._decks:
            self._default = name
    
    @property
    def deck_names(self) -> list[str]:
        """Get list of all registered deck names."""
        return list(self._decks.keys())
    
    def has(self, name: str) -> bool:
        """Check if a deck is registered."""
        return name in self._decks
    
    def clear(self) -> None:
        """Clear all registered decks."""
        self._decks.clear()
        self._default = ''


# Global registry instance
registry = DeckRegistry.get_instance()


def register_deck(
    name: str,
    factory: Callable[[], SlideDeck],
    default: bool = False,
) -> None:
    """Register a deck factory in the global registry.
    
    Args:
        name: Unique name for the deck.
        factory: Callable that creates and returns a SlideDeck.
        default: If True, set this as the default deck.
    """
    registry.register(name, factory, default)


def get_deck(name: str | None = None) -> SlideDeck | None:
    """Get a deck from the global registry.
    
    Args:
        name: Deck name, or None to get the default deck.
        
    Returns:
        The SlideDeck instance, or None if not found.
    """
    return registry.get(name)
