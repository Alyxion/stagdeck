"""MasterSlide - Base class for all slide layouts."""

from nicegui import ui

from stagdeck.slide import Slide
from stagdeck.slide_element import SlideElement


class MasterSlide(Slide):
    """Base for all layouts - provides the background element.
    
    All slide layouts inherit from MasterSlide which creates the
    background SlideElement. Subclasses call super().build() to
    get the background, then add their own elements.
    """
    
    async def build(self):
        """Build the background element."""
        await super().build()
        
        with SlideElement('background', classes='absolute inset-0'):
            # Background color/gradient from theme
            bg_color = self.data.get('background_color', '')
            if not bg_color and hasattr(self, 'theme') and self.theme:
                bg_color = self.theme.get('background.color', '#1a1a2e')
            
            if bg_color:
                if 'gradient' in bg_color or bg_color.startswith('linear') or bg_color.startswith('radial'):
                    ui.element('div').classes('w-full h-full').style(f'background: {bg_color}')
                else:
                    ui.element('div').classes('w-full h-full').style(f'background-color: {bg_color}')
            else:
                ui.element('div').classes('w-full h-full bg-slate-900')
