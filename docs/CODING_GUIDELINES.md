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
├── stagdeck/           # 📦 Package source
│   ├── __init__.py     # 🎬 Package exports
│   ├── slide.py        # 🎴 Slide data model
│   ├── slide_deck.py   # 📊 SlideDeck data model
│   ├── viewer.py       # 🖥️ DeckViewer UI component
│   ├── registry.py     # 📋 Deck registry
│   └── static/         # 🎨 Static assets (CSS, images)
├── docs/               # 📚 Documentation
├── tests/              # 🧪 Test files
└── main.py             # 🚀 Demo application
```

## 🏷️ Naming Conventions

- **Classes**: `PascalCase` (e.g., `SlideDeck`, `DeckViewer`)
- **Functions/Methods**: `snake_case` (e.g., `get_slide_by_name`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_WIDTH`)
- **Private members**: `_leading_underscore` (e.g., `_slide_frame`)
- **Slide names**: `snake_case` (e.g., `intro`, `chapter_1`, `conclusion`)

## 🎯 Best Practices

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

- All new features must have tests
- Test files go in `tests/` directory
- Use `pytest` for testing
- Run tests with: `poetry run pytest`

## 📝 Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks
