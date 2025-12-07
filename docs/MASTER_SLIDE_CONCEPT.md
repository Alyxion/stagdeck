# Master Slide Concept

This document defines the standard slide layouts for presentation decks.

---

## Common Slide Types

Based on PowerPoint and professional presentation tools, these are the essential slide layouts:

### Title & Opening Slides

| Layout | Elements | Use Case |
|--------|----------|----------|
| **Title Slide** | title, subtitle, background | Opening slide, presentation title |
| **Title with Picture** | title, subtitle, image (full/partial) | Visual opening |
| **Section Header** | title, subtitle | Chapter/section dividers |
| **Title Only** | title | Minimal, for custom content |
| **Title and Caption** | title, caption (bottom) | Title with attribution |

### Content Slides

| Layout | Elements | Use Case |
|--------|----------|----------|
| **Title and Content** | title, body | Standard content slide |
| **Two Content** | title, left, right | Side-by-side content |
| **Comparison** | title, left_header, left, right_header, right | Comparing two items |
| **3 Column** | title, col1, col2, col3 | Three-way comparison |
| **Text** | title, body (large area) | Text-heavy content |

### Picture Slides

| Layout | Elements | Use Case |
|--------|----------|----------|
| **Picture** | image (full) | Full-bleed image |
| **Picture with Caption** | image, caption | Image with description |
| **Panoramic Picture with Caption** | image (wide), caption | Wide/cinematic image |
| **Text - 1-Picture** | title, text, image | Text with single image |
| **Text - 3-Pictures** | title, text, image1, image2, image3 | Text with image gallery |
| **Text - 4-Pictures** | title, text, images (2x2 grid) | Text with image grid |
| **Picture only** | image | No text, just image |
| **Divider with Picture** | title, image (diagonal/split) | Section break with visual |

### Special Layouts

| Layout | Elements | Use Case |
|--------|----------|----------|
| **Blank** | (empty) | Custom builder only |
| **Content with Caption** | title, body, caption | Content with footnote |
| **Quote with Caption** | quote, attribution, caption | Testimonials, citations |
| **Name Card** | name, title, image, contact | Speaker/team intro |
| **Video** | video, title (optional) | Video content |
| **End** | title, contact, logo | Closing slide |

### Decorative Variants

| Layout | Elements | Use Case |
|--------|----------|----------|
| **Text - HalfRay** | title, body, decorative shape | Styled content |
| **Text - Ray** | title, body, decorative shape | Styled content |
| **Text - Picture - ColorBar** | title, text, image, color accent | Branded content |
| **Text - Picture - GrayColorBar** | title, text, image, gray accent | Subtle branded |

---

## Element Hierarchy

All layouts inherit from `MasterSlide` which provides the background:

```
Slide (base)
  └── MasterSlide
        │   build(): SlideElement("background")
        │
        ├── TitleSlide
        ├── TitleContentSlide
        ├── TwoContentSlide
        ├── SectionHeaderSlide
        ├── PictureSlide
        ├── ComparisonSlide
        ├── ThreeColumnSlide
        ├── QuoteSlide
        ├── NameCardSlide
        ├── VideoSlide
        ├── BlankSlide
        └── EndSlide
```

---

## Default Deck Implementation

The default deck provides these essential layouts.

### File Structure (One Slide Per File)

```
stagdeck/templates/decks/default/
├── __init__.py           # Exports all layouts
├── master.py             # MasterSlide base class
├── deck.py               # create_default_master() factory
└── slides/
    ├── __init__.py       # Exports all slide classes
    ├── title.py          # TitleSlide
    ├── section.py        # SectionSlide
    ├── content.py        # ContentSlide
    ├── two_column.py     # TwoColumnSlide
    ├── comparison.py     # ComparisonSlide
    ├── three_column.py   # ThreeColumnSlide
    ├── picture.py        # PictureSlide
    ├── picture_caption.py # PictureCaptionSlide
    ├── text_picture.py   # TextPictureSlide
    ├── quote.py          # QuoteSlide
    ├── name_card.py      # NameCardSlide
    ├── blank.py          # BlankSlide
    └── end.py            # EndSlide
```

### Available Layouts

| Layout | File | Elements | Use Case |
|--------|------|----------|----------|
| `title` | title.py | title, subtitle | Opening slide |
| `section` | section.py | title, subtitle | Section divider |
| `content` | content.py | title, body | Standard content |
| `two_column` | two_column.py | title, left, right | Side-by-side |
| `comparison` | comparison.py | title, left_header, left, right_header, right | Compare items |
| `three_column` | three_column.py | title, col1, col2, col3 | Three-way |
| `picture` | picture.py | image | Full-bleed image |
| `picture_caption` | picture_caption.py | image, caption | Image + text |
| `text_picture` | text_picture.py | title, text, image | Text + image |
| `quote` | quote.py | quote, attribution | Testimonials |
| `name_card` | name_card.py | image, name, role, bio | Person intro |
| `blank` | blank.py | (background only) | Custom content |
| `end` | end.py | title, subtitle, contact | Closing slide |

---

## Element Naming Convention

Standard element names used across layouts:

| Element | Description |
|---------|-------------|
| `background` | Full-slide background |
| `title` | Main heading |
| `subtitle` | Secondary heading |
| `body` | Main content area |
| `caption` | Small text (bottom) |
| `left`, `right` | Two-column areas |
| `col1`, `col2`, `col3` | Three-column areas |
| `image` | Primary image |
| `image1`, `image2`, etc. | Multiple images |
| `quote` | Quote text |
| `attribution` | Quote source |
| `name` | Person name |
| `role` | Person title/role |
| `contact` | Contact info |
| `logo` | Brand logo |
| `video` | Video element |

---

## Style References

Each element references a theme style:

| Element | Style Reference |
|---------|-----------------|
| `title` | `title` |
| `subtitle` | `subtitle` |
| `body` | `body_text` |
| `caption` | `caption` |
| `quote` | `quote` |
| `attribution` | `attribution` |
| `name` | `name` |
| `role` | `role` |
