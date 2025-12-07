"""ThreeColumnSlide - Three-column layout with title."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class ThreeColumnSlide(MasterSlide):
    """Three-column layout with title.
    
    Elements: background, title, columns (col1, col2, col3)
    Data: title, col1, col2, col3
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col p-16'):
            with SlideElement('title', style='title', classes='mb-8'):
                ui.label(self.data.get('title', '')).classes(
                    'text-5xl font-bold text-white'
                )
            
            with SlideElement('columns', classes='flex-1 flex gap-8'):
                with SlideElement('col1', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('col1', '')).classes(
                        'text-lg text-white/90 prose prose-invert max-w-none'
                    )
                
                with SlideElement('col2', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('col2', '')).classes(
                        'text-lg text-white/90 prose prose-invert max-w-none'
                    )
                
                with SlideElement('col3', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('col3', '')).classes(
                        'text-lg text-white/90 prose prose-invert max-w-none'
                    )
