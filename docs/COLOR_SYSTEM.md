# 🎨 StagDeck Color System Analysis

## Base Color Categories

Based on the components defined in COMPONENTS.md, we need the following color categories:

---

## 1. Semantic Colors (8 base colors)

These define the meaning/purpose of colors:

| Variable | Purpose | Example |
|----------|---------|---------|
| `primary` | Brand color, main actions, links | #667eea |
| `secondary` | Supporting brand color | #764ba2 |
| `accent` | Highlights, emphasis, CTAs | #f5576c |
| `success` | Positive states, confirmations | #10b981 |
| `warning` | Cautions, alerts | #f59e0b |
| `error` | Errors, destructive actions | #ef4444 |
| `info` | Information, tips | #3b82f6 |
| `neutral` | Default, unemphasized | #6b7280 |

---

## 2. Text Colors (6 base colors)

| Variable | Purpose | Components |
|----------|---------|------------|
| `text_primary` | Main body text | text, bullet, numbered, definition |
| `text_secondary` | Muted/supporting text | subtitle, caption, footnote, text_small |
| `text_heading` | Headings | title, heading1-3 |
| `text_inverse` | Text on dark backgrounds | (all text on dark layouts) |
| `text_link` | Hyperlinks | link |
| `text_disabled` | Inactive/disabled text | disabled states |

---

## 3. Background Colors (6 base colors)

| Variable | Purpose | Components |
|----------|---------|------------|
| `bg_primary` | Main background | slide background |
| `bg_secondary` | Elevated surfaces | card, panel |
| `bg_tertiary` | Subtle differentiation | table rows, alternating |
| `bg_inverse` | Dark backgrounds | dark layouts |
| `bg_overlay` | Semi-transparent overlays | modals, tooltips |
| `bg_code` | Code block backgrounds | code_block, terminal |

---

## 4. Border Colors (3 base colors)

| Variable | Purpose | Components |
|----------|---------|------------|
| `border_default` | Standard borders | card, panel, table, input |
| `border_strong` | Emphasized borders | focused inputs, selected |
| `border_subtle` | Light separators | divider, grid lines |

---

## 5. Interactive State Colors (derived)

These are typically derived from base colors with opacity/shade adjustments:

| State | Derivation | Components |
|-------|------------|------------|
| `hover` | primary @ 10% opacity | button, link, card |
| `active` | primary @ 20% opacity | button pressed |
| `focus` | primary @ 30% + ring | input, button focus |
| `selected` | primary @ 15% bg | list items, table rows |
| `disabled` | neutral @ 50% opacity | all interactive |

---

## 6. Chart/Data Colors (8 base colors)

For data visualization - should be distinguishable:

| Variable | Purpose |
|----------|---------|
| `chart_1` | First data series |
| `chart_2` | Second data series |
| `chart_3` | Third data series |
| `chart_4` | Fourth data series |
| `chart_5` | Fifth data series |
| `chart_6` | Sixth data series |
| `chart_7` | Seventh data series |
| `chart_8` | Eighth data series |

---

## 7. Connection/Diagram Colors (4 base colors)

| Variable | Purpose | Components |
|----------|---------|------------|
| `connector_default` | Standard lines | line, connector_*, arrow_* |
| `connector_emphasis` | Important connections | highlighted paths |
| `connector_subtle` | Background connections | secondary relationships |
| `connector_negative` | Negative/error flows | error paths |

---

## Total Base Colors: 35

- Semantic: 8
- Text: 6
- Background: 6
- Border: 3
- Chart: 8
- Connector: 4

---

## Component Color Mapping

### Text Elements

| Component | Colors Used |
|-----------|-------------|
| `title` | text_heading |
| `subtitle` | text_secondary |
| `heading1-3` | text_heading |
| `text` | text_primary |
| `text_small` | text_secondary |
| `text_large` | text_primary |
| `quote` | text_primary, border_default (left border) |
| `caption` | text_secondary |
| `footnote` | text_secondary |
| `label` | text_secondary |
| `badge` | bg_secondary, text_primary (or semantic colors) |
| `code_inline` | bg_code, text_primary |

### Lists

| Component | Colors Used |
|-----------|-------------|
| `bullet` | primary (marker), text_primary (text) |
| `bullet_level2-3` | neutral (marker), text_primary (text) |
| `numbered` | primary (number), text_primary (text) |
| `checklist` | success (checked), neutral (unchecked) |
| `timeline` | primary (line), text_primary (text) |
| `definition` | text_heading (term), text_primary (desc) |

### Visual Elements

| Component | Colors Used |
|-----------|-------------|
| `card` | bg_secondary, border_default |
| `panel` | bg_secondary |
| `divider` | border_subtle |
| `accent_line` | primary or accent |
| `callout_box` | bg_secondary, border_default |

### Data Visualization

| Component | Colors Used |
|-----------|-------------|
| `chart_*` | chart_1 through chart_8 |
| `stat_number` | text_heading or accent |
| `progress_bar` | primary (fill), bg_tertiary (track) |
| `progress_ring` | primary (fill), bg_tertiary (track) |
| `table_header` | bg_secondary, text_heading |
| `table_cell` | bg_primary, text_primary |
| `table_highlight` | bg_tertiary or accent @ 10% |

### Diagrams

| Component | Colors Used |
|-----------|-------------|
| `flowchart` | connector_default, bg_secondary (nodes) |
| `org_chart` | connector_default, bg_secondary (nodes) |
| `venn` | chart_1, chart_2, chart_3 @ 50% opacity |
| `pyramid` | gradient from chart_1 to chart_3 |
| `funnel` | gradient from chart_1 to chart_3 |

### Connections

| Component | Colors Used |
|-----------|-------------|
| `line`, `connector_*` | connector_default |
| `arrow_*` | connector_default |
| `bracket_*`, `brace_*` | connector_default |
| `relationship lines` | connector_default, connector_subtle |

### Annotations

| Component | Colors Used |
|-----------|-------------|
| `callout_box` | bg_secondary, border_default |
| `warning` | warning (bg @ 10%), warning (border), text_primary |
| `info` | info (bg @ 10%), info (border), text_primary |
| `success` | success (bg @ 10%), success (border), text_primary |
| `error` | error (bg @ 10%), error (border), text_primary |
| `highlight` | accent @ 30% |
| `step_number` | primary (bg), text_inverse |

### Interactive

| Component | Colors Used |
|-----------|-------------|
| `button` | primary (bg), text_inverse |
| `button_secondary` | bg_secondary, text_primary, border_default |
| `link` | text_link |
| `input` | bg_primary, border_default, text_primary |

### Code

| Component | Colors Used |
|-----------|-------------|
| `code_block` | bg_code, text_primary (+ syntax colors) |
| `terminal` | bg_inverse, text_inverse |

---

## Syntax Highlighting Colors (additional 8)

For code blocks:

| Variable | Purpose |
|----------|---------|
| `syntax_keyword` | Keywords (if, for, class) |
| `syntax_string` | String literals |
| `syntax_number` | Numeric values |
| `syntax_comment` | Comments |
| `syntax_function` | Function names |
| `syntax_variable` | Variables |
| `syntax_operator` | Operators |
| `syntax_type` | Type names |

---

## Summary

### Minimum Required Base Colors: 35 + 8 syntax = 43

But many can be derived:
- Text colors often derive from a base + opacity
- Interactive states derive from primary
- Chart colors can be a generated palette

### Practical Base Colors: ~20 hand-picked + derivations

1. **Brand**: primary, secondary, accent
2. **Semantic**: success, warning, error, info
3. **Neutrals**: 5-shade gray scale (50, 200, 400, 600, 900)
4. **Chart**: 8-color palette (can be generated)
5. **Syntax**: 8 colors (often from a standard theme)
