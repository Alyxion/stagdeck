"""Tests for content element components."""

import pytest
from inspect import iscoroutinefunction

# Note: These components render NiceGUI elements, so we test the module imports
# and basic class/function signatures. Visual testing is done via render endpoint.

from stagdeck.components import (
    # Classes
    ContentElement,
    ContentStyle,
    TableElement,
    BulletListElement,
    NumberedListElement,
    CodeBlockElement,
    BlockquoteElement,
    ParagraphElement,
    MixedContentElement,
    REM_TO_PX_FACTOR,
    # Functions
    render_table,
    render_bullet_list,
    render_numbered_list,
    render_code_block,
    render_blockquote,
    render_paragraph,
    render_mixed_content,
)


class TestContentElementClasses:
    """Test content element class structure."""
    
    def test_table_element_inherits_from_base(self):
        """TableElement inherits from ContentElement."""
        assert issubclass(TableElement, ContentElement)
    
    def test_bullet_list_element_inherits_from_base(self):
        """BulletListElement inherits from ContentElement."""
        assert issubclass(BulletListElement, ContentElement)
    
    def test_numbered_list_element_inherits_from_base(self):
        """NumberedListElement inherits from ContentElement."""
        assert issubclass(NumberedListElement, ContentElement)
    
    def test_code_block_element_inherits_from_base(self):
        """CodeBlockElement inherits from ContentElement."""
        assert issubclass(CodeBlockElement, ContentElement)
    
    def test_blockquote_element_inherits_from_base(self):
        """BlockquoteElement inherits from ContentElement."""
        assert issubclass(BlockquoteElement, ContentElement)
    
    def test_paragraph_element_inherits_from_base(self):
        """ParagraphElement inherits from ContentElement."""
        assert issubclass(ParagraphElement, ContentElement)
    
    def test_mixed_content_element_inherits_from_base(self):
        """MixedContentElement inherits from ContentElement."""
        assert issubclass(MixedContentElement, ContentElement)
    
    def test_table_element_has_async_build(self):
        """TableElement has async build method."""
        element = TableElement('| A | B |')
        assert iscoroutinefunction(element.build)
    
    def test_bullet_list_element_has_async_build(self):
        """BulletListElement has async build method."""
        element = BulletListElement('- Item')
        assert iscoroutinefunction(element.build)
    
    def test_px_size_conversion(self):
        """px_size property converts rem to pixels correctly."""
        element = TableElement('| A |', font_size=2.0)
        assert element.px_size == 2.0 * REM_TO_PX_FACTOR


class TestContentElementInitialization:
    """Test content element initialization."""
    
    def test_table_element_stores_content(self):
        """TableElement stores content."""
        content = '| Header |\n|--------|\n| Cell |'
        element = TableElement(content)
        assert element.content == content
    
    def test_table_element_default_font_size(self):
        """TableElement has default font size."""
        element = TableElement('| A |')
        assert element.font_size == 1.8
    
    def test_table_element_custom_font_size(self):
        """TableElement accepts custom font size."""
        element = TableElement('| A |', font_size=2.5)
        assert element.font_size == 2.5
    
    def test_code_block_element_default_font_size(self):
        """CodeBlockElement has smaller default font size."""
        element = CodeBlockElement('```python\ncode\n```')
        assert element.font_size == 1.4


class TestConvenienceFunctions:
    """Test backward-compatible convenience functions."""
    
    def test_render_table_is_async(self):
        """render_table is an async function."""
        assert iscoroutinefunction(render_table)
    
    def test_render_bullet_list_is_async(self):
        """render_bullet_list is an async function."""
        assert iscoroutinefunction(render_bullet_list)
    
    def test_render_numbered_list_is_async(self):
        """render_numbered_list is an async function."""
        assert iscoroutinefunction(render_numbered_list)
    
    def test_render_code_block_is_async(self):
        """render_code_block is an async function."""
        assert iscoroutinefunction(render_code_block)
    
    def test_render_blockquote_is_async(self):
        """render_blockquote is an async function."""
        assert iscoroutinefunction(render_blockquote)
    
    def test_render_paragraph_is_async(self):
        """render_paragraph is an async function."""
        assert iscoroutinefunction(render_paragraph)
    
    def test_render_mixed_content_is_async(self):
        """render_mixed_content is an async function."""
        assert iscoroutinefunction(render_mixed_content)


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


class TestRemToPxFactor:
    """Test REM_TO_PX_FACTOR constant."""
    
    def test_factor_value(self):
        """REM_TO_PX_FACTOR is 20."""
        assert REM_TO_PX_FACTOR == 20
