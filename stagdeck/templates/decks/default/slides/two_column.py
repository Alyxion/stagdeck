"""TwoColumnSlide - Two-column layout with title."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class TwoColumnSlide(MasterSlide):
    """Two-column layout with title.
    
    Elements: background, title, columns (left, right)
    Data: title (required), left (markdown), right (markdown)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col p-16'):
            with SlideElement('title', style='title', classes='mb-8'):
                ui.label(self.data.get('title', '')).classes(
                    'text-5xl font-bold text-white'
                )
            
            with SlideElement('columns', classes='flex-1 flex gap-12'):
                with SlideElement('left', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('left', '')).classes(
                        'text-xl text-white/90 prose prose-invert max-w-none'
                    )
                
                with SlideElement('right', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('right', '')).classes(
                        'text-xl text-white/90 prose prose-invert max-w-none'
                    )
