"""Blockquote content element."""

from nicegui import ui

from .base import ContentElement


class BlockquoteElement(ContentElement):
    """Renders a markdown blockquote with controlled sizing."""
    
    def __init__(self, content: str, font_size: float = 1.8):
        """Initialize blockquote element.
        
        :param content: Markdown blockquote (with > prefix).
        :param font_size: Font size in rem.
        """
        super().__init__(content, font_size)
    
    async def build(self) -> None:
        """Build the blockquote UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.6;'
        ):
            ui.markdown(self.content)


async def render_blockquote(
    markdown_quote: str,
    font_size: float = 1.8,
) -> None:
    """Render a markdown blockquote with controlled sizing."""
    element = BlockquoteElement(markdown_quote, font_size)
    await element.build()
