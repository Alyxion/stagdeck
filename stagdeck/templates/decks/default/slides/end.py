"""EndSlide - Closing slide with thank you message."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class EndSlide(MasterSlide):
    """Closing slide with thank you message.
    
    Elements: background, title, subtitle, contact
    Data: title (default: "Thank You"), subtitle, contact
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col items-center justify-center'):
            with SlideElement('title', style='title', classes='text-center'):
                ui.label(self.data.get('title', 'Thank You')).classes(
                    'text-7xl font-bold text-white'
                )
            
            if self.data.get('subtitle'):
                with SlideElement('subtitle', style='subtitle', classes='text-center mt-6'):
                    ui.label(self.data.get('subtitle', '')).classes(
                        'text-3xl text-white/80'
                    )
            
            if self.data.get('contact'):
                with SlideElement('contact', style='caption', classes='text-center mt-12'):
                    ui.markdown(self.data.get('contact', '')).classes(
                        'text-xl text-white/60 prose prose-invert'
                    )
