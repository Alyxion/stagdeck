# 🧩 StagDeck Components Reference

A comprehensive guide to slide components, inspired by professional presentation tools.

---

## 1. Text Elements

### 1.1 Headings

| Element | Description | Typical Size | Use Case |
|---------|-------------|--------------|----------|
| `title` | Main slide title | 48-72px | One per slide, primary message |
| `subtitle` | Secondary title | 24-36px | Clarifying text below title |
| `heading1` | Section heading | 36-48px | Major content sections |
| `heading2` | Subsection heading | 28-36px | Sub-topics within sections |
| `heading3` | Minor heading | 24-28px | Detailed breakdowns |

### 1.2 Body Text

| Element | Description | Typical Size | Use Case |
|---------|-------------|--------------|----------|
| `text` | Standard body text | 18-24px | Main content paragraphs |
| `text_small` | Smaller body text | 14-16px | Captions, footnotes |
| `text_large` | Emphasized text | 28-32px | Key statements |
| `quote` | Block quotation | 24-28px | Citations, testimonials |
| `caption` | Image/figure caption | 12-14px | Describing visuals |
| `footnote` | Reference notes | 10-12px | Citations, disclaimers |

### 1.3 Special Text

| Element | Description | Use Case |
|---------|-------------|----------|
| `label` | Short descriptive text | Diagram labels, annotations |
| `badge` | Highlighted tag | Status indicators, categories |
| `tooltip` | Hover information | Additional context |
| `code_inline` | Inline code | Variable names, commands |

---

## 2. Lists

### 2.1 Bullet Lists

| Element | Description | Style |
|---------|-------------|-------|
| `bullet` | Standard bullet point | • or custom icon |
| `bullet_level1` | First level indent | Primary points |
| `bullet_level2` | Second level indent | Sub-points |
| `bullet_level3` | Third level indent | Details |

### 2.2 Numbered Lists

| Element | Description | Style |
|---------|-------------|-------|
| `numbered` | Numbered list item | 1. 2. 3. |
| `numbered_alpha` | Alphabetic list | a. b. c. |
| `numbered_roman` | Roman numerals | i. ii. iii. |

### 2.3 Special Lists

| Element | Description | Use Case |
|---------|-------------|----------|
| `checklist` | Checkbox items | Task lists, requirements |
| `timeline` | Sequential items | Process steps, history |
| `definition` | Term + description | Glossaries, explanations |

---

## 3. Visual Elements

### 3.1 Images

| Element | Description | Use Case |
|---------|-------------|----------|
| `image` | Standard image | Photos, illustrations |
| `image_full` | Full-bleed image | Background, hero images |
| `image_inset` | Framed image | Highlighted visuals |
| `icon` | Small symbolic image | UI elements, decorations |
| `logo` | Brand identity | Headers, footers |
| `avatar` | Person/profile image | Team slides, testimonials |

### 3.2 Shapes

| Element | Description | Use Case |
|---------|-------------|----------|
| `rectangle` | Basic rectangle | Containers, highlights |
| `rounded_rect` | Rounded corners | Cards, buttons |
| `circle` | Perfect circle | Icons, avatars |
| `oval` | Ellipse shape | Decorative elements |
| `line` | Straight line | Dividers, connectors |
| `arrow` | Directional arrow | Flow indicators |
| `callout` | Speech bubble | Annotations, quotes |

### 3.3 Decorative

| Element | Description | Use Case |
|---------|-------------|----------|
| `divider` | Horizontal separator | Section breaks |
| `accent_line` | Colored accent | Title underlines |
| `background_shape` | Large decorative shape | Visual interest |
| `pattern` | Repeating pattern | Subtle backgrounds |

---

## 4. Connection Elements

### 4.1 Lines & Connectors

| Element | Description | Use Case |
|---------|-------------|----------|
| `line` | Straight line | Simple connections |
| `line_dashed` | Dashed line | Secondary connections |
| `line_dotted` | Dotted line | Weak/optional connections |
| `line_thick` | Heavy weight line | Emphasis connections |
| `connector_straight` | Point-to-point line | Direct relationships |
| `connector_elbow` | Right-angle connector | Org charts, flowcharts |
| `connector_curved` | Bezier curve | Smooth flow connections |
| `connector_arc` | Arc connector | Circular layouts |

### 4.2 Arrows

| Element | Description | Use Case |
|---------|-------------|----------|
| `arrow_single` | One-way arrow | Direction, flow |
| `arrow_double` | Two-way arrow | Bidirectional relationship |
| `arrow_block` | Thick block arrow | Process flow, emphasis |
| `arrow_curved` | Curved arrow | Circular references |
| `arrow_bent` | Right-angle arrow | Step connections |
| `arrow_circular` | Looping arrow | Feedback, cycles |

### 4.3 Arrow Heads

| Style | Description | Use Case |
|-------|-------------|----------|
| `triangle` | Standard triangle | Default arrows |
| `stealth` | Sharp stealth | Modern, technical |
| `diamond` | Diamond shape | Relationships |
| `circle` | Circle end | Nodes, endpoints |
| `square` | Square end | Block diagrams |
| `none` | No arrowhead | Plain lines |

### 4.4 Brackets & Braces

| Element | Description | Use Case |
|---------|-------------|----------|
| `bracket_square` | Square bracket [ ] | Grouping items |
| `bracket_round` | Parenthesis ( ) | Optional grouping |
| `brace_curly` | Curly brace { } | Code, sets |
| `brace_horizontal` | Horizontal brace | Spanning multiple items |
| `brace_vertical` | Vertical brace | Grouping rows |

### 4.5 Flow Indicators

| Element | Description | Use Case |
|---------|-------------|----------|
| `flow_arrow` | Large process arrow | Major flow direction |
| `chevron` | Chevron/angle | Sequential steps |
| `chevron_chain` | Connected chevrons | Process pipeline |
| `step_connector` | Numbered step link | Ordered processes |
| `branch` | Splitting connector | Decision points |
| `merge` | Joining connector | Convergence points |

### 4.6 Relationship Lines

| Element | Description | Use Case |
|---------|-------------|----------|
| `association` | Simple line | Basic relationship |
| `dependency` | Dashed arrow | Depends on |
| `inheritance` | Triangle-head line | Parent-child |
| `composition` | Diamond-head line | Contains/owns |
| `aggregation` | Empty diamond line | Has-a relationship |
| `realization` | Dashed triangle | Implements |

### 4.7 Connection Styling

```json
{
  "connector": {
    "stroke": "${primary}",
    "stroke_width": 2,
    "stroke_dasharray": "none",
    "arrow_start": "none",
    "arrow_end": "triangle",
    "arrow_size": 10,
    "curve": "straight",
    "opacity": 1.0
  }
}
```

| Property | Values | Description |
|----------|--------|-------------|
| `stroke` | color | Line color |
| `stroke_width` | number | Line thickness (px) |
| `stroke_dasharray` | none/dashed/dotted | Line style |
| `arrow_start` | none/triangle/diamond/circle | Start marker |
| `arrow_end` | none/triangle/diamond/circle | End marker |
| `arrow_size` | number | Arrowhead size |
| `curve` | straight/elbow/curved/arc | Path type |
| `opacity` | 0.0-1.0 | Transparency |

---

## 5. Data Visualization

### 4.1 Charts

| Element | Description | Use Case |
|---------|-------------|----------|
| `chart_bar` | Bar chart | Comparisons |
| `chart_column` | Column chart | Time series, rankings |
| `chart_line` | Line chart | Trends over time |
| `chart_area` | Area chart | Volume over time |
| `chart_pie` | Pie chart | Part-to-whole |
| `chart_donut` | Donut chart | Part-to-whole with center |
| `chart_scatter` | Scatter plot | Correlations |
| `chart_bubble` | Bubble chart | 3-variable comparison |
| `chart_radar` | Radar/spider chart | Multi-dimensional comparison |
| `chart_gauge` | Gauge/meter | Single metric progress |

### 4.2 Diagrams

| Element | Description | Use Case |
|---------|-------------|----------|
| `flowchart` | Process flow | Workflows, decisions |
| `org_chart` | Organizational hierarchy | Team structure |
| `mind_map` | Radial idea map | Brainstorming, concepts |
| `venn` | Overlapping circles | Relationships, intersections |
| `pyramid` | Layered triangle | Hierarchies, priorities |
| `funnel` | Narrowing stages | Sales process, filtering |
| `cycle` | Circular process | Recurring processes |
| `matrix` | 2x2 or grid layout | Comparisons, quadrants |
| `swimlane` | Parallel processes | Cross-functional workflows |

### 4.3 Infographics

| Element | Description | Use Case |
|---------|-------------|----------|
| `stat_number` | Large statistic | Key metrics |
| `progress_bar` | Horizontal progress | Completion, comparison |
| `progress_ring` | Circular progress | Percentage complete |
| `icon_grid` | Grid of icons | Feature lists |
| `comparison` | Side-by-side | Before/after, vs |
| `timeline_visual` | Visual timeline | History, roadmap |

---

## 5. Tables

| Element | Description | Use Case |
|---------|-------------|----------|
| `table` | Standard data table | Structured data |
| `table_header` | Header row/column | Column/row labels |
| `table_cell` | Data cell | Individual values |
| `table_highlight` | Emphasized cell | Important values |
| `table_total` | Summary row | Totals, averages |

---

## 6. Media Elements

| Element | Description | Use Case |
|---------|-------------|----------|
| `video` | Embedded video | Demos, explanations |
| `audio` | Audio player | Narration, music |
| `iframe` | Embedded content | Web content, apps |
| `animation` | Animated element | Attention, transitions |
| `3d_model` | 3D visualization | Products, architecture |

---

## 7. Interactive Elements

| Element | Description | Use Case |
|---------|-------------|----------|
| `button` | Clickable button | Navigation, actions |
| `link` | Hyperlink | References, navigation |
| `input` | Text input field | Forms, demos |
| `dropdown` | Selection menu | Options, filters |
| `slider` | Value slider | Adjustable parameters |
| `toggle` | On/off switch | Binary options |

---

## 8. Layout Components

### 8.1 Containers

| Element | Description | Use Case |
|---------|-------------|----------|
| `card` | Bordered container | Grouped content |
| `panel` | Background section | Content areas |
| `sidebar` | Side content area | Navigation, notes |
| `footer` | Bottom section | Page numbers, branding |
| `header` | Top section | Titles, navigation |

### 8.2 Grids

| Element | Description | Use Case |
|---------|-------------|----------|
| `grid_2col` | Two columns | Side-by-side content |
| `grid_3col` | Three columns | Feature comparisons |
| `grid_4col` | Four columns | Icon grids, galleries |
| `grid_asymmetric` | Unequal columns | Image + text layouts |

### 8.3 Spacing

| Element | Description | Use Case |
|---------|-------------|----------|
| `spacer` | Empty space | Vertical separation |
| `margin` | Outer spacing | Edge padding |
| `padding` | Inner spacing | Content breathing room |

---

## 9. Code Elements

| Element | Description | Use Case |
|---------|-------------|----------|
| `code_block` | Multi-line code | Code samples |
| `code_inline` | Inline code | Variable names |
| `terminal` | Terminal/console | Command examples |
| `diff` | Code diff view | Changes, comparisons |
| `syntax_highlight` | Colored syntax | Language-specific |

---

## 10. Annotation Elements

| Element | Description | Use Case |
|---------|-------------|----------|
| `callout_box` | Highlighted box | Important notes |
| `warning` | Warning message | Cautions, alerts |
| `info` | Information box | Tips, notes |
| `success` | Success message | Confirmations |
| `error` | Error message | Problems, issues |
| `step_number` | Numbered circle | Process steps |
| `annotation_arrow` | Pointing arrow | Drawing attention |
| `highlight` | Text highlight | Emphasis |

---

## 11. Theme-Specific Styling

Each element can have these style properties defined in the theme:

```json
{
  "element_name": {
    "color": "${text_dark}",
    "size": "${font_size_xl}",
    "weight": "bold",
    "opacity": 1.0,
    "font": "Inter",
    "classes": "tracking-tight",
    "style": "text-shadow: 0 1px 2px rgba(0,0,0,0.1)"
  }
}
```

### Common Style Properties

| Property | Type | Description |
|----------|------|-------------|
| `color` | string | Text/foreground color |
| `background` | string | Background color/gradient |
| `size` | number/string | Font size or dimensions |
| `weight` | string | Font weight (normal, bold, etc.) |
| `opacity` | number | Transparency (0.0 - 1.0) |
| `font` | string | Font family |
| `border` | string | Border style |
| `radius` | number | Border radius |
| `shadow` | string | Box/text shadow |
| `padding` | number/string | Inner spacing |
| `margin` | number/string | Outer spacing |
| `classes` | string | Additional Tailwind classes |
| `style` | string | Additional inline CSS |

---

## 12. Slide Layout Templates

Common slide layouts that combine components:

| Layout | Components | Use Case |
|--------|------------|----------|
| **Title Slide** | title, subtitle, logo | Opening slide |
| **Section Header** | heading1, subtitle | Section dividers |
| **Title + Content** | title, text, bullets | Standard content |
| **Two Column** | title, grid_2col, text | Comparisons |
| **Title + Image** | title, image, caption | Visual focus |
| **Full Image** | image_full, title overlay | Impact slides |
| **Quote Slide** | quote, attribution, avatar | Testimonials |
| **Stats Slide** | stat_number (x3), labels | Key metrics |
| **Comparison** | title, comparison, bullets | Before/after |
| **Timeline** | title, timeline_visual | Process, history |
| **Team Slide** | title, avatar grid, names | Team intros |
| **Chart Slide** | title, chart_*, caption | Data presentation |
| **Code Slide** | title, code_block, text | Technical content |
| **Thank You** | title, contact info, logo | Closing slide |

---

## 13. Implementation Priority

### Phase 1 - Core Text
- [ ] title, subtitle, heading1-3
- [ ] text, text_small, text_large
- [ ] bullet lists (3 levels)
- [ ] numbered lists

### Phase 2 - Visual Basics
- [ ] image, icon, logo
- [ ] card, panel
- [ ] divider, accent_line
- [ ] grid layouts (2-4 col)

### Phase 3 - Data Visualization
- [ ] chart_bar, chart_line, chart_pie
- [ ] stat_number, progress_bar
- [ ] table with styling

### Phase 4 - Diagrams
- [ ] flowchart, org_chart
- [ ] venn, pyramid, funnel
- [ ] timeline_visual

### Phase 5 - Interactive
- [ ] button, link
- [ ] code_block with syntax highlighting
- [ ] callout boxes (info, warning, etc.)

### Phase 6 - Advanced
- [ ] video, iframe
- [ ] animations
- [ ] custom shapes

---

## 10. Content Element Classes (Implemented)

StagDeck provides content element classes for rendering markdown with explicit size control.

### 10.1 Base Class

```python
from stagdeck.components import ContentElement, REM_TO_PX_FACTOR

class ContentElement(ABC):
    """Base class for all content elements."""
    
    def __init__(self, content: str, font_size: float = 1.8):
        self.content = content
        self.font_size = font_size
    
    @property
    def px_size(self) -> float:
        """Convert rem to pixels (rem × 20)."""
        return self.font_size * REM_TO_PX_FACTOR
    
    @abstractmethod
    async def build(self) -> None:
        """Build the content element UI."""
        pass
```

### 10.2 Available Elements

| Class | Purpose | Default Font Size |
|-------|---------|-------------------|
| `TableElement` | Markdown tables | 1.8rem |
| `BulletListElement` | Bullet lists (- or *) | 1.8rem |
| `NumberedListElement` | Numbered lists (1. 2.) | 1.8rem |
| `CodeBlockElement` | Code blocks (```) | 1.4rem |
| `BlockquoteElement` | Blockquotes (>) | 1.8rem |
| `ParagraphElement` | Plain text/paragraphs | 1.8rem |
| `MixedContentElement` | Mixed markdown | 1.8rem |

### 10.3 Usage

```python
from stagdeck.components import TableElement

# Create element
table = TableElement(
    content='| A | B |\n|---|---|\n| 1 | 2 |',
    font_size=2.0,
)

# Build UI (async)
await table.build()
```

### 10.4 Convenience Functions

For simpler usage, async convenience functions are available:

```python
from stagdeck.components import render_table, render_bullet_list

await render_table('| A | B |', font_size=1.8)
await render_bullet_list('- Item 1\n- Item 2', font_size=1.8)
```

### 10.5 File Structure

```
stagdeck/components/content_elements/
├── __init__.py          # Package exports
├── base.py              # ContentElement, ContentStyle, REM_TO_PX_FACTOR
├── table.py             # TableElement
├── bullet_list.py       # BulletListElement
├── numbered_list.py     # NumberedListElement
├── code_block.py        # CodeBlockElement
├── blockquote.py        # BlockquoteElement
├── paragraph.py         # ParagraphElement
└── mixed_content.py     # MixedContentElement
```
