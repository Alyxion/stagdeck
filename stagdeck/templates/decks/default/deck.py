"""Factory function to create the default master deck."""

from stagdeck.slide_deck import SlideDeck
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


def create_default_master() -> SlideDeck:
    """Create the default master deck with all standard layouts.
    
    Returns a SlideDeck containing all layout slides that can be
    used as a master for presentation decks.
    
    :return: SlideDeck with standard layouts registered.
    
    Example:
        >>> master = create_default_master()
        >>> deck = SlideDeck(title='My Talk', master=master)
        >>> deck.add(layout='title', title='Hello World')
    """
    master = SlideDeck(title='Default Master')
    
    # Title & Opening
    master.add_slide(TitleSlide(name='title'))
    master.add_slide(SectionSlide(name='section'))
    
    # Content
    master.add_slide(ContentSlide(name='content'))
    master.add_slide(TwoColumnSlide(name='two_column'))
    master.add_slide(ComparisonSlide(name='comparison'))
    master.add_slide(ThreeColumnSlide(name='three_column'))
    
    # Pictures
    master.add_slide(PictureSlide(name='picture'))
    master.add_slide(PictureCaptionSlide(name='picture_caption'))
    master.add_slide(TextPictureSlide(name='text_picture'))
    
    # Special
    master.add_slide(QuoteSlide(name='quote'))
    master.add_slide(NameCardSlide(name='name_card'))
    master.add_slide(BlankSlide(name='blank'))
    master.add_slide(EndSlide(name='end'))
    
    return master
