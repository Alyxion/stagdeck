# Custom Python Slides

This document describes how to create custom slides using Python by subclassing `Slide` and overriding `build_content()`.

---

## Overview

While markdown is great for text-focused slides, sometimes you need:
- Interactive charts (Plotly, ECharts)
- Dynamic data from APIs or databases
- Custom NiceGUI components (buttons, inputs, progress bars)
- Complex layouts not possible in markdown

StagDeck supports **custom Python slides** by subclassing `Slide` and overriding the `build_content()` method.

---

## Quick Start

```python
from dataclasses import dataclass
from nicegui import ui
from stagdeck.slide import Slide

@dataclass
class MyCustomSlide(Slide):
    """A custom slide with NiceGUI components."""
    
    def __post_init__(self):
        self.title = 'My Custom Slide'
        self.background_color = '#1a1a2e'
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            ui.label('Hello from Python!').classes('text-4xl text-white')
            ui.button('Click me', on_click=lambda: ui.notify('Clicked!'))

# Add to deck
deck.slides.append(MyCustomSlide(name='my_slide'))
```

---

## The `build_content()` Method

Override this async method to build your slide's content:

```python
async def build_content(self, step: int = 0) -> None:
    """Build custom slide content.
    
    :param step: Current animation step (0-based).
    """
    pass
```

### Key Points

- **Async**: The method is `async` to support async NiceGUI operations
- **Step parameter**: Use `step` for multi-step animations
- **Layout helpers**: Use `add_content_area()` and `add_section()` for positioning
- **NiceGUI context**: You're inside a NiceGUI context, so all `ui.*` components work

---

## Layout Helpers

### `add_content_area()`

Creates a centered content container. Use as a context manager:

```python
async def build_content(self, step: int = 0):
    with self.add_content_area():
        ui.label('Centered content')
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `align` | str | `'center'` | Alignment: `'center'`, `'left'`, `'right'`, `'top'`, `'bottom'` |
| `background` | str | `''` | Background color/gradient/image URL |
| `background_modifiers` | str | `''` | Modifiers like `'blur:8 overlay:0.5'` |

**Examples:**

```python
# Left-aligned content
with self.add_content_area(align='left'):
    ui.label('Left-aligned')

# With background
with self.add_content_area(background='#2a2a4e'):
    ui.label('On colored background')

# With image background
with self.add_content_area(background='/media/photo.jpg', background_modifiers='overlay:0.5'):
    ui.label('On image with overlay')
```

### `add_section()`

Creates a positioned section for split layouts:

```python
async def build_content(self, step: int = 0):
    with self.add_section(position='left', background='/media/photo.jpg'):
        pass  # Image fills left half
    with self.add_section(position='right'):
        ui.label('Content on right')
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `position` | str | `''` | Position: `'left'`, `'right'`, `'top'`, `'bottom'`, or `''` for full |
| `background` | str | `''` | Background color/gradient/image URL |
| `background_modifiers` | str | `''` | Modifiers like `'blur:8 overlay:0.5'` |
| `width` | str | `''` | Custom width (e.g., `'60%'`). Defaults based on position |
| `height` | str | `''` | Custom height (e.g., `'40%'`). Defaults based on position |

---

## Slide Properties

Set these in `__post_init__()` to configure the slide:

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Unique slide name for navigation |
| `title` | str | Slide title (rendered at top) |
| `subtitle` | str | Slide subtitle |
| `background_color` | str | Background color, gradient, or `url(/path/to/image.jpg)` |
| `background_position` | str | For split layouts: `'left'`, `'right'`, `'top'`, `'bottom'` |
| `background_modifiers` | str | Image modifiers: `'overlay'`, `'overlay:0.5'`, `'blur'`, `'blur:8'` |
| `steps` | int | Number of animation steps (default: 1) |

---

## Examples

### Interactive Plotly Chart

```python
@dataclass
class ChartSlide(Slide):
    def __post_init__(self):
        self.title = '📊 Sales Dashboard'
        self.background_color = '#1a1a2e'
    
    async def build_content(self, step: int = 0):
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(x=['Q1', 'Q2', 'Q3', 'Q4'], y=[10, 15, 13, 17])
        ])
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        
        with self.add_content_area():
            ui.plotly(fig).classes('w-full').style('height: 400px;')
```

### Split Layout with Progress Bars

```python
@dataclass
class ProgressSlide(Slide):
    def __post_init__(self):
        self.title = 'Project Status'
        self.background_color = 'url(/media/mountain.jpg)'
        self.background_position = 'left'  # Image on left
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            for name, value in [('Frontend', 85), ('Backend', 70), ('Testing', 45)]:
                with ui.row().classes('w-full items-center gap-4'):
                    ui.label(name).classes('w-24 text-white')
                    ui.linear_progress(value=value/100).classes('flex-1')
```

### Full Background with Overlay

```python
@dataclass
class MetricsSlide(Slide):
    def __post_init__(self):
        self.title = 'Live Metrics'
        self.background_color = 'url(/media/stars.jpg)'
        self.background_modifiers = 'overlay:0.6'
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            with ui.row().classes('gap-8'):
                for label, value in [('Users', 1247), ('Requests', 3842)]:
                    with ui.card().classes('bg-white/10 p-6'):
                        ui.label(label).classes('text-white/70')
                        ui.label(str(value)).classes('text-4xl font-bold text-white')
```

### Multi-Step Animation

```python
@dataclass
class AnimatedSlide(Slide):
    def __post_init__(self):
        self.title = 'Step by Step'
        self.background_color = '#1a1a2e'
        self.steps = 3  # Enable 3 steps
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            if step >= 0:
                ui.label('Step 1: Introduction').classes('text-2xl text-white')
            if step >= 1:
                ui.label('Step 2: Details').classes('text-2xl text-green-400 mt-4')
            if step >= 2:
                ui.label('Step 3: Conclusion').classes('text-2xl text-blue-400 mt-4')
```

---

## Adding Custom Slides to a Deck

```python
from stagdeck import SlideDeck, App

def create_deck():
    deck = SlideDeck(title='My Presentation')
    
    # Load markdown slides
    deck.add_from_file('slides.md')
    
    # Append custom Python slides
    deck.slides.append(ChartSlide(name='chart'))
    deck.slides.append(ProgressSlide(name='progress'))
    
    # Or insert at specific position
    # deck.slides.insert(5, MetricsSlide(name='metrics'))
    
    return deck

App.run(create_deck)
```

---

## Best Practices

1. **Use `@dataclass`**: Always decorate custom slides with `@dataclass` for proper initialization
2. **Set properties in `__post_init__()`**: Configure title, background, etc. after dataclass init
3. **Use layout helpers**: Prefer `add_content_area()` over manual positioning
4. **Keep it async**: The `build_content()` method must be `async`
5. **Name your slides**: Always set `name` for navigation and debugging
6. **Match theme colors**: Use colors that complement the theme (dark backgrounds for midnight theme)

---

## Comparison: Markdown vs Python Slides

| Feature | Markdown | Python |
|---------|----------|--------|
| Text content | ✅ Easy | ⚠️ Verbose |
| Images | ✅ Simple syntax | ✅ Full control |
| Tables | ✅ GFM syntax | ⚠️ Manual |
| Code blocks | ✅ Syntax highlighting | ⚠️ Manual |
| Interactive charts | ❌ | ✅ Plotly, ECharts |
| Dynamic data | ❌ | ✅ APIs, databases |
| Custom components | ❌ | ✅ Any NiceGUI component |
| Animations | ⚠️ Build lists only | ✅ Full control |

**Recommendation**: Use markdown for content-focused slides, Python for interactive/dynamic slides.
