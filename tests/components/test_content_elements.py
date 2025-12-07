"""Tests for content element components."""

import pytest

# Note: These components render NiceGUI elements, so we test the module imports
# and basic function signatures. Visual testing is done via render endpoint.

from stagdeck.components.content_elements import (
    render_table,
    render_bullet_list,
    render_numbered_list,
    render_code_block,
    render_blockquote,
    render_paragraph,
    render_mixed_content,
    ContentStyle,
)


class TestContentElementImports:
    """Test that all content elements can be imported."""
    
    def test_render_table_exists(self):
        """render_table function exists."""
        assert callable(render_table)
    
    def test_render_bullet_list_exists(self):
        """render_bullet_list function exists."""
        assert callable(render_bullet_list)
    
    def test_render_numbered_list_exists(self):
        """render_numbered_list function exists."""
        assert callable(render_numbered_list)
    
    def test_render_code_block_exists(self):
        """render_code_block function exists."""
        assert callable(render_code_block)
    
    def test_render_blockquote_exists(self):
        """render_blockquote function exists."""
        assert callable(render_blockquote)
    
    def test_render_paragraph_exists(self):
        """render_paragraph function exists."""
        assert callable(render_paragraph)
    
    def test_render_mixed_content_exists(self):
        """render_mixed_content function exists."""
        assert callable(render_mixed_content)


class TestContentStyle:
    """Test ContentStyle dataclass."""
    
    def test_default_values(self):
        """ContentStyle has sensible defaults."""
        style = ContentStyle()
        assert style.font_size == 1.8
        assert style.line_height == 1.6
        assert style.color == ''
    
    def test_custom_values(self):
        """ContentStyle accepts custom values."""
        style = ContentStyle(font_size=2.0, line_height=1.8, color='#fff')
        assert style.font_size == 2.0
        assert style.line_height == 1.8
        assert style.color == '#fff'
