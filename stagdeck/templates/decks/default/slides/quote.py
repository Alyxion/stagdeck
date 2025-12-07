"""QuoteSlide - Quote with attribution."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class QuoteSlide(MasterSlide):
    """Quote with attribution.
    
    Elements: background, quote, attribution
    Data: quote, attribution
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex flex-col items-center justify-center p-20'):
            with SlideElement('quote', style='quote', classes='text-center max-w-4xl'):
                ui.label(f'"{self.data.get("quote", "")}"').classes(
                    'text-4xl italic text-white/90 leading-relaxed'
                )
            
            if self.data.get('attribution'):
                with SlideElement('attribution', style='attribution', classes='mt-8'):
                    ui.label(f'— {self.data.get("attribution", "")}').classes(
                        'text-2xl text-white/70'
                    )
