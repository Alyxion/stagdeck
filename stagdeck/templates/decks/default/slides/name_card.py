"""NameCardSlide - Person introduction card."""

from nicegui import ui

from stagdeck.slide_element import SlideElement
from ..master import MasterSlide


class NameCardSlide(MasterSlide):
    """Person introduction card.
    
    Elements: background, image, name, role, bio
    Data: image, name, role, bio (optional)
    """
    
    async def build(self):
        await super().build()
        
        with SlideElement('content', classes='absolute inset-0 flex items-center justify-center gap-16 p-16'):
            # Photo
            with SlideElement('image', classes='w-80 h-80 rounded-full overflow-hidden'):
                image_src = self.data.get('image', '')
                if image_src:
                    ui.image(image_src).classes('w-full h-full object-cover')
                else:
                    ui.element('div').classes('w-full h-full bg-white/20')
            
            # Info
            with SlideElement('info', classes='flex flex-col'):
                with SlideElement('name', style='name', classes=''):
                    ui.label(self.data.get('name', '')).classes(
                        'text-5xl font-bold text-white'
                    )
                
                with SlideElement('role', style='role', classes='mt-2'):
                    ui.label(self.data.get('role', '')).classes(
                        'text-2xl text-white/70'
                    )
                
                if self.data.get('bio'):
                    with SlideElement('bio', style='body_text', classes='mt-6 max-w-lg'):
                        ui.markdown(self.data.get('bio', '')).classes(
                            'text-lg text-white/80 prose prose-invert'
                        )
