"""ComparisonSlide - Comparison layout with headers for each column."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class ComparisonSlide(MasterSlide):
    """Comparison layout with headers for each column.
    
    Elements: background, title, columns (left_header, left, right_header, right)
    Data: title, left_header, left, right_header, right
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col p-16'):
            with SlideElement('title', style='title', classes='mb-8'):
                ui.label(self.data.get('title', '')).classes(
                    'text-5xl font-bold text-white'
                )
            
            with SlideElement('columns', classes='flex-1 flex gap-12'):
                # Left column
                with SlideElement('left_column', classes='flex-1 flex flex-col'):
                    with SlideElement('left_header', style='subtitle', classes='mb-4 pb-2 border-b border-white/30'):
                        ui.label(self.data.get('left_header', '')).classes(
                            'text-2xl font-semibold text-white'
                        )
                    with SlideElement('left', style='body_text', classes='flex-1'):
                        ui.markdown(self.data.get('left', '')).classes(
                            'text-xl text-white/90 prose prose-invert max-w-none'
                        )
                
                # Right column
                with SlideElement('right_column', classes='flex-1 flex flex-col'):
                    with SlideElement('right_header', style='subtitle', classes='mb-4 pb-2 border-b border-white/30'):
                        ui.label(self.data.get('right_header', '')).classes(
                            'text-2xl font-semibold text-white'
                        )
                    with SlideElement('right', style='body_text', classes='flex-1'):
                        ui.markdown(self.data.get('right', '')).classes(
                            'text-xl text-white/90 prose prose-invert max-w-none'
                        )
