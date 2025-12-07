# Layout System

This document defines how slide layouts work - master slides with hierarchical SlideElements.

---

## Core Concept

**Layouts are slides in a master deck containing named SlideElements.**

Like PowerPoint:
- A **master deck** contains layout slides (title slide, content slide, two-column, etc.)
- Each layout slide contains **SlideElements** - named containers for content
- Elements can **nest** within other elements
- **Order matters** - first element is the base layer (e.g., background)
- **Names are unique** and searchable through the entire hierarchy
- **Styling comes from themes** - elements reference theme styles, not hardcoded values

```
Slide (base class)
  └── MasterSlide
        │   async build(): adds SlideElement("background")
        │
        ├── TitleSlide
        │     async build(): await super + SlideElement("title"), SlideElement("subtitle")
        │
        ├── ContentSlide
        │     async build(): await super + SlideElement("title"), SlideElement("body")
        │
        └── TwoColumnSlide
              async build(): await super + SlideElement("title"), SlideElement("columns")
                                                        ├── SlideElement("left")
                                                        └── SlideElement("right")
```

---

## SlideElement

A `SlideElement` is a NiceGUI component - a padding/margin-less container with a unique name.

```python
from nicegui import ui
from nicegui.element import Element

class SlideElement(Element, component='div'):
    """Named container for slide content. No padding/margin by default."""
    
    def __init__(self, name: str, style: str = '', classes: str = ''):
        super().__init__()
        self.name = name
        self.style_ref = style  # Theme style reference
        self.children_elements: dict[str, 'SlideElement'] = {}
        
        # No padding/margin by default
        base_classes = 'p-0 m-0'
        if classes:
            base_classes = f'{base_classes} {classes}'
        self.classes(base_classes)
        
        # Register with parent SlideElement (uses NiceGUI's context system)
        if self.parent_slot and self.parent_slot.parent:
            parent = self.parent_slot.parent
            if isinstance(parent, SlideElement):
                parent.children_elements[name] = self
    
    def find(self, name: str) -> 'SlideElement | None':
        """Find element by name in this element's hierarchy."""
        if name in self.children_elements:
            return self.children_elements[name]
        # Search recursively in children
        for child in self.children_elements.values():
            found = child.find(name)
            if found:
                return found
        return None
    
    def __getitem__(self, name: str) -> 'SlideElement':
        """Shorthand for find(name)."""
        element = self.find(name)
        if element is None:
            raise KeyError(f"Element '{name}' not found")
        return element
```

### Key Properties

| Property | Description |
|----------|-------------|
| `name` | Unique identifier within parent hierarchy |
| `style_ref` | Reference to theme component style (colors, fonts) |
| `classes` | Tailwind/CSS classes (starts with `p-0 m-0`) |
| `children_elements` | Dict of child elements by name |

### Usage

```python
# Create and nest elements
with SlideElement('root') as root:
    with SlideElement('columns', classes='flex gap-8'):
        with SlideElement('left', style='body_text', classes='flex-1'):
            ui.markdown('Left content')
        with SlideElement('right', style='body_text', classes='flex-1'):
            ui.markdown('Right content')

# Find by name (searches hierarchy from root)
left = root.find('left')
columns = root['columns']  # Shorthand, raises KeyError if not found
```

---

## Defining Layouts (Master Deck)

Layouts are `Slide` subclasses. The `build()` method creates the SlideElement hierarchy.

### The MasterSlide Base Class

All layouts inherit from `MasterSlide` which provides the common background:

```python
from nicegui import ui
from stagdeck import Slide, SlideDeck, SlideElement

class MasterSlide(Slide):
    """Base for all layouts - provides background."""
    
    async def build(self):
        await super().build()
        with SlideElement('background', classes='absolute inset-0'):
            ui.element('div').classes('w-full h-full').style(
                f'background: {self.theme.get("background.color")}'
            )
```

### Example: Title Slide Layout

```python
class TitleSlide(MasterSlide):
    """Title slide with centered title and subtitle."""
    
    async def build(self):
        await super().build()  # Adds background
        
        with SlideElement('title', style='title', classes='text-center mt-[30%]'):
            ui.label(self.data.get('title', '')).classes(
                self.theme.classes('title')
            )
        
        with SlideElement('subtitle', style='subtitle', classes='text-center mt-4'):
            ui.label(self.data.get('subtitle', '')).classes(
                self.theme.classes('subtitle')
            )
```

### Example: Content Slide Layout

```python
class ContentSlide(MasterSlide):
    """Standard content slide with title and body."""
    
    async def build(self):
        await super().build()  # Adds background
        
        with SlideElement('title', style='title', classes='mb-6'):
            ui.label(self.data.get('title', '')).classes(
                self.theme.classes('title')
            )
        
        with SlideElement('body', style='body_text', classes='flex-1'):
            ui.markdown(self.data.get('body', '')).classes(
                self.theme.classes('body_text')
            )
```

### Example: Two-Column Layout

```python
class TwoColumnSlide(MasterSlide):
    """Two columns with title."""
    
    async def build(self):
        await super().build()  # Adds background
        
        with SlideElement('title', style='title', classes='mb-8'):
            ui.label(self.data.get('title', '')).classes(
                self.theme.classes('title')
            )
        
        with SlideElement('columns', classes='flex gap-8 flex-1'):
            with SlideElement('left', style='body_text', classes='flex-1'):
                ui.markdown(self.data.get('left', '')).classes(
                    self.theme.classes('body_text')
                )
            with SlideElement('right', style='body_text', classes='flex-1'):
                ui.markdown(self.data.get('right', '')).classes(
                    self.theme.classes('body_text')
                )
```

### Example: Image with Text Layout

```python
class ImageTextSlide(MasterSlide):
    """Image on left, text on right."""
    
    async def build(self):
        await super().build()  # Adds background
        
        with SlideElement('title', style='title', classes='mb-6'):
            ui.label(self.data.get('title', '')).classes(
                self.theme.classes('title')
            )
        
        with SlideElement('content', classes='flex gap-8 flex-1'):
            with SlideElement('image', classes='w-[60%]'):
                ui.image(self.data.get('image', '')).classes('object-contain')
            
            with SlideElement('text', style='body_text', classes='w-[40%]'):
                ui.markdown(self.data.get('text', '')).classes(
                    self.theme.classes('body_text')
                )
```

---

## Content vs Data

Two distinct concepts:

| Property | Type | Description |
|----------|------|-------------|
| `content` | `str` | Raw input - markdown string |
| `data` | `dict[str, Any]` | Parsed/resolved data for elements |

### Lifecycle

```
1. Slide created with content     →  slide = TitleSlide(content='# Hello\n...')
2. Content parsed into data       →  slide.prepare()  (async)
3. Resources preloaded            →  images downloaded, videos buffered
4. Build called with data ready   →  await slide.build()
5. NiceGUI components rendered    →  ui.label(), ui.image(), etc.
```

### Content (Input)

Raw markdown or text provided by the user:

```python
# Markdown content
deck.add(layout='content', content='''
# Welcome to StagDeck

This is the body text with **markdown**.

- Point one
- Point two
''')

# Or explicit kwargs (converted to data directly)
deck.add(
    layout='title',
    title='Welcome to StagDeck',
    subtitle='Beautiful presentations with Python',
)
```

### Data (Parsed/Resolved)

The `prepare()` method parses content and resolves resources into `data`:

```python
class Slide:
    content: str = ''                    # Raw markdown input
    data: dict[str, Any] = field(default_factory=dict)  # Parsed data
    
    async def prepare(self):
        """Parse content and preload resources. Called before build()."""
        if self.content:
            self.data = self._parse_markdown(self.content)
        
        # Preload images, videos
        for name, value in self.data.items():
            if self._is_image_path(value):
                self.data[name] = await self._preload_image(value)
            elif self._is_video_path(value):
                self.data[name] = await self._preload_video(value)
```

### Data Types

| Key | Value Type | Description |
|-----|------------|-------------|
| `'title'` | `str` | Extracted from `# Heading` |
| `'subtitle'` | `str` | Extracted from `## Heading` |
| `'body'` | `str` | Remaining markdown |
| `'image'` | `bytes` or `Path` | Preloaded image data |
| `'video'` | `Path` | Preloaded video reference |
| `'code'` | `str` | Code block content |
| `'chart'` | `dict` | Chart configuration |

### Accessing Data in Build

```python
class TitleSlide(MasterSlide):
    async def build(self):
        await super().build()
        
        # self.data is the parsed/resolved dict
        title_text = self.data.get('title', '')
        subtitle_text = self.data.get('subtitle', '')
        
        with self.add('title', style='title'):
            ui.label(title_text).classes(self.theme.classes('title'))
        
        with self.add('subtitle', style='subtitle'):
            ui.label(subtitle_text).classes(self.theme.classes('subtitle'))
```

### Markdown Parsing

```python
content = '''
# Welcome

This is the body text.

- Point one
- Point two
'''

# After prepare(), data becomes:
data = {
    'title': 'Welcome',
    'body': 'This is the body text.\n\n- Point one\n- Point two'
}
```

### Direct Data (Skip Parsing)

For explicit element values, pass kwargs directly:

```python
# kwargs go directly to data (no parsing needed)
deck.add(
    layout='image_text',
    title='Our Team',
    image='photos/team.jpg',      # Will be preloaded
    text='Meet the amazing team.',
)
# data = {'title': 'Our Team', 'image': <preloaded>, 'text': 'Meet...'}
```

### Required Data

Layouts can specify required data keys:

```python
class TitleSlide(MasterSlide):
    required_data = ['title']  # subtitle is optional
    
    async def prepare(self):
        await super().prepare()
        for key in self.required_data:
            if key not in self.data:
                raise ValueError(f"Missing required data: {key}")
```

---

### Registering Layouts

```python
master = SlideDeck(title='Master')
master.add(TitleSlide(name='title'))
master.add(ContentSlide(name='content'))
master.add(TwoColumnSlide(name='two_column'))
master.add(ImageTextSlide(name='image_text'))
```

### Inheritance Chain

```
Slide (base)
  └── MasterSlide (adds background)
        ├── TitleSlide (adds title, subtitle)
        ├── ContentSlide (adds title, body)
        ├── TwoColumnSlide (adds title, columns/left/right)
        └── ImageTextSlide (adds title, content/image/text)
```

---

## Using Layouts (Presentation Deck)

### Method 1: Markdown Content

```python
deck = SlideDeck(title='My Talk', master=master)

deck.add(layout='content', content='''
# Introduction

This is the body content with **markdown** support.

- Point one
- Point two
''')
```

**Parser maps markdown to elements:**
- `# Heading` → fills element named `title`
- `## Subheading` → fills element named `subtitle` (if exists)
- Remaining content → fills element named `body` or `content`

### Method 2: Named Elements

```python
deck.add(
    layout='two_column',
    title='Comparison',
    left='**Option A**\n- Fast\n- Simple',
    right='**Option B**\n- Flexible\n- Powerful',
)
```

Keyword arguments match element names in the layout.

### Method 3: Dict Content

```python
deck.add(layout='image_text', content={
    'title': 'Our Team',
    'image': 'photos/team.jpg',
    'text': 'Meet the amazing people behind the product.',
})
```

### Method 4: Builder with Element Access

```python
def build_dashboard(elements):
    """Access elements programmatically."""
    elements['title'].content = 'Q4 Dashboard'
    
    # Access nested elements by name
    with elements['left']:
        ui.echart(options=chart_config)
    
    with elements['right']:
        ui.table(columns=cols, rows=data)

deck.add(layout='two_column', builder=build_dashboard)
```

---

## Theme Integration

SlideElements reference **theme styles**, not hardcoded values.

### Theme Defines Styles

```json
{
  "components": {
    "title": {
      "color": "${text_primary}",
      "size": "64px",
      "weight": "bold",
      "font": "Inter"
    },
    "subtitle": {
      "color": "${text_secondary}",
      "size": "32px",
      "weight": "normal"
    },
    "body_text": {
      "color": "${text_primary}",
      "size": "24px",
      "line_height": "1.6"
    },
    "background": {
      "color": "${bg_primary}",
      "gradient": "linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)"
    }
  }
}
```

### Element References Style

```python
SlideElement(
    name='title',
    style='title',      # ← References theme component 'title'
    classes='text-center',
)
```

The renderer applies theme styles automatically:
1. Look up `style='title'` in theme components
2. Apply color, size, weight, font from theme
3. Apply Tailwind classes for positioning

---

## Rendering Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Presentation   │     │     Layout      │     │     Theme       │
│     Slide       │     │   (from master) │     │    Styles       │
│                 │     │                 │     │                 │
│  content={      │ ──▶ │  SlideElements  │ ──▶ │  colors, fonts  │
│    'title':..   │     │  with names     │     │  sizes          │
│    'body':..    │     │                 │     │                 │
│  }              │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         └──────────────────────┴───────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Rendered     │
                       │     Slide       │
                       └─────────────────┘
```

1. Slide specifies `layout='two_column'` and `content={...}`
2. Layout provides SlideElement hierarchy from master deck
3. Content fills elements by matching names
4. Theme provides styling for each element's `style` reference
5. Renderer creates NiceGUI components with combined styling

---

## Default Layouts

Built-in layouts available in every master deck:

| Layout | Elements | Use Case |
|--------|----------|----------|
| `title` | background, title, subtitle | Opening/section slides |
| `content` | background, title, body | Standard content |
| `two_column` | background, title, columns/left/right | Comparisons |
| `image_left` | background, title, content/image/text | Image + description |
| `image_right` | background, title, content/text/image | Description + image |
| `image_full` | image, title_overlay | Full-bleed image |
| `blank` | background | Custom builder only |

---

## Simplified Slide Definition

With this system, `Slide` becomes simpler:

```python
@dataclass
class Slide:
    name: str = ''
    layout: str = 'content'           # Layout name from master
    content: str | dict = ''          # Markdown OR element name → content dict
    builder: Callable | None = None   # Custom builder (receives elements)
    
    # Theming
    theme_overrides: ThemeOverrides | None = None
    
    # Timing
    steps: int = 1
    step_durations: list[float] | None = None
    transition_duration: float = 0.0
    
    # Metadata
    notes: str = ''
```

No more `title`, `subtitle`, `content` as separate fields - they're element names in the layout.

---

## Implementation Priority

1. **Phase 1**: SlideElement class with hierarchy and find()
2. **Phase 2**: Master deck layout registration
3. **Phase 3**: Content → element mapping
4. **Phase 4**: Markdown parser
5. **Phase 5**: Builder with element access
