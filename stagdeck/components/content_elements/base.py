"""Base class for content elements."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# Conversion factor: rem to px for 1920x1080 slides
# Base 16px * rem value * scale factor for good sizing on 1920px slides
REM_TO_PX_FACTOR = 20


@dataclass
class ContentStyle:
    """Style configuration for content elements."""
    font_size: float = 1.8  # rem
    line_height: float = 1.6
    color: str = ''


class ContentElement(ABC):
    """Base class for all content elements.
    
    Content elements wrap NiceGUI's markdown with explicit size control
    for consistent rendering across browser and render endpoints.
    """
    
    def __init__(self, content: str, font_size: float = 1.8):
        """Initialize content element.
        
        :param content: Markdown content to render.
        :param font_size: Font size in rem (converted to px internally).
        """
        self.content = content
        self.font_size = font_size
    
    @property
    def px_size(self) -> float:
        """Convert rem font size to pixels."""
        return self.font_size * REM_TO_PX_FACTOR
    
    @abstractmethod
    async def build(self) -> None:
        """Build the content element UI."""
        pass
