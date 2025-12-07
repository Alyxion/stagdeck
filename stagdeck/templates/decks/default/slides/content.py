"""ContentSlide - Standard content slide with title and body."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class ContentSlide(MasterSlide):
    """Standard content slide with title and body.
    
    Elements: background, title, body
    Data: title (required), body (required, markdown)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col p-16'):
            with SlideElement('title', style='title', classes='mb-8'):
                ui.label(self.data.get('title', '')).classes(
                    'text-5xl font-bold text-white'
                )
            
            with SlideElement('body', style='body_text', classes='flex-1'):
                ui.markdown(self.data.get('body', '')).classes(
                    'text-2xl text-white/90 prose prose-invert prose-lg max-w-none'
                )
