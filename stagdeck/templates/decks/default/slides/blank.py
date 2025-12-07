"""BlankSlide - Blank slide for custom content."""

from ..master import MasterSlide


class BlankSlide(MasterSlide):
    """Blank slide for custom content.
    
    Elements: background only
    Data: none (use builder for custom content)
    """
    
    async def build(self):
        await super().build()
        # Just background, no additional elements
