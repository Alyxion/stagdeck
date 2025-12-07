"""Content elements for StagDeck slides.

These components wrap NiceGUI's markdown but provide explicit size control
to ensure proper scaling based on content analysis.
"""

from .base import (
    ContentElement,
    ContentStyle,
    REM_TO_PX_FACTOR,
)

from .table import TableElement, render_table
from .bullet_list import BulletListElement, render_bullet_list
from .numbered_list import NumberedListElement, render_numbered_list
from .code_block import CodeBlockElement, render_code_block
from .blockquote import BlockquoteElement, render_blockquote
from .paragraph import ParagraphElement, render_paragraph
from .mixed_content import MixedContentElement, render_mixed_content

__all__ = [
    # Base
    'ContentElement',
    'ContentStyle',
    'REM_TO_PX_FACTOR',
    # Element Classes
    'TableElement',
    'BulletListElement',
    'NumberedListElement',
    'CodeBlockElement',
    'BlockquoteElement',
    'ParagraphElement',
    'MixedContentElement',
    # Convenience Functions
    'render_table',
    'render_bullet_list',
    'render_numbered_list',
    'render_code_block',
    'render_blockquote',
    'render_paragraph',
    'render_mixed_content',
]
