"""Showcase of slide layouts using the current StagDeck system.

This sample demonstrates various slide configurations including:
- Title slides
- Content with bullet lists
- Code blocks with syntax highlighting
- Tables
- Images (using Unsplash royalty-free images)
- Quotes

Run with: python main.py
"""

from stagdeck import SlideDeck, App


def create_showcase_deck() -> SlideDeck:
    """Create a presentation showcasing slide capabilities."""
    
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
    # Introduction
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
- 📸 Slide rendering & export
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Code Block Example
    # ==========================================================================
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
    
    # ==========================================================================
    # Table Example
    # ==========================================================================
    deck.add(
        title='Feature Comparison',
        content='''
| Feature | StagDeck | PowerPoint | Reveal.js |
|---------|----------|------------|-----------|
| Python API | ✅ | ❌ | ❌ |
| Markdown | ✅ | ❌ | ✅ |
| Theming | ✅ | ✅ | ✅ |
| Version Control | ✅ | ❌ | ✅ |
| Live Reload | ✅ | ❌ | ✅ |
| Export to PDF | ✅ | ✅ | ✅ |
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Image Example - Using Unsplash (royalty-free, commercial use allowed)
    # ==========================================================================
    deck.add(
        title='Beautiful Imagery',
        content='''
Embed images directly in your slides:

![Mountain landscape](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80)

*Photo from Unsplash - free for commercial use*
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Quote Example
    # ==========================================================================
    deck.add(
        title='Inspiration',
        content='''
> "The best way to predict the future is to invent it."
> 
> — Alan Kay

Great presentations tell stories and inspire action.
''',
        background_color='linear-gradient(135deg, #0f3460 0%, #16213e 100%)',
    )
    
    # ==========================================================================
    # Code with Multiple Languages
    # ==========================================================================
    deck.add(
        title='Multi-Language Support',
        content='''
**JavaScript:**
```javascript
const greet = (name) => `Hello, ${name}!`;
console.log(greet('World'));
```

**SQL:**
```sql
SELECT name, COUNT(*) as count
FROM users
GROUP BY name
ORDER BY count DESC;
```
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Nested Lists
    # ==========================================================================
    deck.add(
        title='Project Structure',
        content='''
Organize your presentations:

- **slides/**
    - `intro.md` - Introduction slides
    - `main.md` - Main content
    - `conclusion.md` - Wrap-up
- **assets/**
    - `images/` - Slide images
    - `diagrams/` - Technical diagrams
- **themes/**
    - `custom.json` - Your brand theme
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Small Table Example
    # ==========================================================================
    deck.add(
        title='Quarterly Results',
        content='''
| Quarter | Revenue | Growth |
|---------|---------|--------|
| Q1 2024 | $1.2M | +12% |
| Q2 2024 | $1.5M | +25% |
| Q3 2024 | $1.8M | +20% |
| Q4 2024 | $2.1M | +17% |
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Large Table Example
    # ==========================================================================
    deck.add(
        title='Product Comparison Matrix',
        content='''
| Feature | Basic | Pro | Enterprise | Ultimate |
|---------|-------|-----|------------|----------|
| Users | 1 | 5 | 50 | Unlimited |
| Storage | 1 GB | 10 GB | 100 GB | 1 TB |
| API Access | ❌ | ✅ | ✅ | ✅ |
| Custom Themes | ❌ | ✅ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ | ✅ |
| SSO Integration | ❌ | ❌ | ✅ | ✅ |
| Custom Domain | ❌ | ❌ | ❌ | ✅ |
| SLA Guarantee | ❌ | ❌ | 99.9% | 99.99% |
| Price/month | Free | $9 | $49 | $199 |
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Theming
    # ==========================================================================
    deck.add(
        title='Theming System',
        content='''
Customize your presentation with themes:

- **Colors**: Primary, secondary, accent palettes
- **Typography**: Fonts, sizes, weights
- **Backgrounds**: Solid colors or gradients
- **Overrides**: Per-slide customization

```python
deck.use_theme('default:midnight.json')
deck.override(palette={'primary': '#ff6b6b'})
```
''',
        background_color='linear-gradient(135deg, #0f3460 0%, #16213e 100%)',
    )
    
    # ==========================================================================
    # Navigation
    # ==========================================================================
    deck.add(
        title='Keyboard Navigation',
        content='''
| Key | Action |
|-----|--------|
| `→` or `Space` | Next slide |
| `←` | Previous slide |
| `↑` / `↓` | Previous / Next step |
| `F` | Toggle fullscreen |
| `Esc` | Exit fullscreen |
| `G` | Go to slide (enter number) |
| `?` | Show help |
''',
        background_color='#1a1a2e',
    )
    
    # ==========================================================================
    # Rendering & Export
    # ==========================================================================
    deck.add(
        title='Rendering & Export',
        content='''
Export your slides programmatically:

```bash
# Single slide as PNG
curl "http://localhost:8080/render?slide=0"

# All slides as ZIP
curl "http://localhost:8080/render/batch"

# Grid overview
curl "http://localhost:8080/render/grid"
```

Perfect for thumbnails, PDFs, and sharing!
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

**Documentation:** stagdeck.readthedocs.io

*Built with ❤️ using NiceGUI*
''',
        background_color='linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    )
    
    return deck


if __name__ in {'__main__', '__mp_main__'}:
    App.run(create_showcase_deck, title='StagDeck Showcase')
