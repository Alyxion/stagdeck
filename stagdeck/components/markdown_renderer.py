"""Custom Markdown Renderer for StagDeck.

Parses markdown and renders each element (table, code, list, etc.) as a 
separate NiceGUI component with proper sizing control.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from nicegui import ui


class BlockType(Enum):
    """Types of markdown blocks."""
    PARAGRAPH = auto()
    HEADING = auto()
    TABLE = auto()
    CODE = auto()
    BULLET_LIST = auto()
    NUMBERED_LIST = auto()
    BLOCKQUOTE = auto()
    IMAGE = auto()


@dataclass
class MarkdownBlock:
    """A parsed markdown block."""
    type: BlockType
    content: str
    level: int = 0  # For headings
    language: str = ''  # For code blocks
    rows: list[list[str]] | None = None  # For tables
    items: list[str] | None = None  # For lists


def parse_markdown_blocks(content: str) -> list[MarkdownBlock]:
    """Parse markdown into separate blocks.
    
    :param content: Raw markdown content.
    :return: List of parsed blocks.
    """
    blocks: list[MarkdownBlock] = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Code block
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            blocks.append(MarkdownBlock(
                type=BlockType.CODE,
                content='\n'.join(code_lines),
                language=lang or 'text',
            ))
            i += 1  # Skip closing ```
            continue
        
        # Table
        if line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            
            # Parse table
            rows = []
            for tl in table_lines:
                # Skip separator line
                if re.match(r'^\|[\s\-:|]+\|$', tl.strip()):
                    continue
                cells = [c.strip() for c in tl.split('|')[1:-1]]
                if cells:
                    rows.append(cells)
            
            blocks.append(MarkdownBlock(
                type=BlockType.TABLE,
                content='\n'.join(table_lines),
                rows=rows,
            ))
            continue
        
        # Blockquote
        if line.strip().startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(MarkdownBlock(
                type=BlockType.BLOCKQUOTE,
                content='\n'.join(quote_lines),
            ))
            continue
        
        # Bullet list
        if re.match(r'^[\s]*[-*+]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[\s]*[-*+]\s+', lines[i]):
                item = re.sub(r'^[\s]*[-*+]\s+', '', lines[i])
                items.append(item)
                i += 1
            blocks.append(MarkdownBlock(
                type=BlockType.BULLET_LIST,
                content='\n'.join(items),
                items=items,
            ))
            continue
        
        # Numbered list
        if re.match(r'^[\s]*\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[\s]*\d+\.\s+', lines[i]):
                item = re.sub(r'^[\s]*\d+\.\s+', '', lines[i])
                items.append(item)
                i += 1
            blocks.append(MarkdownBlock(
                type=BlockType.NUMBERED_LIST,
                content='\n'.join(items),
                items=items,
            ))
            continue
        
        # Heading
        if line.strip().startswith('#'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2)
                blocks.append(MarkdownBlock(
                    type=BlockType.HEADING,
                    content=text,
                    level=level,
                ))
                i += 1
                continue
        
        # Image
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            blocks.append(MarkdownBlock(
                type=BlockType.IMAGE,
                content=img_match.group(2),  # URL
                language=img_match.group(1),  # Alt text (reusing field)
            ))
            i += 1
            continue
        
        # Default: paragraph (collect consecutive non-special lines)
        para_lines = []
        while i < len(lines):
            l = lines[i]
            if not l.strip():
                break
            if l.strip().startswith(('```', '|', '>', '#', '-', '*', '+')) or re.match(r'^\d+\.', l.strip()):
                break
            if re.match(r'!\[.*\]\(.*\)', l.strip()):
                break
            para_lines.append(l)
            i += 1
        
        if para_lines:
            blocks.append(MarkdownBlock(
                type=BlockType.PARAGRAPH,
                content='\n'.join(para_lines),
            ))
    
    return blocks


def render_markdown_blocks(
    content: str,
    font_size: float = 1.8,
    table_scale: float = 1.0,
) -> None:
    """Render markdown content as separate NiceGUI components.
    
    :param content: Raw markdown content.
    :param font_size: Base font size in rem.
    :param table_scale: Additional scale factor for tables.
    """
    blocks = parse_markdown_blocks(content)
    
    for block in blocks:
        if block.type == BlockType.TABLE:
            _render_table(block, font_size * table_scale)
        elif block.type == BlockType.CODE:
            _render_code(block, font_size * 0.85)
        elif block.type == BlockType.BULLET_LIST:
            _render_bullet_list(block, font_size)
        elif block.type == BlockType.NUMBERED_LIST:
            _render_numbered_list(block, font_size)
        elif block.type == BlockType.BLOCKQUOTE:
            _render_blockquote(block, font_size)
        elif block.type == BlockType.HEADING:
            _render_heading(block, font_size)
        elif block.type == BlockType.IMAGE:
            _render_image(block)
        else:
            _render_paragraph(block, font_size)


def _render_table(block: MarkdownBlock, font_size: float) -> None:
    """Render a table block."""
    if not block.rows:
        return
    
    with ui.element('div').classes('w-full').style(
        f'font-size: {font_size}rem; overflow-x: auto;'
    ):
        with ui.element('table').classes('w-full').style(
            'border-collapse: collapse; table-layout: auto; min-width: 100%;'
        ):
            # Header row
            if block.rows:
                with ui.element('thead'):
                    with ui.element('tr'):
                        for cell in block.rows[0]:
                            with ui.element('th').classes('text-left').style(
                                f'padding: 0.4em 0.6em; '
                                f'border: 1px solid rgba(255,255,255,0.2); '
                                f'background: rgba(255,255,255,0.1); '
                                f'font-weight: 600;'
                            ):
                                _html(_inline_markdown(cell))
                
                # Data rows
                with ui.element('tbody'):
                    for i, row in enumerate(block.rows[1:]):
                        bg = 'rgba(255,255,255,0.05)' if i % 2 == 1 else 'transparent'
                        with ui.element('tr').style(f'background: {bg};'):
                            for cell in row:
                                with ui.element('td').style(
                                    f'padding: 0.4em 0.6em; '
                                    f'border: 1px solid rgba(255,255,255,0.2);'
                                ):
                                    _html(_inline_markdown(cell))


def _render_code(block: MarkdownBlock, font_size: float) -> None:
    """Render a code block."""
    with ui.element('div').style(
        f'font-size: {font_size}rem; '
        f'background: rgba(0,0,0,0.25); '
        f'border-radius: 8px; '
        f'padding: 1em 1.2em; '
        f'margin: 0.5em 0; '
        f'overflow-x: auto;'
    ):
        with ui.element('pre').style('margin: 0;'):
            with ui.element('code').style(
                "font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace; "
                'line-height: 1.5;'
            ):
                _html(block.content.replace('<', '&lt;').replace('>', '&gt;'))


def _render_bullet_list(block: MarkdownBlock, font_size: float) -> None:
    """Render a bullet list."""
    if not block.items:
        return
    
    with ui.element('ul').style(
        f'font-size: {font_size}rem; '
        f'padding-left: 1.5em; '
        f'margin: 0.5em 0; '
        f'list-style-type: disc;'
    ):
        for item in block.items:
            with ui.element('li').style('margin-bottom: 0.3em;'):
                _html(_inline_markdown(item))


def _render_numbered_list(block: MarkdownBlock, font_size: float) -> None:
    """Render a numbered list."""
    if not block.items:
        return
    
    with ui.element('ol').style(
        f'font-size: {font_size}rem; '
        f'padding-left: 1.5em; '
        f'margin: 0.5em 0; '
        f'list-style-type: decimal;'
    ):
        for item in block.items:
            with ui.element('li').style('margin-bottom: 0.3em;'):
                _html(_inline_markdown(item))


def _render_blockquote(block: MarkdownBlock, font_size: float) -> None:
    """Render a blockquote."""
    with ui.element('blockquote').style(
        f'font-size: {font_size}rem; '
        f'border-left: 4px solid rgba(255,255,255,0.3); '
        f'padding-left: 1em; '
        f'margin: 0.5em 0; '
        f'font-style: italic; '
        f'opacity: 0.9;'
    ):
        _html(_inline_markdown(block.content))


def _render_heading(block: MarkdownBlock, font_size: float) -> None:
    """Render a heading."""
    # Scale heading size based on level
    sizes = {1: 1.8, 2: 1.5, 3: 1.3, 4: 1.1, 5: 1.0, 6: 0.9}
    scale = sizes.get(block.level, 1.0)
    
    with ui.element(f'h{block.level}').style(
        f'font-size: {font_size * scale}rem; '
        f'font-weight: 600; '
        f'margin: 0.5em 0;'
    ):
        _html(_inline_markdown(block.content))


def _render_image(block: MarkdownBlock) -> None:
    """Render an image."""
    ui.image(block.content).style(
        'max-width: 100%; '
        'max-height: 50vh; '
        'border-radius: 8px; '
        'margin: 0.5em auto; '
        'display: block;'
    )


def _render_paragraph(block: MarkdownBlock, font_size: float) -> None:
    """Render a paragraph."""
    with ui.element('p').style(
        f'font-size: {font_size}rem; '
        f'margin: 0.5em 0; '
        f'line-height: 1.5;'
    ):
        _html(_inline_markdown(block.content))


def _inline_markdown(text: str) -> str:
    """Convert inline markdown to HTML.
    
    Handles: **bold**, *italic*, `code`, [links](url)
    """
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic  
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code style="background: rgba(0,0,0,0.2); padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em;">\1</code>', text)
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color: #60a5fa; text-decoration: underline;">\1</a>', text)
    
    return text


def _html(content: str) -> None:
    """Render HTML content safely."""
    ui.html(content, sanitize=False)
