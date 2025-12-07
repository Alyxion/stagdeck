"""PictureSlide - Full-bleed picture slide."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class PictureSlide(MasterSlide):
    """Full-bleed picture slide.
    
    Elements: background, image
    Data: image (path/url)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('image', classes='absolute inset-0'):
            image_src = self.data.get('image', '')
            if image_src:
                ui.image(image_src).classes('w-full h-full object-cover')
