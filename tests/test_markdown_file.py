"""Tests for markdown file loading and slide manipulation."""

import pytest
from pathlib import Path

from stagdeck import SlideDeck


class TestAddFromFile:
    """Test add_from_file() functionality."""
    
    def test_load_single_slide(self, tmp_path):
        """Can load a single slide from markdown file."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Hello World\n\nContent here.')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert len(deck.slides) == 1
        assert deck.slides[0].title == 'Hello World'
    
    def test_load_multiple_slides(self, tmp_path):
        """Can load multiple slides separated by ---."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''# Slide 1
Content 1

---

# Slide 2
Content 2

---

# Slide 3
Content 3
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert len(deck.slides) == 3
        assert deck.slides[0].title == 'Slide 1'
        assert deck.slides[1].title == 'Slide 2'
        assert deck.slides[2].title == 'Slide 3'
    
    def test_custom_separator(self, tmp_path):
        """Can use custom separator."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''# Slide 1

===

# Slide 2
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file, separator='===')
        
        assert len(deck.slides) == 2
    
    def test_tracks_source_file(self, tmp_path):
        """Source file is tracked for hot-reload."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Test')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert md_file.resolve() in deck.source_files
    
    def test_chaining(self, tmp_path):
        """add_from_file returns self for chaining."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Test')
        
        deck = SlideDeck()
        result = deck.add_from_file(md_file)
        
        assert result is deck
    
    def test_file_not_found(self, tmp_path):
        """Raises FileNotFoundError for missing file."""
        deck = SlideDeck()
        
        with pytest.raises(FileNotFoundError):
            deck.add_from_file(tmp_path / 'nonexistent.md')
    
    def test_empty_slides_ignored(self, tmp_path):
        """Empty slides between separators are ignored."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''# Slide 1

---

---

# Slide 2
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert len(deck.slides) == 2


class TestNameDirective:
    """Test [name: ...] directive parsing."""
    
    def test_name_directive_parsed(self, tmp_path):
        """[name: ...] directive sets slide name."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: intro]
# Introduction

Welcome!
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert deck.slides[0].name == 'intro'
    
    def test_name_directive_case_insensitive(self, tmp_path):
        """[NAME: ...] works too."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[NAME: MySlide]
# Test
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert deck.slides[0].name == 'MySlide'
    
    def test_name_with_spaces(self, tmp_path):
        """Name can have spaces trimmed."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name:   spaced_name   ]
# Test
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert deck.slides[0].name == 'spaced_name'
    
    def test_multiple_named_slides(self, tmp_path):
        """Multiple slides can have names."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: first]
# First

---

[name: second]
# Second

---

# Third
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert deck.slides[0].name == 'first'
        assert deck.slides[1].name == 'second'
        assert deck.slides[2].name.startswith('slide_')  # Auto-generated
    
    def test_get_slide_by_name(self, tmp_path):
        """Can retrieve slide by name."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: target]
# Target Slide
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        slide = deck.get_slide_by_name('target')
        assert slide is not None
        assert slide.title == 'Target Slide'


class TestInsert:
    """Test insert() functionality."""
    
    def test_insert_after(self, tmp_path):
        """Can insert slide after named slide."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: first]
# First

---

[name: second]
# Second
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.insert('# Inserted', after='first')
        
        assert len(deck.slides) == 3
        assert deck.slides[0].title == 'First'
        assert deck.slides[1].title == 'Inserted'
        assert deck.slides[2].title == 'Second'
    
    def test_insert_before(self, tmp_path):
        """Can insert slide before named slide."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: first]
# First

---

[name: second]
# Second
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.insert('# Inserted', before='second')
        
        assert len(deck.slides) == 3
        assert deck.slides[0].title == 'First'
        assert deck.slides[1].title == 'Inserted'
        assert deck.slides[2].title == 'Second'
    
    def test_insert_at_beginning(self, tmp_path):
        """Can insert before first slide."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: first]
# First
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.insert('# New First', before='first')
        
        assert deck.slides[0].title == 'New First'
        assert deck.slides[1].title == 'First'
    
    def test_insert_at_end(self, tmp_path):
        """Can insert after last slide."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: last]
# Last
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.insert('# New Last', after='last')
        
        assert deck.slides[0].title == 'Last'
        assert deck.slides[1].title == 'New Last'
    
    def test_insert_chaining(self, tmp_path):
        """insert returns self for chaining."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('[name: a]\n# A')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        result = deck.insert('# B', after='a')
        
        assert result is deck
    
    def test_insert_requires_before_or_after(self):
        """Raises ValueError if neither before nor after specified."""
        deck = SlideDeck()
        deck.add('# Test', name='test')
        
        with pytest.raises(ValueError, match="Exactly one"):
            deck.insert('# New')
    
    def test_insert_rejects_both_before_and_after(self):
        """Raises ValueError if both before and after specified."""
        deck = SlideDeck()
        deck.add('# Test', name='test')
        
        with pytest.raises(ValueError, match="Exactly one"):
            deck.insert('# New', before='test', after='test')
    
    def test_insert_unknown_name_raises(self):
        """Raises ValueError for unknown slide name."""
        deck = SlideDeck()
        deck.add('# Test', name='test')
        
        with pytest.raises(ValueError, match="not found"):
            deck.insert('# New', after='nonexistent')


class TestReplace:
    """Test replace() functionality."""
    
    def test_replace_slide(self, tmp_path):
        """Can replace a named slide."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: placeholder]
# Placeholder
This will be replaced.
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.replace('placeholder', '# Replaced\n\nNew content!')
        
        assert len(deck.slides) == 1
        assert deck.slides[0].title == 'Replaced'
        assert deck.slides[0].name == 'placeholder'  # Name preserved
    
    def test_replace_preserves_position(self, tmp_path):
        """Replaced slide stays in same position."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: first]
# First

---

[name: middle]
# Middle

---

[name: last]
# Last
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.replace('middle', '# New Middle')
        
        assert deck.slides[0].title == 'First'
        assert deck.slides[1].title == 'New Middle'
        assert deck.slides[2].title == 'Last'
    
    def test_replace_with_builder(self, tmp_path):
        """Can replace with custom builder."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('[name: chart]\n# Chart Placeholder')
        
        def my_builder(slide):
            pass
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        deck.replace('chart', '# Dynamic Chart', builder=my_builder)
        
        assert deck.slides[0].builder is my_builder
    
    def test_replace_chaining(self, tmp_path):
        """replace returns self for chaining."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('[name: a]\n# A')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        result = deck.replace('a', '# B')
        
        assert result is deck
    
    def test_replace_unknown_name_raises(self):
        """Raises ValueError for unknown slide name."""
        deck = SlideDeck()
        deck.add('# Test', name='test')
        
        with pytest.raises(ValueError, match="not found"):
            deck.replace('nonexistent', '# New')
    
    def test_replace_preserves_name_by_default(self, tmp_path):
        """Replace preserves original name by default (for stable references)."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('[name: original]\n# Old')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        # Even with [name:] in markdown, original name is preserved
        deck.replace('original', '[name: ignored]\n# New')
        
        # Name is preserved so references to 'original' still work
        assert deck.slides[0].name == 'original'
        assert deck.slides[0].title == 'New'


class TestIntegration:
    """Integration tests for markdown file + Python hybrid workflow."""
    
    def test_full_workflow(self, tmp_path):
        """Complete workflow: load, insert, replace."""
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: intro]
# Introduction

---

[name: content]
# Main Content

---

[name: chart_placeholder]
# Chart
(placeholder)

---

[name: conclusion]
# Conclusion
''')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        # Insert a slide after intro
        deck.insert('# Agenda', after='intro', name='agenda')
        
        # Replace the placeholder
        deck.replace('chart_placeholder', '# Sales Chart')
        
        # Verify final order
        assert len(deck.slides) == 5
        assert deck.slides[0].name == 'intro'
        assert deck.slides[1].name == 'agenda'
        assert deck.slides[2].name == 'content'
        assert deck.slides[3].name == 'chart_placeholder'
        assert deck.slides[4].name == 'conclusion'
        
        # Verify content
        assert deck.slides[1].title == 'Agenda'
        assert deck.slides[3].title == 'Sales Chart'
