"""Paragraph content element."""

from nicegui import ui

from .base import ContentElement


class ParagraphElement(ContentElement):
    """Renders markdown paragraph/text with controlled sizing."""
    
    def __init__(self, content: str, font_size: float = 1.8):
        """Initialize paragraph element.
        
        :param content: Markdown text (can include inline formatting).
        :param font_size: Font size in rem.
        """
        super().__init__(content, font_size)
    
    async def build(self) -> None:
        """Build the paragraph UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.6;'
        ):
            ui.markdown(self.content)


async def render_paragraph(
    markdown_text: str,
    font_size: float = 1.8,
) -> None:
    """Render markdown paragraph/text with controlled sizing."""
    element = ParagraphElement(markdown_text, font_size)
    await element.build()
