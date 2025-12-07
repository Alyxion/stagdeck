"""StagDeck Components.

Custom UI components and utilities for building presentations.
"""

from .markdown_parser import (
    MarkdownParser,
    MarkdownDeckInfo,
    MarkdownSlideInfo,
    SlideContentType,
)

from .slide_layout import (
    LayoutMode,
    LayoutConfig,
    ContentMetrics,
    build_slide_layout,
    detect_layout_mode,
    analyze_content,
    calculate_content_scale,
    DEFAULT_CONFIG,
)

from .content_elements import (
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
    # Convenience functions
    render_table,
    render_bullet_list,
    render_numbered_list,
    render_code_block,
    render_blockquote,
    render_paragraph,
    render_mixed_content,
)

__all__ = [
    # Markdown Parser
    'MarkdownParser',
    'MarkdownDeckInfo',
    'MarkdownSlideInfo',
    'SlideContentType',
    # Slide Layout
    'LayoutMode',
    'LayoutConfig',
    'ContentMetrics',
    'build_slide_layout',
    'detect_layout_mode',
    'analyze_content',
    'calculate_content_scale',
    'DEFAULT_CONFIG',
    # Content Element Classes
    'ContentElement',
    'ContentStyle',
    'TableElement',
    'BulletListElement',
    'NumberedListElement',
    'CodeBlockElement',
    'BlockquoteElement',
    'ParagraphElement',
    'MixedContentElement',
    'REM_TO_PX_FACTOR',
    # Content Element Functions
    'render_table',
    'render_bullet_list',
    'render_numbered_list',
    'render_code_block',
    'render_blockquote',
    'render_paragraph',
    'render_mixed_content',
]
