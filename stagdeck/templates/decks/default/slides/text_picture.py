"""TextPictureSlide - Text on left, picture on right."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class TextPictureSlide(MasterSlide):
    """Text on left, picture on right.
    
    Elements: background, title, content (text, image)
    Data: title, text (markdown), image
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col p-16'):
            with SlideElement('title', style='title', classes='mb-8'):
                ui.label(self.data.get('title', '')).classes(
                    'text-5xl font-bold text-white'
                )
            
            with SlideElement('body', classes='flex-1 flex gap-12'):
                with SlideElement('text', style='body_text', classes='flex-1'):
                    ui.markdown(self.data.get('text', '')).classes(
                        'text-xl text-white/90 prose prose-invert max-w-none'
                    )
                
                with SlideElement('image', classes='flex-1'):
                    image_src = self.data.get('image', '')
                    if image_src:
                        ui.image(image_src).classes('w-full h-full object-contain')
