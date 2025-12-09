"""Showcase of slide layouts using the new markdown-first syntax.

This sample demonstrates the Deckset-inspired markdown syntax:
- `# Title` for slide titles
- `## Subtitle` for subtitles
- `![background](#color)` for background colors
- `![background](image.jpg)` for background images
- Everything else is content

Run with: python main.py
"""

from pathlib import Path

from stagdeck import SlideDeck, App


def create_showcase_deck() -> SlideDeck:
    """Create a presentation showcasing the markdown-first syntax."""
    
    deck = SlideDeck(title='StagDeck Showcase')
    
    # Register media folder - images become accessible at /media/filename
    media_dir = Path(__file__).parent / 'media'
    deck.add_media_folder(media_dir, '/media')
    
    # ==========================================================================
    # Title Slide - Using markdown-first syntax
    # ==========================================================================
    deck.add('''
![background](linear-gradient(135deg, #1a1a2e 0%, #16213e 100%))

# StagDeck Showcase
## Beautiful presentations with Python
''')
    
    # ==========================================================================
    # Introduction
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# What is StagDeck?

**StagDeck** is a Python framework for creating presentations.

- 🐍 Pure Python - no HTML/CSS required
- 📝 Markdown support for content
- 🎨 Theming system for consistent styling
- ⌨️ Keyboard navigation
- 🖥️ Fullscreen mode
- 📸 Slide rendering & export
''')
    
    # ==========================================================================
    # Code Block Example
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Simple API

```python
from stagdeck import SlideDeck, App

def create_deck():
    deck = SlideDeck(title='My Talk')
    deck.add(\'''
    # Hello
    
    World!
    \''')
    return deck

App.run(create_deck)
```

That's it! Your presentation is ready.
''')
    
    # ==========================================================================
    # Table Example
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Feature Comparison

| Feature | StagDeck | PowerPoint | Reveal.js |
|---------|----------|------------|-----------|
| Python API | ✅ | ❌ | ❌ |
| Markdown | ✅ | ❌ | ✅ |
| Theming | ✅ | ✅ | ✅ |
| Version Control | ✅ | ❌ | ✅ |
| Live Reload | ✅ | ❌ | ✅ |
| Export to PDF | ✅ | ✅ | ✅ |
''')
    
    # ==========================================================================
    # Media Folder Feature
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Local Media Support

Register a media folder to use local images:

```python
deck.add_media_folder('./media', '/media')
```

Then reference images in markdown:

```markdown
![inline](/media/mountain.jpg)
```
''')
    
    # ==========================================================================
    # Local Image Example
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Local Images

Images from your media folder:

![inline](/media/mountain.jpg)

*Served securely from your local media folder*
''')
    
    # ==========================================================================
    # Background Image (no filter by default)
    # ==========================================================================
    deck.add('''
![background](/media/stars.jpg)

# Background Images
## No Filter by Default

Images display without any filter unless you request one.
''')
    
    # ==========================================================================
    # Background Image with Overlay
    # ==========================================================================
    deck.add('''
![overlay](/media/mountain.jpg)

# With Overlay
## Improves Readability

Use `![overlay]` to add a semi-transparent overlay.
''')
    
    # ==========================================================================
    # Background Image with Blur + Text Shadow
    # ==========================================================================
    deck.add('''
[.title:shadow: 2px 2px 4px rgba(0,0,0,0.8)]
[.subtitle:shadow: 1px 1px 2px rgba(0,0,0,0.6)]
[.text:shadow: 1px 1px 2px rgba(0,0,0,0.5)]
![blur:16](/media/stars.jpg)

# With Blur
## Soft Focus Effect

Use `![blur:16]` for a blur effect. Text has a slight outline for readability.
''')
    
    # ==========================================================================
    # Combined Filters
    # ==========================================================================
    deck.add('''
![blur:4 overlay:0.5](/media/mountain.jpg)

# Combined Filters
## Blur + Overlay

Use `![blur:4 overlay:0.5]` for both effects.
''')
    
    # ==========================================================================
    # Left Split Layout
    # ==========================================================================
    deck.add('''
![left](/media/mountain.jpg)
Test
![right blur:5 overlay:0.5](/media/mountain.jpg)
# Left Image Layout

Content appears on the right side.

- Great for showcasing images
- Text remains readable
- Professional look
''')
    
    # ==========================================================================
    # Right Split Layout
    # ==========================================================================
    deck.add('''
![right](/media/stars.jpg)

# Right Image Layout

Content appears on the left side.

- Alternate your layouts
- Keep presentations dynamic
- Balance visual interest
''')
    
    # ==========================================================================
    # Top Split Layout
    # ==========================================================================
    deck.add('''
![top](/media/mountain.jpg)

# Top Image Layout

Image on top, content below. Great for landscape photos!
''')
    
    # ==========================================================================
    # Bottom Split Layout
    # ==========================================================================
    deck.add('''
![bottom](/media/stars.jpg)

# Bottom Image Layout

Content on top, image below. Perfect for dramatic reveals!
''')
    
    # ==========================================================================
    # Split with Overlay
    # ==========================================================================
    deck.add('''
![left overlay](/media/mountain.jpg)

# Split with Overlay

Use `![left overlay]` to add overlay to split images.

- Useful for busy images
- Improves text contrast
''')
    
    # ==========================================================================
    # Multi-Region: Left + Right
    # ==========================================================================
    deck.add('''
![left](/media/mountain.jpg)
# Mountain View
The majestic peaks rise above the clouds.

![right](/media/stars.jpg)
# Night Sky
Stars illuminate the darkness.
''')
    
    # ==========================================================================
    # Multi-Region: Triple Column
    # ==========================================================================
    deck.add('''
![](/media/mountain.jpg)
# Feature One
- Fast performance
- Easy to use

![](/media/stars.jpg)
# Feature Two
- Beautiful themes
- Markdown support

![](/media/mountain.jpg)
# Feature Three
- Export to PDF
- Live reload
''')
    
    # ==========================================================================
    # Quote Example
    # ==========================================================================
    deck.add('''
![background](linear-gradient(135deg, #0f3460 0%, #16213e 100%))

# Inspiration

> "The best way to predict the future is to invent it."
> 
> — Alan Kay

Great presentations tell stories and inspire action.
''')
    
    # ==========================================================================
    # Code with Multiple Languages
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Multi-Language Support

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
''')
    
    # ==========================================================================
    # Nested Lists
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Project Structure

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
''')
    
    # ==========================================================================
    # Small Table Example
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Quarterly Results

| Quarter | Revenue | Growth |
|---------|---------|--------|
| Q1 2024 | $1.2M | +12% |
| Q2 2024 | $1.5M | +25% |
| Q3 2024 | $1.8M | +20% |
| Q4 2024 | $2.1M | +17% |
''')
    
    # ==========================================================================
    # Large Table Example
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Product Comparison Matrix

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
''')
    
    # ==========================================================================
    # Theming
    # ==========================================================================
    deck.add('''
![background](linear-gradient(135deg, #0f3460 0%, #16213e 100%))

# Theming System

Customize your presentation with themes:

- **Colors**: Primary, secondary, accent palettes
- **Typography**: Fonts, sizes, weights
- **Backgrounds**: Solid colors or gradients
- **Overrides**: Per-slide customization

```python
deck.use_theme('default:midnight.json')
deck.override(palette={'primary': '#ff6b6b'})
```
''')
    
    # ==========================================================================
    # Navigation
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Keyboard Navigation

| Key | Action |
|-----|--------|
| `→` or `Space` | Next slide |
| `←` | Previous slide |
| `↑` / `↓` | Previous / Next step |
| `F` | Toggle fullscreen |
| `Esc` | Exit fullscreen |
| `G` | Go to slide (enter number) |
| `?` | Show help |
''')
    
    # ==========================================================================
    # Rendering & Export
    # ==========================================================================
    deck.add('''
![background](#1a1a2e)

# Rendering & Export

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
''')
    
    # ==========================================================================
    # End Slide
    # ==========================================================================
    deck.add('''
![background](linear-gradient(135deg, #1a1a2e 0%, #16213e 100%))

# Thank You!
## Questions?

**GitHub:** github.com/stagdeck

**Documentation:** stagdeck.readthedocs.io

*Built with ❤️ using NiceGUI*
''')
    
    return deck


if __name__ in {'__main__', '__mp_main__'}:
    App.run(create_showcase_deck, title='StagDeck Showcase')
