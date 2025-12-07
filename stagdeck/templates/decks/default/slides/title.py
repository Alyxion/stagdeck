"""TitleSlide - Opening slide with centered title and subtitle."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class TitleSlide(MasterSlide):
    """Opening slide with centered title and subtitle.
    
    Elements: background, title, subtitle
    Data: title (required), subtitle (optional)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col items-center justify-center'):
            with SlideElement('title', style='title', classes='text-center'):
                ui.label(self.data.get('title', '')).classes(
                    'text-7xl font-bold text-white'
                )
            
            if self.data.get('subtitle'):
                with SlideElement('subtitle', style='subtitle', classes='text-center mt-6'):
                    ui.label(self.data.get('subtitle', '')).classes(
                        'text-3xl text-white/80'
                    )
