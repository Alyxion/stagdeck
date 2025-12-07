"""Slide layouts for the default master deck."""

from .title import TitleSlide
from .section import SectionSlide
from .content import ContentSlide
from .two_column import TwoColumnSlide
from .comparison import ComparisonSlide
from .three_column import ThreeColumnSlide
from .picture import PictureSlide
from .picture_caption import PictureCaptionSlide
from .text_picture import TextPictureSlide
from .quote import QuoteSlide
from .name_card import NameCardSlide
from .blank import BlankSlide
from .end import EndSlide

__all__ = [
    'TitleSlide',
    'SectionSlide',
    'ContentSlide',
    'TwoColumnSlide',
    'ComparisonSlide',
    'ThreeColumnSlide',
    'PictureSlide',
    'PictureCaptionSlide',
    'TextPictureSlide',
    'QuoteSlide',
    'NameCardSlide',
    'BlankSlide',
    'EndSlide',
]
