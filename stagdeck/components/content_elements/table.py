"""Table content element."""

from nicegui import ui

from .base import ContentElement


class TableElement(ContentElement):
    """Renders a markdown table with controlled sizing."""
    
    def __init__(
        self,
        content: str,
        font_size: float = 1.8,
        cell_padding: str = '0.5em 0.8em',
    ):
        """Initialize table element.
        
        :param content: Markdown table string (with | delimiters).
        :param font_size: Font size in rem.
        :param cell_padding: CSS padding for cells.
        """
        super().__init__(content, font_size)
        self.cell_padding = cell_padding
    
    async def build(self) -> None:
        """Build the table UI."""
        with ui.element('div').classes('w-full').style(
            f'font-size: {self.px_size}px; line-height: 1.4;'
        ):
            ui.markdown(self.content).classes('w-full')


async def render_table(
    markdown_table: str,
    font_size: float = 1.8,
    cell_padding: str = '0.5em 0.8em',
) -> None:
    """Render a markdown table with controlled sizing."""
    element = TableElement(markdown_table, font_size, cell_padding)
    await element.build()
