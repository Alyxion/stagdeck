# StagDeck Testing Guide

This document describes how to run and write tests for StagDeck.

## Test Types

StagDeck uses two types of tests:

1. **Unit Tests** - Pure Python tests for non-UI logic (theme loading, data structures, utilities)
2. **Integration Tests** - NiceGUI `User` fixture tests for UI components

## Setup

### Dependencies

```bash
poetry add --group dev pytest pytest-asyncio
```

### pytest.ini Configuration

The `pyproject.toml` contains pytest configuration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

For UI integration tests, add the NiceGUI testing plugin:

```toml
addopts = "-p nicegui.testing.user_plugin"
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_slide.py

# Run specific test class
poetry run pytest tests/test_slide.py::TestSlideCreation

# Run theme tests only
poetry run pytest tests/theme/
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_slide.py            # Slide class unit tests
├── test_slide_deck.py       # SlideDeck class unit tests
├── test_registry.py         # DeckRegistry unit tests
└── theme/
    ├── __init__.py
    ├── test_loading.py      # Theme loading and inheritance
    ├── test_context.py      # ThemeContext and overrides
    ├── test_styles.py       # ElementStyle and LayoutStyle
    └── test_slide_deck_theme.py  # SlideDeck theme integration
```

## Writing Unit Tests

Unit tests don't require NiceGUI and test pure Python logic:

```python
"""tests/test_slide.py"""
import pytest
from stagdeck import Slide

class TestSlideCreation:
    def test_create_slide_with_title(self):
        slide = Slide(title='Hello World')
        assert slide.title == 'Hello World'
    
    def test_default_steps(self):
        slide = Slide()
        assert slide.steps == 1
```

## Writing Integration Tests (UI)

For testing UI components, use NiceGUI's `User` fixture. This simulates a browser
without actually running one - tests are fast and don't need Selenium.

### Basic Example

```python
"""tests/test_viewer.py"""
import pytest
from nicegui.testing import User

from stagdeck import SlideDeck, DeckViewer

async def test_viewer_shows_slide_title(user: User) -> None:
    """Test that viewer displays slide title."""
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Welcome Slide')
    
    # Create page with viewer
    DeckViewer.create_page(deck, path='/')
    
    # Open the page
    await user.open('/')
    
    # Assert content is visible
    await user.should_see('Welcome Slide')

async def test_navigation_buttons(user: User) -> None:
    """Test navigation between slides."""
    deck = SlideDeck(title='Test')
    deck.add(title='Slide 1')
    deck.add(title='Slide 2')
    
    DeckViewer.create_page(deck, path='/')
    await user.open('/')
    
    await user.should_see('Slide 1')
    
    # Click next button
    user.find('arrow_forward').click()
    
    await user.should_see('Slide 2')
```

### User Fixture Methods

| Method | Description |
|--------|-------------|
| `await user.open('/')` | Navigate to a page |
| `await user.should_see('text')` | Assert text is visible |
| `await user.should_not_see('text')` | Assert text is not visible |
| `user.find(ui.button)` | Find element by type |
| `user.find('text')` | Find element by text content |
| `user.find(marker='name')` | Find element by marker |
| `.click()` | Click an element |
| `.type('text')` | Type into an input |
| `.trigger('event')` | Trigger an event |

### Testing with Markers

Use markers to identify elements in tests:

```python
# In your component
ui.button('Submit').mark('submit_btn')

# In your test
user.find(marker='submit_btn').click()
```

### Async Execution

All UI tests must be `async` functions. The `asyncio_mode = auto` setting
handles this automatically.

```python
async def test_something(user: User) -> None:
    await user.open('/')
    # ... test code
```

## Theme Tests

Theme tests are unit tests that don't require the UI:

```python
"""tests/theme/test_loading.py"""
import pytest
from stagdeck.theme import Theme

class TestThemeLoading:
    def test_load_aurora_theme(self):
        theme = Theme.from_reference('default:aurora.json')
        assert theme.name == 'aurora'
    
    def test_theme_inheritance(self):
        midnight = Theme.from_reference('default:midnight.json')
        assert midnight.variables['bg'] == '#0f172a'  # Dark background
```

## Fixtures

### conftest.py

```python
"""tests/conftest.py"""
import pytest
from pathlib import Path

@pytest.fixture
def themes_dir() -> Path:
    """Path to built-in themes directory."""
    return Path(__file__).parent.parent / 'stagdeck' / 'templates' / 'themes'

@pytest.fixture
def sample_deck():
    """Create a sample deck for testing."""
    from stagdeck import SlideDeck
    deck = SlideDeck(title='Test Deck')
    deck.add(title='Slide 1', content='Content 1')
    deck.add(title='Slide 2', content='Content 2')
    return deck
```

## Best Practices

1. **Keep unit tests fast** - No UI, no I/O where possible
2. **Use descriptive test names** - `test_slide_with_multiple_steps_calculates_total_duration`
3. **One assertion per test** - Makes failures easier to diagnose
4. **Use fixtures for common setup** - Avoid repetition
5. **Test edge cases** - Empty decks, missing themes, invalid inputs
6. **Use `User` fixture for UI** - Faster than Selenium-based `screen` fixture

## References

- [NiceGUI Testing Documentation](https://nicegui.io/documentation/section_testing)
- [NiceGUI User Fixture](https://nicegui.io/documentation/user)
- [pytest Documentation](https://docs.pytest.org/)
