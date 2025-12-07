"""Tests for SlideElement using NiceGUI User fixture."""

import pytest
from nicegui import ui
from nicegui.testing import User

from stagdeck.slide_element import SlideElement


async def test_slide_element_creates_div(user: User) -> None:
    """SlideElement creates a div with no padding/margin."""
    @ui.page('/')
    def page():
        SlideElement('test')
    
    await user.open('/')
    # Element should exist (no error means success)


async def test_slide_element_has_no_padding_margin(user: User) -> None:
    """SlideElement has p-0 m-0 classes by default."""
    @ui.page('/')
    def page():
        elem = SlideElement('test')
        # Check classes are applied
        assert 'p-0' in elem._classes
        assert 'm-0' in elem._classes
    
    await user.open('/')


async def test_slide_element_accepts_additional_classes(user: User) -> None:
    """SlideElement accepts additional Tailwind classes."""
    @ui.page('/')
    def page():
        elem = SlideElement('test', classes='flex gap-4')
        assert 'p-0' in elem._classes
        assert 'm-0' in elem._classes
        assert 'flex' in elem._classes
        assert 'gap-4' in elem._classes
    
    await user.open('/')


async def test_slide_element_stores_name(user: User) -> None:
    """SlideElement stores its name."""
    @ui.page('/')
    def page():
        elem = SlideElement('my_element')
        assert elem.name == 'my_element'
    
    await user.open('/')


async def test_slide_element_stores_style_ref(user: User) -> None:
    """SlideElement stores style reference."""
    @ui.page('/')
    def page():
        elem = SlideElement('title', style='title')
        assert elem.style_ref == 'title'
    
    await user.open('/')


async def test_nested_elements_register_with_parent(user: User) -> None:
    """Nested SlideElements register with parent via context."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            SlideElement('child1')
            SlideElement('child2')
        
        assert 'child1' in root.children_elements
        assert 'child2' in root.children_elements
        assert root.children_elements['child1'].name == 'child1'
        assert root.children_elements['child2'].name == 'child2'
    
    await user.open('/')


async def test_deeply_nested_elements(user: User) -> None:
    """Deeply nested SlideElements form correct hierarchy."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            with SlideElement('columns') as columns:
                SlideElement('left')
                SlideElement('right')
        
        # Direct children of root
        assert 'columns' in root.children_elements
        assert 'left' not in root.children_elements  # Not direct child
        
        # Children of columns
        assert 'left' in columns.children_elements
        assert 'right' in columns.children_elements
    
    await user.open('/')


async def test_find_direct_child(user: User) -> None:
    """find() returns direct child element."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            SlideElement('child')
        
        found = root.find('child')
        assert found is not None
        assert found.name == 'child'
    
    await user.open('/')


async def test_find_nested_child(user: User) -> None:
    """find() searches recursively through hierarchy."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            with SlideElement('columns'):
                SlideElement('left')
                SlideElement('right')
        
        # Find nested elements from root
        left = root.find('left')
        right = root.find('right')
        
        assert left is not None
        assert left.name == 'left'
        assert right is not None
        assert right.name == 'right'
    
    await user.open('/')


async def test_find_returns_none_for_missing(user: User) -> None:
    """find() returns None for non-existent element."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            SlideElement('child')
        
        assert root.find('nonexistent') is None
    
    await user.open('/')


async def test_getitem_shorthand(user: User) -> None:
    """__getitem__ provides shorthand for find()."""
    @ui.page('/')
    def page():
        with SlideElement('root') as root:
            SlideElement('child')
        
        assert root['child'].name == 'child'
    
    await user.open('/')


async def test_getitem_raises_keyerror(user: User) -> None:
    """__getitem__ raises KeyError for missing element."""
    @ui.page('/')
    def page():
        root = SlideElement('root')
        
        with pytest.raises(KeyError) as exc_info:
            _ = root['nonexistent']
        
        assert 'nonexistent' in str(exc_info.value)
    
    await user.open('/')


async def test_context_manager_nesting(user: User) -> None:
    """SlideElement works as context manager for nesting."""
    @ui.page('/')
    def page():
        with SlideElement('outer') as outer:
            with SlideElement('inner') as inner:
                ui.label('Content')
        
        assert 'inner' in outer.children_elements
        assert outer.children_elements['inner'] is inner
    
    await user.open('/')


async def test_non_slide_element_parent(user: User) -> None:
    """SlideElement inside non-SlideElement doesn't register."""
    @ui.page('/')
    def page():
        with ui.column():
            elem = SlideElement('orphan')
        
        # Should not crash, just won't have a SlideElement parent
        assert elem.name == 'orphan'
        assert len(elem.children_elements) == 0
    
    await user.open('/')
