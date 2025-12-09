"""Tests for SlideDeck class."""

import pytest
from pathlib import Path
import tempfile
import os

from stagdeck import SlideDeck


class TestSlideDeckMediaFolder:
    """Test media folder functionality."""
    
    def test_add_media_folder(self, tmp_path):
        """Can add a media folder."""
        deck = SlideDeck()
        media_dir = tmp_path / 'media'
        media_dir.mkdir()
        
        deck.add_media_folder(media_dir, '/media')
        
        assert '/media' in deck.media_folders
        assert deck.media_folders['/media'] == media_dir.resolve()
    
    def test_add_media_folder_chaining(self, tmp_path):
        """add_media_folder returns self for chaining."""
        deck = SlideDeck()
        media_dir = tmp_path / 'media'
        media_dir.mkdir()
        
        result = deck.add_media_folder(media_dir)
        
        assert result is deck
    
    def test_add_media_folder_normalizes_url_path(self, tmp_path):
        """URL path is normalized to start with / and not end with /."""
        deck = SlideDeck()
        media_dir = tmp_path / 'media'
        media_dir.mkdir()
        
        deck.add_media_folder(media_dir, 'assets/')
        
        assert '/assets' in deck.media_folders
    
    def test_add_media_folder_nonexistent_raises(self):
        """Raises ValueError for non-existent folder."""
        deck = SlideDeck()
        
        with pytest.raises(ValueError, match="does not exist"):
            deck.add_media_folder('/nonexistent/path')
    
    def test_add_media_folder_file_raises(self, tmp_path):
        """Raises ValueError if path is a file, not directory."""
        deck = SlideDeck()
        file_path = tmp_path / 'file.txt'
        file_path.write_text('test')
        
        with pytest.raises(ValueError, match="not a directory"):
            deck.add_media_folder(file_path)
    
    def test_multiple_media_folders(self, tmp_path):
        """Can add multiple media folders."""
        deck = SlideDeck()
        
        images_dir = tmp_path / 'images'
        images_dir.mkdir()
        
        videos_dir = tmp_path / 'videos'
        videos_dir.mkdir()
        
        deck.add_media_folder(images_dir, '/images')
        deck.add_media_folder(videos_dir, '/videos')
        
        assert len(deck.media_folders) == 2
        assert '/images' in deck.media_folders
        assert '/videos' in deck.media_folders


class TestSlideDeckMarkdownAdd:
    """Test markdown-first add() method."""
    
    def test_add_with_markdown_title(self):
        """Can add slide with title from markdown."""
        deck = SlideDeck()
        deck.add('# Hello World')
        
        assert len(deck.slides) == 1
        assert deck.slides[0].title == 'Hello World'
    
    def test_add_with_markdown_title_subtitle(self):
        """Can add slide with title and subtitle from markdown."""
        deck = SlideDeck()
        deck.add('''
# Main Title
## Subtitle
''')
        assert deck.slides[0].title == 'Main Title'
        assert deck.slides[0].subtitle == 'Subtitle'
    
    def test_add_with_markdown_background(self):
        """Can add slide with background from markdown."""
        deck = SlideDeck()
        deck.add('''
![background](#1a1a2e)

# Title
''')
        assert deck.slides[0].background_color == '#1a1a2e'
    
    def test_add_with_markdown_background_image(self):
        """Can add slide with background image from markdown."""
        deck = SlideDeck()
        deck.add('''
![background](image.jpg)

# Title
''')
        assert deck.slides[0].background_color == 'url(image.jpg)'
    
    def test_add_explicit_overrides_markdown(self):
        """Explicit parameters override markdown values."""
        deck = SlideDeck()
        deck.add('''
# Markdown Title
''', title='Explicit Title')
        
        assert deck.slides[0].title == 'Explicit Title'
    
    def test_add_backward_compatible(self):
        """Old-style add() still works."""
        deck = SlideDeck()
        deck.add(
            title='My Title',
            content='My content',
            background='#000',
        )
        
        assert deck.slides[0].title == 'My Title'
        assert deck.slides[0].content == 'My content'
        assert deck.slides[0].background_color == '#000'
    
    def test_add_background_color_alias(self):
        """background_color parameter still works (backward compat)."""
        deck = SlideDeck()
        deck.add(
            title='Title',
            background_color='#fff',
        )
        
        assert deck.slides[0].background_color == '#fff'
