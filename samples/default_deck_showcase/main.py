"""Showcase of slide layouts using markdown file + Python hybrid approach.

This sample demonstrates:
- Loading slides from a markdown file with `add_from_file()`
- Named slides using `[name: slidename]` directive
- Inserting Python slides with `insert(before='name')` or `insert(after='name')`
- Replacing placeholder slides with `replace('name', ...)`

Run with: python main.py
"""

from pathlib import Path

from stagdeck import SlideDeck, App


def create_showcase_deck() -> SlideDeck:
    """Create a presentation from markdown file with Python enhancements."""
    
    deck = SlideDeck(title='StagDeck Showcase')
    
    # Register media folder - images become accessible at /media/filename
    media_dir = Path(__file__).parent / 'media'
    deck.add_media_folder(media_dir, '/media')
    
    # Load all slides from markdown file
    # Each slide can have [name: slidename] for later reference
    slides_file = Path(__file__).parent / 'slides.md'
    deck.add_from_file(slides_file)
    
    # Example: Insert a Python-generated slide after 'comparison'
    # deck.insert('''
    # # Dynamic Slide
    # This was inserted via Python!
    # ''', after='comparison')
    
    # Example: Replace a placeholder slide with custom builder
    # deck.replace('chart_placeholder', builder=my_chart_builder)
    
    return deck


# Example custom builder for dynamic slides
def my_chart_builder(slide):
    """Example builder that could render a dynamic chart."""
    from nicegui import ui
    ui.label('Dynamic Chart Would Go Here')


if __name__ in {'__main__', '__mp_main__'}:
    App.run(create_showcase_deck, title='StagDeck Showcase')
