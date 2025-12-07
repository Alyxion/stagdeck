"""Mixed content element."""

from nicegui import ui

from .base import ContentElement


class MixedContentElement(ContentElement):
    """Renders mixed markdown content with controlled sizing.
    
    Use this for content that may contain multiple element types.
    The font size applies to the container and elements inherit it.
    """
    
    def __init__(self, content: str, font_size: float = 1.8):
        """Initialize mixed content element.
        
        :param content: Any markdown content.
        :param font_size: Base font size in rem.
        """
        super().__init__(content, font_size)
    
    async def build(self) -> None:
        """Build the mixed content UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.5;'
        ):
            ui.markdown(self.content)


async def render_mixed_content(
    markdown_content: str,
    font_size: float = 1.8,
) -> None:
    """Render mixed markdown content with controlled sizing."""
    element = MixedContentElement(markdown_content, font_size)
    await element.build()
