# 📝 StagDeck Coding Guidelines

## Code Style

### General
- **Line length**: 120 characters maximum
- **Docstring style**: PyCharm/IntelliJ style (reStructuredText)
- **Python version**: 3.12+
- **Type hints**: Required for all public functions and methods

### Docstring Format

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the behavior
    in more detail.
    
    :param param1: Description of param1.
    :param param2: Description of param2.
    :return: Description of return value.
    :raises ValueError: When param1 is empty.
    """
    pass
```

### Class Docstrings

```python
class ExampleClass:
    """
    Brief description of the class.
    
    Longer description if needed.
    
    :ivar attribute1: Description of attribute1.
    :ivar attribute2: Description of attribute2.
    """
    pass
```

## 🎨 CSS, HTML & JavaScript Guidelines

### The Rule
**Inline CSS is fine. Large reusable styles and JS belong in static files.**

### ✅ Allowed

```python
# ✅ GOOD: Inline styles for element-specific styling
ui.label('Hello').style('color: red; font-size: 24px;')

# ✅ GOOD: Dynamic styles based on data
bg_color = slide.background_color or '#ffffff'
ui.element('div').style(f'background-color: {bg_color};')

# ✅ GOOD: Tailwind classes
ui.label('Hello').classes('text-red-500 text-2xl mt-4')

# ✅ GOOD: NiceGUI's built-in styling
ui.label('Hello').props('color="red"')

# ✅ GOOD: Short JavaScript for simple interactions
ui.run_javascript('document.documentElement.requestFullscreen()')
```

### ❌ Not Allowed

```python
# ❌ BAD: Large CSS blocks in Python code
ui.add_head_html('''
    <style>
        .slide-wrapper { display: flex; align-items: center; ... }
        .slide-frame { width: 1920px; height: 1080px; ... }
        /* 50+ more lines */
    </style>
''')

# ❌ BAD: Large JavaScript blocks in Python code
ui.add_head_html('''
    <script>
        function updateSlideScale() {
            // 30+ lines of code
        }
    </script>
''')

# ❌ BAD: add_head_html in deck-specific code (affects entire server!)
# This should only be called once at app startup, not per-deck
ui.add_head_html('<style>.my-style { color: red; }</style>')
```

### Static Files Location

Reusable styles and scripts belong in static files:
- `stagdeck/static/styles.css` - Application-wide CSS
- `stagdeck/static/scaling.js` - Slide scaling logic
- Loaded once at application startup via `DeckViewer._setup_static_assets()`

### Why?

1. **`add_head_html` is global**: It affects ALL clients on the server, not just the current deck
2. **Maintainability**: Large CSS/JS blocks in Python are hard to read and maintain
3. **Reusability**: Static files can be cached and reused
4. **Tooling**: CSS/JS files get proper syntax highlighting and linting

## 📁 Project Structure

```
stagdeck/
├── stagdeck/               # 📦 Package source
│   ├── __init__.py         # 🎬 Package exports
│   ├── slide.py            # 🎴 Slide data model
│   ├── slide_deck.py       # 📊 SlideDeck data model
│   ├── viewer.py           # 🖥️ DeckViewer UI component (entry point)
│   ├── registry.py         # 📋 Deck registry
│   ├── static/             # 🎨 Static assets (CSS, JS)
│   ├── templates/themes/   # 🎨 Theme JSON files
│   ├── theme/              # 🎨 Theme system
│   │   ├── theme.py        # Theme class
│   │   ├── loader.py       # Theme loading with inheritance
│   │   ├── context.py      # ThemeContext and overrides
│   │   └── styles.py       # ElementStyle, LayoutStyle
│   └── utils/              # 🔧 Utilities
│       └── paths.py        # Path security utilities
├── docs/                   # 📚 Documentation
├── tests/                  # 🧪 Test files
│   ├── test_viewer.py      # Integration tests (NiceGUI User fixture)
│   └── theme/              # Theme unit tests
└── main.py                 # 🚀 Demo application
```

## 🏷️ Naming Conventions

- **Classes**: `PascalCase` (e.g., `SlideDeck`, `DeckViewer`)
- **Functions/Methods**: `snake_case` (e.g., `get_slide_by_name`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_WIDTH`)
- **Private members**: `_leading_underscore` (e.g., `_slide_frame`)
- **Slide names**: `snake_case` (e.g., `intro`, `chapter_1`, `conclusion`)

## 🏗️ Architecture Principles

### No Global State

Never use global variables, class-level registries, or module-level mutable state:

```python
# ❌ BAD: Global registry
class SlideElement:
    _registry: dict[str, 'SlideElement'] = {}  # Global state!

# ✅ GOOD: Instance-based hierarchy
class SlideElement:
    def __init__(self, parent: 'SlideElement | None' = None):
        self.children: dict[str, 'SlideElement'] = {}
        if parent:
            parent.children[self.name] = self
```

### Async Build Methods

All `build()` methods must be async:

```python
class MySlide(MasterSlide):
    async def build(self):
        await super().build()
        self.add('title', style='title')
```

### Hot Reload

NiceGUI supports hot reload - code changes are applied automatically without restarting the server. Only restart when:
- Adding new dependencies
- Changing startup configuration
- Modifying static assets (CSS/JS) - requires hard refresh (Cmd+Shift+R)

### Visual Testing

Use the `/render` endpoint to capture slide screenshots for visual verification:
```bash
curl -o slide.png "http://localhost:8080/render?slide=0&width=1920&height=1080&delay=2"
```
This creates a clean PNG without navbar at exact resolution.

Use `/render/grid` for a quick overview of all slides:
```bash
curl -o grid.png "http://localhost:8080/render/grid?cols=4&zoom=0.25"
```

### Slide Scaling (Browser Zoom)

The slide frame uses CSS `transform: scale()` to fit the viewport while maintaining aspect ratio. Critical CSS requirements:

1. **`flex-shrink: 0`** on `.slide-frame` - Prevents flex container from compressing the frame width, which would break aspect ratio at high browser zoom levels.
2. **`overflow: visible`** on `.slide-scaler` - Allows the scaled frame to extend beyond its container before being clipped by the wrapper.
3. **Native dimensions via data attributes** - The JS reads `data-width` and `data-height` to calculate scale, avoiding browser zoom effects on computed styles.

### Entry Point: App

`App` manages application lifecycle; `DeckViewer` renders a deck; `SlideDeck` is the data model.

```python
from stagdeck import SlideDeck, App

def create_deck():
    """Factory function - called per user request."""
    deck = SlideDeck(title='My Talk')
    deck.add(title='Hello')
    return deck

App.run(create_deck)  # Always pass factory, never a pre-created deck

# Multiple pages
App.create_page(create_main_deck, path='/')
App.create_page(create_backup_deck, path='/backup')
ui.run()
```

### Theme & Style System

The styling system has three layers that work together:

```
┌─────────────────────────────────────────────────────────────┐
│  JSON Theme Files                                           │
│  - stagdeck/templates/themes/midnight.json (dark, default)  │
│  - stagdeck/templates/themes/aurora.json (light)            │
│  - Define colors, sizes, weights via palette + slide section│
│  - Support inheritance (midnight extends aurora)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LayoutStyle (Python)                                       │
│  - Loads defaults from midnight.json via get_default_style()│
│  - Contains ElementStyle for title, subtitle, text          │
│  - User styles merge with defaults (color overrides size)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Slide._build_default_content()                             │
│  - Calls style.to_css('title') to get CSS                   │
│  - Applies inline styles to NiceGUI elements                │
└─────────────────────────────────────────────────────────────┘
```

#### JSON Theme Files

Theme files define the visual properties. The `slide` section controls presentation styling:

```json
// stagdeck/templates/themes/midnight.json
{
  "name": "midnight",
  "extends": "aurora.json",
  
  "palette": {
    "heading": "#f8fafc",
    "text": "#e2e8f0",
    "text_faint": "#94a3b8"
  },

  "slide": {
    "background": "${bg}",
    "title": { "color": "${heading}", "size": 80, "weight": "bold" },
    "subtitle": { "color": "${text_faint}", "size": 40 },
    "text": { "color": "${text}", "size": 32 }
  }
}
```

- **`palette`**: Color variables referenced via `${name}` syntax
- **`slide.title/subtitle/text`**: ElementStyle definitions with color, size, weight
- **`extends`**: Inherit from another theme (values merge)

#### ElementStyle

The atomic unit of styling. Contains properties for a single element type:

```python
@dataclass
class ElementStyle:
    color: str = ''           # CSS color value
    size: str | int = ''      # Font size (px number or CSS string like '5rem')
    weight: str = ''          # Font weight ('bold', '600', etc.)
    opacity: float = 1.0      # Opacity 0.0-1.0
    font: str = ''            # Font family
    classes: str = ''         # Tailwind classes (applied alongside CSS)
    css: str = ''             # Additional inline CSS (applied alongside classes)
```

Key methods:
- `apply(element)` → **Preferred**: applies both Tailwind classes AND CSS to a NiceGUI element
- `to_css()` → Get CSS string only
- `to_tailwind()` → Get Tailwind classes only
- `merge(other)` → New ElementStyle with other's values taking precedence

**Important**: `classes` and `css` are additive, not alternatives. Use `apply()` to get both.

#### SlideStyle (replaces LayoutStyle)

Dict-based container for element styles. Supports any element name from the theme JSON:

```python
class SlideStyle:
    name: str                              # Theme name
    background: str                        # Background CSS
    _elements: dict[str, ElementStyle]     # All element styles by name
```

Key methods:
- `from_theme('midnight')` → Load all elements from JSON file
- `get('title')` → Returns ElementStyle merged with defaults
- `get('text.h1')` → Access any element from theme (text, table, chart, etc.)
- `apply('title', ui_element)` → Apply style to NiceGUI element
- `set('custom', ElementStyle(...))` → Add custom element style

Available element names from midnight.json:
- Slide: `title`, `subtitle`, `text`
- Text: `text.h1`, `text.h2`, `text.body`, `text.caption`, `text.link`, etc.
- Lists: `list.bullet`, `list.numbered`, `list.checklist`
- Tables: `table.header`, `table.cell`, `table.row_alt`
- Code: `code.block`, `code.terminal`
- And many more...

#### Style Resolution (Cascade)

When rendering a slide, styles cascade in this order (highest priority first):

1. **Slide's own style** (`slide.style`)
2. **Master layout's style** (`master_slide.style`)
3. **Deck's default_style** (`deck.default_style`)
4. **Global defaults** from `get_default_style()` → midnight.json

```python
# In Slide.get_style():
def get_style(self, master_slide=None, deck=None) -> SlideStyle:
    if self.style is not None:
        return self.style
    if master_slide and master_slide.style:
        return master_slide.style
    if deck and deck.default_style:
        return deck.default_style
    return SlideStyle()  # Empty, will merge with defaults
```

#### Merging Behavior

When you specify only some properties, defaults fill in the rest:

```python
# User specifies only color
user_style = SlideStyle(
    title=ElementStyle(color='#ff0000')  # Only color, no size
)

# get('title') merges with defaults from midnight.json:
# - color: #ff0000 (from user)
# - size: 80 (from midnight.json)
# - weight: bold (from midnight.json)
```

This allows users to customize colors without worrying about sizes.

#### Usage Examples

**No custom styling** (uses midnight.json defaults):
```python
deck = SlideDeck(title='My Talk')
deck.add(title='Hello', subtitle='World')
# Title: #f8fafc, 80px, bold (from midnight.json)
```

**Custom colors only** (sizes from defaults):
```python
from stagdeck.theme import SlideStyle, ElementStyle

my_style = SlideStyle(
    title=ElementStyle(color='#00ff00'),  # Green title
    subtitle=ElementStyle(color='#888888'),
)
deck = SlideDeck(title='My Talk', default_style=my_style)
# Title: #00ff00, 80px, bold (color overridden, size from defaults)
```

**Full custom style**:
```python
my_style = SlideStyle(
    title=ElementStyle(color='#ffffff', size=100, weight='900'),
    subtitle=ElementStyle(color='#cccccc', size=50),
    text=ElementStyle(color='#eeeeee', size=36),
)
deck = SlideDeck(title='My Talk', default_style=my_style)
```

**Load from different theme**:
```python
aurora_style = SlideStyle.from_theme('aurora')  # Light theme
deck = SlideDeck(title='My Talk', default_style=aurora_style)
```

**Using apply() for both CSS and Tailwind**:
```python
style = get_default_style()

# Apply style to a NiceGUI element (uses both classes AND css)
label = ui.label('Hello')
style.apply('title', label)

# Or directly from ElementStyle
style.get('title').apply(label)
```

#### Adding New Themes

1. Create JSON file in `stagdeck/templates/themes/`:
```json
{
  "name": "corporate",
  "extends": "aurora.json",
  "palette": {
    "brand": "#0066cc",
    "heading": "#333333"
  },
  "slide": {
    "title": { "color": "${heading}", "size": 72, "weight": "bold" },
    "subtitle": { "color": "${brand}", "size": 36 },
    "text": { "color": "#444444", "size": 28 }
  }
}
```

2. Use in code:
```python
style = LayoutStyle.from_theme('corporate')
deck = SlideDeck(title='Quarterly Report', default_style=style)
```

See [THEME_CONCEPT.md](THEME_CONCEPT.md) for advanced theme features (variables, computed values, component styling).

## �� Best Practices

### Deck Creation
```python
# ✅ GOOD: Named slides for deep linking
deck.add(name='intro', title='Introduction')
deck.add(name='features', title='Features')

# ❌ BAD: Relying on auto-generated names
deck.add(title='Introduction')  # Gets name 'slide_0'
```

### Custom Builders
```python
# ✅ GOOD: Accept step parameter for multi-step slides
def my_slide(step: int):
    if step >= 0:
        ui.label('First item')
    if step >= 1:
        ui.label('Second item')

deck.add(name='reveal', builder=my_slide, steps=2)

# ✅ GOOD: No-step builder is also fine
def simple_slide():
    ui.label('Simple content')

deck.add(name='simple', builder=simple_slide)
```

## 🧪 Testing

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

### Quick Reference

- **Unit tests**: Pure Python tests for non-UI logic (theme, data structures)
- **Integration tests**: NiceGUI `User` fixture for UI components
- Run tests: `poetry run pytest`
- Run with verbose: `poetry run pytest -v`

### Test Types

```python
# Unit test (no NiceGUI required)
def test_theme_loading():
    theme = Theme.from_reference('default:aurora.json')
    assert theme.name == 'aurora'

# Integration test (uses NiceGUI User fixture)
async def test_viewer_shows_title(user: User) -> None:
    deck = SlideDeck(title='Test')
    deck.add(title='Hello')
    DeckViewer.create_page(deck, path='/')
    await user.open('/')
    await user.should_see('Hello')
```

## 📝 Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks
