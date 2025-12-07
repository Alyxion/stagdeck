"""Showcase of slide layouts using the current StagDeck system.

This sample demonstrates various slide configurations.
Run with: python main.py

NOTE: The new layout system (MasterSlide, SlideElement) is still in concept phase.
This sample uses the current working API.
"""

from stagdeck import SlideDeck, App


def create_showcase_deck() -> SlideDeck:
    """Create a presentation showcasing slide capabilities."""
    
    # Use default styling - no custom theme needed
    deck = SlideDeck(title='StagDeck Showcase')
    
    # ==========================================================================
    # Title Slide
    # ==========================================================================
    deck.add(
        title='StagDeck Showcase',
        subtitle='Beautiful presentations with Python',
        background_color='linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    )
    
    # ==========================================================================
    # Content Slides
    # ==========================================================================
    deck.add(
        title='What is StagDeck?',
        content='''
**StagDeck** is a Python framework for creating presentations.

- 🐍 Pure Python - no HTML/CSS required
- 📝 Markdown support for content
- 🎨 Theming system for consistent styling
- ⌨️ Keyboard navigation
- 🖥️ Fullscreen mode
''',
        background_color='#1a1a2e',
    )
    
    deck.add(
        title='Simple API',
        content='''
```python
from stagdeck import SlideDeck, App

def create_deck():
    deck = SlideDeck(title='My Talk')
    deck.add(title='Hello', content='World!')
    return deck

App.run(create_deck)
```

That's it! Your presentation is ready.
''',
        background_color='#1a1a2e',
    )
    
    deck.add(
        title='Markdown Support',
        content='''
Full **markdown** support including:

- **Bold** and *italic* text
- `inline code` and code blocks
- Lists (ordered and unordered)
- [Links](https://github.com)
- And more!
''',
        background_color='#1a1a2e',
    )
    
    deck.add(
        title='Theming',
        content='''
Customize your presentation with themes:

- **Colors**: Primary, secondary, accent
- **Typography**: Fonts, sizes, weights
- **Backgrounds**: Solid colors or gradients
- **Overrides**: Per-slide customization
''',
        background_color='linear-gradient(135deg, #0f3460 0%, #16213e 100%)',
    )
    
    deck.add(
        title='Navigation',
        content='''
Control your presentation:

- **→** Next slide
- **←** Previous slide
- **Space** Next step
- **Shift+Space** Previous step
- **F** Toggle fullscreen
- **Esc** Exit fullscreen
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # End Slide
    # ==========================================================================
    deck.add(
        title='Thank You!',
        subtitle='Questions?',
        content='''
**GitHub:** github.com/stagdeck
''',
        background_color='linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    )
    
    return deck


if __name__ in {'__main__', '__mp_main__'}:
    App.run(create_showcase_deck, title='StagDeck Showcase')
