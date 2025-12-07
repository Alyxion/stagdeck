# 🎨 StagDeck Theme System Concept

## Overview

The theme system provides a flexible, JSON-based styling mechanism with variable support,
basic operators, and computed value caching. It separates design tokens from usage,
enabling consistent styling across presentations.

---

## Goals

1. **Semantic palette naming** - Use semantic names (`bg`, `fg`, `text`, `heading`, `border`) instead of color-specific names (`gray_500`). This enables easy theme switching.

2. **Easy dark theme adaptation** - A dark theme should only need to override the `palette` section. All component definitions reference palette variables, so swapping light ↔ dark is just palette replacement.

3. **Single layout per file** - Each theme file defines one complete visual style. No mixing of layouts within a theme.

4. **Reusable variables** - Define once in `palette`, reference everywhere with `${variable}`.

5. **Component grouping** - Organize by component type (`text`, `list`, `container`, `chart`, etc.) not by property type.

6. **Computed values** - Support basic math operators for derived values (spacing scales, font sizes).

7. **Cached resolution** - Computed values are cached for performance.

8. **Cascading overrides** - Theme values can be overridden at deck or slide level.

---

## Usage

### Deck-Level Theme

```python
from stagdeck import SlideDeck

# Single theme
deck = SlideDeck(title='My Presentation')
deck.use_theme('default:aurora.json')

# Multiple themes (first is primary, others are fallbacks)
deck.use_themes('default:aurora.json', 'default:midnight.json')

# Deck-level overrides (affect all slides)
deck.override('primary', '#ff0000')
deck.override_palette(primary='#ff0000', accent='#00ff00')
```

### Slide-Level Overrides

```python
# Override when adding slide
from stagdeck.theme import overrides

deck.add(
    title='Special Slide',
    theme_overrides=overrides(primary='#ff0000'),
)

# Or chain overrides on existing slide
deck.slides[-1].override('primary', '#ff0000')
deck.slides[-1].override_palette(accent='#00ff00')
```

### Component Property Overrides

Override specific component properties using dot notation:

```python
# Override chart colors for a specific slide
deck.add(
    title='Sales Chart',
    theme_overrides=overrides(**{
        'pie_chart.colors': ['#ff6384', '#36a2eb', '#ffce56'],
        'pie_chart.stroke': '#ffffff',
    }),
)

# Override nested properties
slide.override('bar_chart.axis.color', '#333333')
slide.override('bar_chart.grid.width', 2)

# Override first chart color only (array index)
slide.override('pie_chart.colors.0', '#ff0000')

# Multiple component overrides
slide.override('button.primary.bg', '#0066cc')
slide.override('text.h1.color', '#1a1a1a')
slide.override('container.card.shadow', '0 4px 12px rgba(0,0,0,0.15)')
```

**Dot notation format:** `component.element.property`

| Example | Description |
|---------|-------------|
| `pie_chart.colors` | All chart colors |
| `pie_chart.colors.0` | First chart color |
| `bar_chart.axis.color` | Bar chart axis color |
| `text.h1.color` | Heading 1 text color |
| `button.primary.bg` | Primary button background |
| `container.card.radius` | Card border radius |

### Resolution Order

Theme values resolve in this priority (highest first):
1. Slide-level overrides
2. Deck-level overrides
3. Primary theme
4. Fallback themes (in order)

---

## 1. Structure

### 1.1 Theme File Format (JSON)

```json
{
  "name": "corporate",
  "version": "1.0",
  
  "variables": {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "accent": "#f5576c",
    "text_dark": "#1a1a2e",
    "text_light": "#ffffff",
    "spacing_base": 16,
    "font_size_base": 16,
    "border_radius": 8
  },
  
  "computed": {
    "primary_gradient": "linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)",
    "spacing_sm": "${spacing_base} * 0.5",
    "spacing_lg": "${spacing_base} * 2",
    "font_size_sm": "${font_size_base} * 0.875",
    "font_size_lg": "${font_size_base} * 1.25",
    "font_size_xl": "${font_size_base} * 1.5",
    "font_size_2xl": "${font_size_base} * 2",
    "font_size_6xl": "${font_size_base} * 4"
  },
  
  "layouts": {
    "title": {
      "background": "${primary_gradient}",
      "title": { "color": "${text_light}", "size": "${font_size_6xl}" },
      "subtitle": { "color": "${text_light}", "opacity": 0.8 },
      "text": { "color": "${text_light}" }
    },
    "content": {
      "background": "#f8fafc",
      "title": { "color": "${text_dark}", "size": "${font_size_6xl}" },
      "subtitle": { "color": "${text_dark}", "opacity": 0.6 },
      "text": { "color": "${text_dark}" }
    },
    "code": {
      "background": "linear-gradient(135deg, #f093fb 0%, ${accent} 100%)",
      "title": { "color": "${text_light}" },
      "code_bg": "rgba(0,0,0,0.2)",
      "code_text": "${text_light}"
    }
  }
}
```

### 1.2 Variable Reference Syntax

- `${variable_name}` - Reference a variable or computed value
- Variables resolve recursively (computed can reference other computed)
- Circular references are detected and raise an error

### 1.3 Operator Support (Safe Evaluation)

Supported operators for numeric values:
- `+` Addition
- `-` Subtraction  
- `*` Multiplication
- `/` Division
- `%` Modulo
- `( )` Grouping

Examples:
```json
{
  "spacing_lg": "${spacing_base} * 2",
  "padding": "(${spacing_base} + 4) * 1.5",
  "width": "${base_width} - ${margin} * 2"
}
```

**No Python eval()** - Uses a safe tokenizer and evaluator.

---

## 2. Python API

### 2.1 Theme Class

```python
@dataclass
class Theme:
    """🎨 Theme definition with variables, computed values, and layouts."""
    
    name: str
    variables: dict[str, str | int | float]
    computed: dict[str, str]
    layouts: dict[str, LayoutStyle]
    
    _cache: dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_json(cls, path: str | Path) -> 'Theme':
        """Load theme from JSON file."""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Theme':
        """Create theme from dictionary."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a resolved value (variable, computed, or nested path)."""
    
    def resolve(self, value: str) -> str | int | float:
        """Resolve a value with variable substitution and operators."""
    
    def get_layout(self, name: str) -> 'LayoutStyle':
        """Get a layout style by name."""
    
    def clear_cache(self) -> None:
        """Clear the computed value cache."""
```

### 2.2 LayoutStyle Class

```python
@dataclass
class LayoutStyle:
    """🖼️ Style definitions for a specific layout."""
    
    background: str = ''
    title: ElementStyle = field(default_factory=ElementStyle)
    subtitle: ElementStyle = field(default_factory=ElementStyle)
    text: ElementStyle = field(default_factory=ElementStyle)
    heading: ElementStyle = field(default_factory=ElementStyle)
    link: ElementStyle = field(default_factory=ElementStyle)
    code_bg: str = ''
    code_text: str = ''
    bullet: ElementStyle = field(default_factory=ElementStyle)
    accent: str = ''
    
    def to_tailwind(self, element: str) -> str:
        """Convert element style to Tailwind classes."""
    
    def to_css(self, element: str) -> str:
        """Convert element style to inline CSS."""
```

### 2.3 ElementStyle Class

```python
@dataclass  
class ElementStyle:
    """🎯 Style for a specific element type."""
    
    color: str = ''
    size: str | int | float = ''
    weight: str = ''
    opacity: float = 1.0
    classes: str = ''  # Additional Tailwind classes
    
    def to_tailwind(self) -> str:
        """Convert to Tailwind classes."""
    
    def to_css(self) -> str:
        """Convert to inline CSS."""
```

---

## 3. Safe Expression Evaluator

### 3.1 Tokenizer

```python
class ExpressionTokenizer:
    """Tokenize mathematical expressions safely."""
    
    TOKENS = {
        'NUMBER': r'\d+\.?\d*',
        'VARIABLE': r'\$\{[\w_]+\}',
        'OPERATOR': r'[+\-*/%]',
        'LPAREN': r'\(',
        'RPAREN': r'\)',
        'WHITESPACE': r'\s+',
    }
```

### 3.2 Evaluator

```python
class SafeExpressionEvaluator:
    """Evaluate expressions without using eval()."""
    
    def evaluate(self, expression: str, variables: dict) -> int | float | str:
        """
        Evaluate expression with variable substitution.
        
        - If expression contains only string interpolation, return string
        - If expression is numeric with operators, compute result
        - Raises ValueError for invalid expressions
        """
```

---

## 4. Caching Strategy

### 4.1 Cache Keys

- Variables: `var:{name}`
- Computed: `computed:{name}`
- Layout styles: `layout:{name}:{element}`
- Resolved expressions: `expr:{hash(expression)}`

### 4.2 Cache Invalidation

- `clear_cache()` - Manual full clear
- Automatic clear on variable/computed modification
- LRU eviction for expression cache (max 1000 entries)

---

## 5. Future: Markdown Override Syntax

For inline theme overrides in slide content (to be implemented later):

```markdown
# My Slide {.title color="${accent}"}

Some text with {.highlight bg="${primary}" color="white"}highlighted{/} words.

:::box padding="${spacing_lg}" bg="${secondary}"
Boxed content with theme variables
:::
```

---

## 6. Usage Examples

### 6.1 Loading a Theme

```python
from stagdeck import Theme

# From JSON file
theme = Theme.from_json('themes/corporate.json')

# From dict (inline)
theme = Theme.from_dict({
    'name': 'minimal',
    'variables': {'primary': '#000000'},
    'layouts': {...}
})
```

### 6.2 Using in Slides

```python
# Theme attached to master deck
master = SlideDeck(title='Master', theme=theme)

# Layout inherits theme
master.add(name='title', builder=title_builder)  # Uses theme.layouts['title']

# Slide accesses resolved values
def my_builder(step: int, slide: Slide):
    colors = slide.get_colors()  # From theme
    ui.label('Hello').classes(colors.title.to_tailwind())
```

### 6.3 Accessing Values

```python
# Get resolved variable
primary = theme.get('primary')  # '#667eea'

# Get computed value (cached)
gradient = theme.get('primary_gradient')  # 'linear-gradient(...)'

# Get layout element style
title_color = theme.get('layouts.title.title.color')  # '#ffffff'

# Get as Tailwind
title_tw = theme.get_layout('title').title.to_tailwind()  # 'text-white'
```

---

## 7. Implementation Priority

1. **Phase 1**: Core Theme class with JSON loading, variables, basic resolution
2. **Phase 2**: Safe expression evaluator with operators
3. **Phase 3**: Caching layer
4. **Phase 4**: LayoutStyle and ElementStyle with Tailwind/CSS conversion
5. **Phase 5**: Integration with Slide and SlideDeck
6. **Phase 6**: Markdown override syntax (future)

---

## 8. File Structure

```
stagdeck/
├── theme/
│   ├── __init__.py          # Exports
│   ├── theme.py             # Theme class
│   ├── layout_style.py      # LayoutStyle, ElementStyle
│   ├── evaluator.py         # SafeExpressionEvaluator
│   └── cache.py             # CacheManager
└── themes/
    ├── default.json
    ├── dark.json
    └── corporate.json
```
