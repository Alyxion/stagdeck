"""Bullet list content element."""

from nicegui import ui

from .base import ContentElement


class BulletListElement(ContentElement):
    """Renders a markdown bullet list with controlled sizing."""
    
    def __init__(
        self,
        content: str,
        font_size: float = 1.8,
        item_spacing: str = '0.4em',
    ):
        """Initialize bullet list element.
        
        :param content: Markdown list string (with - or * items).
        :param font_size: Font size in rem.
        :param item_spacing: Spacing between items.
        """
        super().__init__(content, font_size)
        self.item_spacing = item_spacing
    
    async def build(self) -> None:
        """Build the bullet list UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.5;'
        ):
            ui.markdown(self.content)


async def render_bullet_list(
    markdown_list: str,
    font_size: float = 1.8,
    item_spacing: str = '0.4em',
) -> None:
    """Render a markdown bullet list with controlled sizing."""
    element = BulletListElement(markdown_list, font_size, item_spacing)
    await element.build()
