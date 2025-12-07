"""PictureCaptionSlide - Picture with caption at bottom."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class PictureCaptionSlide(MasterSlide):
    """Picture with caption at bottom.
    
    Elements: background, image, caption
    Data: image, caption
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col'):
            with SlideElement('image', classes='flex-1'):
                image_src = self.data.get('image', '')
                if image_src:
                    ui.image(image_src).classes('w-full h-full object-cover')
            
            with SlideElement('caption', style='caption', classes='p-6 bg-black/50'):
                ui.label(self.data.get('caption', '')).classes(
                    'text-xl text-white/90'
                )
