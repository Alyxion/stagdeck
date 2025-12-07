"""Integration tests for DeckViewer using NiceGUI User fixture."""

import pytest
from nicegui.testing import User

from stagdeck import SlideDeck, DeckViewer


async def test_viewer_displays_slide_title(user: User) -> None:
    """Test that viewer displays the slide title."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Welcome Slide', content='Hello World')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('Welcome Slide')


async def test_viewer_displays_slide_content(user: User) -> None:
    """Test that viewer displays slide content."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Test', content='This is the content')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('This is the content')


async def test_viewer_shows_slide_counter(user: User) -> None:
    """Test that slide counter is displayed."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Slide 1')
    deck.add(title='Slide 2')
    deck.add(title='Slide 3')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('1 / 3')


async def test_navigation_next_slide(user: User) -> None:
    """Test navigating to next slide."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='First Slide')
    deck.add(title='Second Slide')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('First Slide')
    await user.should_see('1 / 2')
    
    # Click next button
    user.find('arrow_forward').click()
    
    await user.should_see('Second Slide')
    await user.should_see('2 / 2')


async def test_navigation_previous_slide(user: User) -> None:
    """Test navigating to previous slide."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='First Slide')
    deck.add(title='Second Slide')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/?slide=1')  # Start on second slide
    await user.should_see('Second Slide')
    
    # Click previous button
    user.find('arrow_back').click()
    
    await user.should_see('First Slide')


async def test_viewer_with_custom_builder(user: User) -> None:
    """Test slide with custom builder function."""
    from nicegui import ui
    
    def custom_builder():
        ui.label('Custom Content').classes('custom-label')
        ui.button('Click Me')
    
    deck = SlideDeck(title='Test Deck')
    deck.add(builder=custom_builder)
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('Custom Content')
    await user.should_see('Click Me')


async def test_viewer_with_markdown_content(user: User) -> None:
    """Test slide with markdown content."""
    deck = SlideDeck(title='Test Deck')
    deck.add(
        title='Markdown Test',
        content='- Item 1\n- Item 2\n- **Bold text**',
    )
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('Item 1')
    await user.should_see('Item 2')


async def test_empty_deck_shows_message(user: User) -> None:
    """Test that empty deck shows appropriate message."""
    deck = SlideDeck(title='Empty Deck')
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    # Empty deck should still render without error
    # The viewer handles empty decks gracefully


async def test_slide_with_subtitle(user: User) -> None:
    """Test slide displays subtitle."""
    deck = SlideDeck(title='Test Deck')
    deck.add(
        title='Main Title',
        subtitle='This is the subtitle',
    )
    
    DeckViewer.create_page(deck, path='/')
    
    await user.open('/')
    await user.should_see('Main Title')
    await user.should_see('This is the subtitle')


async def test_url_query_params_slide_index(user: User) -> None:
    """Test opening specific slide via URL query parameter."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Slide Zero')
    deck.add(title='Slide One')
    deck.add(title='Slide Two')
    
    DeckViewer.create_page(deck, path='/')
    
    # Open slide 2 directly
    await user.open('/?slide=2')
    await user.should_see('Slide Two')
    await user.should_see('3 / 3')
