"""Code block content element."""

from nicegui import ui

from .base import ContentElement


class CodeBlockElement(ContentElement):
    """Renders a markdown code block with controlled sizing."""
    
    def __init__(self, content: str, font_size: float = 1.4):
        """Initialize code block element.
        
        :param content: Markdown code block (with ``` delimiters).
        :param font_size: Font size in rem.
        """
        super().__init__(content, font_size)
    
    async def build(self) -> None:
        """Build the code block UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.5;'
        ):
            ui.markdown(self.content)


async def render_code_block(
    markdown_code: str,
    font_size: float = 1.4,
) -> None:
    """Render a markdown code block with controlled sizing."""
    element = CodeBlockElement(markdown_code, font_size)
    await element.build()
