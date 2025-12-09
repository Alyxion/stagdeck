"""Tests for MarkdownParser."""

import pytest

from stagdeck.components import (
    MarkdownParser,
    MarkdownDeckInfo,
    MarkdownSlideInfo,
    SlideContentType,
)


class TestMarkdownParserBasic:
    """Test basic parsing functionality."""
    
    def test_empty_source(self):
        """Parse empty source."""
        parser = MarkdownParser()
        deck_info, slides = parser.parse('')
        
        assert deck_info.title == ''
        assert slides == []
    
    def test_single_slide(self):
        """Parse single slide with title."""
        parser = MarkdownParser()
        deck_info, slides = parser.parse('# Hello World')
        
        assert len(slides) == 1
        assert slides[0].title == 'Hello World'
    
    def test_multiple_slides_separator(self):
        """Parse multiple slides with --- separator."""
        source = '''# Slide One

Content for slide one.

---

# Slide Two

Content for slide two.
'''
        parser = MarkdownParser()
        deck_info, slides = parser.parse(source)
        
        assert len(slides) == 2
        assert slides[0].title == 'Slide One'
        assert slides[1].title == 'Slide Two'
    
    def test_headers_as_slides(self):
        """Parse with headers as slide boundaries."""
        source = '''# First Slide

Content one.

# Second Slide

Content two.
'''
        parser = MarkdownParser(headers_as_slides=True)
        deck_info, slides = parser.parse(source)
        
        assert len(slides) == 2
        assert slides[0].title == 'First Slide'
        assert slides[1].title == 'Second Slide'


class TestFrontmatter:
    """Test frontmatter parsing."""
    
    def test_basic_frontmatter(self):
        """Parse YAML frontmatter."""
        source = '''---
title: My Presentation
author: John Doe
theme: midnight
---

# First Slide
'''
        parser = MarkdownParser()
        deck_info, slides = parser.parse(source)
        
        assert deck_info.title == 'My Presentation'
        assert deck_info.author == 'John Doe'
        assert deck_info.theme == 'midnight'
    
    def test_frontmatter_with_options(self):
        """Parse frontmatter with boolean options."""
        source = '''---
slidenumbers: true
build-lists: true
aspect-ratio: 4:3
---

# Slide
'''
        parser = MarkdownParser()
        deck_info, slides = parser.parse(source)
        
        assert deck_info.slide_numbers is True
        assert deck_info.build_lists is True
        assert deck_info.aspect_ratio == '4:3'
    
    def test_title_from_first_slide(self):
        """Infer deck title from first slide if not in frontmatter."""
        source = '''# Welcome to My Talk

Introduction content.
'''
        parser = MarkdownParser()
        deck_info, slides = parser.parse(source)
        
        assert deck_info.title == 'Welcome to My Talk'


class TestSlideContent:
    """Test slide content extraction."""
    
    def test_title_and_subtitle(self):
        """Extract title and subtitle."""
        source = '''# Main Title

## Subtitle Here

Body content.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].title == 'Main Title'
        assert slides[0].subtitle == 'Subtitle Here'
    
    def test_code_blocks(self):
        """Extract code blocks with language."""
        source = '''# Code Example

```python
def hello():
    print("Hello")
```
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].code_blocks) == 1
        lang, code = slides[0].code_blocks[0]
        assert lang == 'python'
        assert 'def hello()' in code
    
    def test_multiple_code_blocks(self):
        """Extract multiple code blocks."""
        source = '''# Multi-Language

```javascript
console.log("JS");
```

```sql
SELECT * FROM users;
```
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].code_blocks) == 2
        assert slides[0].code_blocks[0][0] == 'javascript'
        assert slides[0].code_blocks[1][0] == 'sql'
    
    def test_bullet_list(self):
        """Extract bullet list items."""
        source = '''# Features

- First item
- Second item
- Third item
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].bullets) == 3
        assert 'First item' in slides[0].bullets
    
    def test_table(self):
        """Extract table data."""
        source = '''# Comparison

| Name | Value |
|------|-------|
| A | 1 |
| B | 2 |
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].tables) == 1
        table = slides[0].tables[0]
        assert table['headers'] == ['Name', 'Value']
        assert len(table['rows']) == 2
    
    def test_image(self):
        """Extract image references."""
        source = '''# Gallery

![Alt text](https://example.com/image.png)
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].images) == 1
        assert slides[0].images[0]['url'] == 'https://example.com/image.png'
        assert slides[0].images[0]['alt'] == 'Alt text'
    
    def test_blockquote(self):
        """Extract blockquotes."""
        source = '''# Quote

> This is a famous quote.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert len(slides[0].quotes) == 1
        assert 'famous quote' in slides[0].quotes[0]


class TestPresenterNotes:
    """Test presenter notes extraction."""
    
    def test_caret_notes(self):
        """Extract notes with ^ prefix."""
        source = '''# My Slide

Visible content.

^ This is a presenter note.
^ Another note.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert 'presenter note' in slides[0].presenter_notes
        assert 'Another note' in slides[0].presenter_notes
    
    def test_notes_not_in_content(self):
        """Presenter notes should not appear in content."""
        source = '''# Slide

^ Secret note.

Visible text.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert 'Secret' not in slides[0].content
        assert 'Secret' in slides[0].presenter_notes


class TestContentTypeDetection:
    """Test automatic content type detection."""
    
    def test_title_only(self):
        """Detect title-only slide."""
        source = '# Just a Title'
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE
    
    def test_title_subtitle(self):
        """Detect title with subtitle."""
        source = '''# Main Title

## Subtitle
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE_SUBTITLE
    
    def test_title_code(self):
        """Detect title with code block."""
        source = '''# Code Demo

```python
print("hello")
```
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE_CODE
    
    def test_title_table(self):
        """Detect title with table."""
        source = '''# Data

| A | B |
|---|---|
| 1 | 2 |
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE_TABLE
    
    def test_title_image(self):
        """Detect title with image."""
        source = '''# Photo

![](image.png)
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE_IMAGE
    
    def test_title_bullets(self):
        """Detect title with bullet list."""
        source = '''# Points

- One
- Two
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].content_type == SlideContentType.TITLE_BULLETS


class TestSlideDirectives:
    """Test per-slide directives."""
    
    def test_background_directive(self):
        """Parse background directive."""
        source = '''# Slide

[.background: #ff0000]

Content here.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert slides[0].background == '#ff0000'
    
    def test_class_directive(self):
        """Parse class directive."""
        source = '''# Slide

[.class: centered large]

Content.
'''
        parser = MarkdownParser()
        _, slides = parser.parse(source)
        
        assert 'centered' in slides[0].classes
        assert 'large' in slides[0].classes


class TestParseSlideMarkdown:
    """Test parse_slide_markdown method for single-slide parsing."""
    
    def test_title_only(self):
        """Parse slide with just a title."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('# Hello World')
        
        assert result['title'] == 'Hello World'
        assert result['subtitle'] == ''
        assert result['content'] == ''
        assert result['background'] == ''
    
    def test_title_and_subtitle(self):
        """Parse slide with title and subtitle."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
# Main Title
## Subtitle Here
''')
        assert result['title'] == 'Main Title'
        assert result['subtitle'] == 'Subtitle Here'
        assert result['content'] == ''
    
    def test_title_subtitle_content(self):
        """Parse slide with title, subtitle, and content."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
# My Title
## My Subtitle

This is the content.

- Bullet 1
- Bullet 2
''')
        assert result['title'] == 'My Title'
        assert result['subtitle'] == 'My Subtitle'
        assert 'This is the content.' in result['content']
        assert '- Bullet 1' in result['content']
    
    def test_background_color(self):
        """Parse slide with background color."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![background](#1a1a2e)

# Title
''')
        assert result['background'] == '#1a1a2e'
        assert result['title'] == 'Title'
    
    def test_background_gradient(self):
        """Parse slide with gradient background."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![background](linear-gradient(135deg, #1a1a2e 0%, #16213e 100%))

# Title
''')
        assert 'linear-gradient' in result['background']
        assert result['title'] == 'Title'
    
    def test_background_image(self):
        """Parse slide with background image."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![background](image.jpg)

# Title
''')
        assert result['background'] == 'url(image.jpg)'
        assert result['title'] == 'Title'
    
    def test_implicit_background_image(self):
        """Parse slide with image at start (implicit background)."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![](hero.jpg)

# Title
''')
        assert result['background'] == 'url(hero.jpg)'
        assert result['title'] == 'Title'
    
    def test_presenter_notes(self):
        """Parse slide with presenter notes."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
# Title

Content here.

^ This is a presenter note.
^ Another note.
''')
        assert result['title'] == 'Title'
        assert 'This is a presenter note.' in result['notes']
        assert 'Another note.' in result['notes']
        assert '^' not in result['content']
    
    def test_content_only(self):
        """Parse slide with content but no title."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
Just some content here.

- Item 1
- Item 2
''')
        assert result['title'] == ''
        assert 'Just some content here.' in result['content']
        assert '- Item 1' in result['content']
    
    def test_full_slide(self):
        """Parse a complete slide with all elements."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![background](#1a1a2e)

# What is StagDeck?
## A Python Presentation Framework

**StagDeck** is a Python framework for creating presentations.

- Pure Python - no HTML/CSS required
- Markdown support for content
- Theming system

^ Remember to demo the live reload feature.
''')
        assert result['background'] == '#1a1a2e'
        assert result['title'] == 'What is StagDeck?'
        assert result['subtitle'] == 'A Python Presentation Framework'
        assert '**StagDeck**' in result['content']
        assert '- Pure Python' in result['content']
        assert 'Remember to demo' in result['notes']
    
    def test_no_filter_by_default(self):
        """No filters applied by default."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![background](image.jpg)

# Title
''')
        assert result['overlay_opacity'] is None
        assert result['blur_radius'] is None
    
    def test_overlay_modifier(self):
        """Using 'overlay' modifier sets default overlay."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![overlay](image.jpg)

# Title
''')
        assert result['overlay_opacity'] == -1.0  # Sentinel for theme default
        assert result['blur_radius'] is None
    
    def test_overlay_with_value(self):
        """Using 'overlay:N' sets specific opacity."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![overlay:0.6](image.jpg)

# Title
''')
        assert result['overlay_opacity'] == 0.6
        assert result['blur_radius'] is None
    
    def test_blur_modifier(self):
        """Using 'blur' modifier sets default blur."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![blur](image.jpg)

# Title
''')
        assert result['blur_radius'] == -1.0  # Sentinel for theme default
        assert result['overlay_opacity'] is None
    
    def test_blur_with_value(self):
        """Using 'blur:N' sets specific radius."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![blur:8](image.jpg)

# Title
''')
        assert result['blur_radius'] == 8.0
        assert result['overlay_opacity'] is None
    
    def test_combined_filters(self):
        """Can combine blur and overlay."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![blur:4 overlay:0.5](image.jpg)

# Title
''')
        assert result['blur_radius'] == 4.0
        assert result['overlay_opacity'] == 0.5
    
    def test_background_left_position(self):
        """Using 'left' modifier sets position."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![left](image.jpg)

# Title
''')
        assert result['background_position'] == 'left'
        assert result['background'] == 'url(image.jpg)'
    
    def test_background_right_position(self):
        """Using 'right' modifier sets position."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![right](image.jpg)

# Title
''')
        assert result['background_position'] == 'right'
        assert result['background'] == 'url(image.jpg)'
    
    def test_split_with_overlay(self):
        """Split layouts can have overlay."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![left overlay](image.jpg)

# Title
''')
        assert result['background_position'] == 'left'
        assert result['overlay_opacity'] == -1.0
    
    def test_split_with_blur(self):
        """Split layouts can have blur."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![right blur:4](image.jpg)

# Title
''')
        assert result['background_position'] == 'right'
        assert result['blur_radius'] == 4.0
    
    def test_background_top_position(self):
        """Using 'top' modifier sets position."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![top](image.jpg)

# Title
''')
        assert result['background_position'] == 'top'
        assert result['background'] == 'url(image.jpg)'
    
    def test_background_bottom_position(self):
        """Using 'bottom' modifier sets position."""
        parser = MarkdownParser()
        result = parser.parse_slide_markdown('''
![bottom](image.jpg)

# Title
''')
        assert result['background_position'] == 'bottom'
        assert result['background'] == 'url(image.jpg)'
