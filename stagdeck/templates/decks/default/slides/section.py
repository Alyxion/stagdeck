"""SectionSlide - Section header/divider slide."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class SectionSlide(MasterSlide):
    """Section header/divider slide.
    
    Elements: background, title, subtitle
    Data: title (required), subtitle (optional)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col items-start justify-center pl-20'):
            with SlideElement('title', style='title', classes=''):
                ui.label(self.data.get('title', '')).classes(
                    'text-6xl font-bold text-white'
                )
            
            if self.data.get('subtitle'):
                with SlideElement('subtitle', style='subtitle', classes='mt-4'):
                    ui.label(self.data.get('subtitle', '')).classes(
                        'text-2xl text-white/70'
                    )
