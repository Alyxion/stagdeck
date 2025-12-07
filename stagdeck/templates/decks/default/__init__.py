"""Default master deck with standard slide layouts."""

from .master import MasterSlide
from .slides import (
    TitleSlide,
    ContentSlide,
    SectionSlide,
    TwoColumnSlide,
    ComparisonSlide,
    ThreeColumnSlide,
    PictureSlide,
    PictureCaptionSlide,
    TextPictureSlide,
    QuoteSlide,
    NameCardSlide,
    BlankSlide,
    EndSlide,
)
from .deck import create_default_master

__all__ = [
    'MasterSlide',
    'TitleSlide',
    'ContentSlide',
    'SectionSlide',
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
    'create_default_master',
]
