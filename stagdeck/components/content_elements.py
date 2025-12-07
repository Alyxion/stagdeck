"""Custom content elements for StagDeck slides.

These components wrap NiceGUI's markdown but provide explicit size control
to ensure proper scaling based on content analysis.
"""

from dataclasses import dataclass
from nicegui import ui


@dataclass
class ContentStyle:
    """Style configuration for content elements."""
    font_size: float = 1.8  # rem
    line_height: float = 1.6
    color: str = ''
    

def render_table(
    markdown_table: str,
    font_size: float = 1.8,
    cell_padding: str = '0.5em 0.8em',
) -> None:
    """Render a markdown table with controlled sizing.
    
    :param markdown_table: Markdown table string (with | delimiters).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    :param cell_padding: CSS padding for cells.
    """
    # Convert rem to px (base 16px * rem value * scale for 1920px slide)
    # On a 1920px slide, we want larger text - multiply by ~20 for good sizing
    px_size = font_size * 20
    
    # Wrapper with font size control - full width, table will be styled by CSS
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.4;'
    ):
        ui.markdown(markdown_table).classes('w-full')


def render_bullet_list(
    markdown_list: str,
    font_size: float = 1.8,
    item_spacing: str = '0.4em',
) -> None:
    """Render a markdown bullet list with controlled sizing.
    
    :param markdown_list: Markdown list string (with - or * items).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    :param item_spacing: Spacing between items.
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.5;'
    ):
        ui.markdown(markdown_list)


def render_numbered_list(
    markdown_list: str,
    font_size: float = 1.8,
    item_spacing: str = '0.4em',
) -> None:
    """Render a markdown numbered list with controlled sizing.
    
    :param markdown_list: Markdown list string (with 1. 2. items).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    :param item_spacing: Spacing between items.
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.5;'
    ):
        ui.markdown(markdown_list)


def render_code_block(
    markdown_code: str,
    font_size: float = 1.4,
) -> None:
    """Render a markdown code block with controlled sizing.
    
    :param markdown_code: Markdown code block (with ``` delimiters).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.5;'
    ):
        ui.markdown(markdown_code)


def render_blockquote(
    markdown_quote: str,
    font_size: float = 1.8,
) -> None:
    """Render a markdown blockquote with controlled sizing.
    
    :param markdown_quote: Markdown blockquote (with > prefix).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.6;'
    ):
        ui.markdown(markdown_quote)


def render_paragraph(
    markdown_text: str,
    font_size: float = 1.8,
) -> None:
    """Render markdown paragraph/text with controlled sizing.
    
    :param markdown_text: Markdown text (can include inline formatting).
    :param font_size: Font size in rem (converted to px for 1920x1080 slides).
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.6;'
    ):
        ui.markdown(markdown_text)


def render_mixed_content(
    markdown_content: str,
    font_size: float = 1.8,
) -> None:
    """Render mixed markdown content with controlled sizing.
    
    This is for content that may contain multiple element types.
    The font size applies to the container and elements inherit it.
    
    :param markdown_content: Any markdown content.
    :param font_size: Base font size in rem (converted to px for 1920x1080 slides).
    """
    px_size = font_size * 20
    with ui.element('div').classes('w-full').style(
        f'font-size: {px_size}px; line-height: 1.5;'
    ):
        ui.markdown(markdown_content)
