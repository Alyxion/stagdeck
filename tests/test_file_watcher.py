"""Tests for FileWatcher hot-reload functionality."""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import time

from stagdeck.file_watcher import FileWatcher


class TestFileWatcher:
    """Test FileWatcher basic functionality."""
    
    def test_watch_file(self, tmp_path):
        """Can watch a file."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('initial')
        
        watcher = FileWatcher()
        watcher.watch(test_file)
        
        assert test_file.resolve() in watcher._files
    
    def test_watch_nonexistent_file_ignored(self, tmp_path):
        """Non-existent files are silently ignored."""
        watcher = FileWatcher()
        watcher.watch(tmp_path / 'nonexistent.md')
        
        assert len(watcher._files) == 0
    
    def test_watch_same_file_twice(self, tmp_path):
        """Watching same file twice doesn't duplicate."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('content')
        
        watcher = FileWatcher()
        watcher.watch(test_file)
        watcher.watch(test_file)
        
        assert len(watcher._files) == 1
    
    def test_watch_accepts_string_path(self, tmp_path):
        """Can watch using string path."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('content')
        
        watcher = FileWatcher()
        watcher.watch(str(test_file))
        
        assert test_file.resolve() in watcher._files
    
    def test_on_change_registers_callback(self):
        """Can register change callbacks."""
        watcher = FileWatcher()
        callback = Mock()
        
        watcher.on_change(callback)
        
        assert callback in watcher._callbacks
    
    def test_multiple_callbacks(self):
        """Can register multiple callbacks."""
        watcher = FileWatcher()
        cb1 = Mock()
        cb2 = Mock()
        
        watcher.on_change(cb1)
        watcher.on_change(cb2)
        
        assert len(watcher._callbacks) == 2


class TestFileWatcherAsync:
    """Test FileWatcher async change detection."""
    
    @pytest.mark.asyncio
    async def test_detects_file_change(self, tmp_path):
        """Detects when a watched file changes."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('initial')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(test_file)
        
        callback = Mock()
        watcher.on_change(callback)
        
        # Start watcher in background
        task = asyncio.create_task(watcher.start())
        
        try:
            # Wait a bit, then modify file
            await asyncio.sleep(0.15)
            test_file.write_text('modified')
            
            # Wait for detection
            await asyncio.sleep(0.25)
            
            # Callback should have been called
            assert callback.called
            assert callback.call_args[0][0] == test_file.resolve()
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_multiple_changes(self, tmp_path):
        """Detects multiple changes to same file."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('v1')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(test_file)
        
        callback = Mock()
        watcher.on_change(callback)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            test_file.write_text('v2')
            await asyncio.sleep(0.25)
            
            test_file.write_text('v3')
            await asyncio.sleep(0.25)
            
            assert callback.call_count >= 2
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_watches_multiple_files(self, tmp_path):
        """Can watch multiple files."""
        file1 = tmp_path / 'file1.md'
        file2 = tmp_path / 'file2.md'
        file1.write_text('content1')
        file2.write_text('content2')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(file1)
        watcher.watch(file2)
        
        changed_files = []
        watcher.on_change(lambda p: changed_files.append(p))
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            file1.write_text('modified1')
            await asyncio.sleep(0.25)
            
            file2.write_text('modified2')
            await asyncio.sleep(0.25)
            
            assert file1.resolve() in changed_files
            assert file2.resolve() in changed_files
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_no_callback_without_change(self, tmp_path):
        """Callback not called if file doesn't change."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('content')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(test_file)
        
        callback = Mock()
        watcher.on_change(callback)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.35)
            assert not callback.called
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_stop_stops_watching(self, tmp_path):
        """stop() stops the watcher."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('content')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(test_file)
        
        callback = Mock()
        watcher.on_change(callback)
        
        task = asyncio.create_task(watcher.start())
        
        # Wait for watcher to start, then stop it
        await asyncio.sleep(0.05)
        watcher.stop()
        
        # Wait for the loop to exit
        await asyncio.sleep(0.15)
        
        # Record call count before modification
        calls_before = callback.call_count
        
        # Modify after stop
        test_file.write_text('modified')
        await asyncio.sleep(0.25)
        
        # Should not have detected any new changes after stop
        assert callback.call_count == calls_before
        
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_calls_all_callbacks(self, tmp_path):
        """All registered callbacks are called on change."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('content')
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(test_file)
        
        cb1 = Mock()
        cb2 = Mock()
        cb3 = Mock()
        watcher.on_change(cb1)
        watcher.on_change(cb2)
        watcher.on_change(cb3)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            test_file.write_text('modified')
            await asyncio.sleep(0.25)
            
            assert cb1.called
            assert cb2.called
            assert cb3.called
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class TestFileWatcherWithSlideDeck:
    """Integration tests with SlideDeck."""
    
    def test_source_files_tracked(self, tmp_path):
        """SlideDeck tracks source files from add_from_file."""
        from stagdeck import SlideDeck
        
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Test')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        assert len(deck.source_files) == 1
        assert md_file.resolve() in deck.source_files
    
    def test_multiple_source_files(self, tmp_path):
        """Can track multiple source files."""
        from stagdeck import SlideDeck
        
        file1 = tmp_path / 'intro.md'
        file2 = tmp_path / 'content.md'
        file1.write_text('# Intro')
        file2.write_text('# Content')
        
        deck = SlideDeck()
        deck.add_from_file(file1)
        deck.add_from_file(file2)
        
        assert len(deck.source_files) == 2
        assert file1.resolve() in deck.source_files
        assert file2.resolve() in deck.source_files
    
    @pytest.mark.asyncio
    async def test_watcher_with_deck_source_files(self, tmp_path):
        """FileWatcher works with deck's source files."""
        from stagdeck import SlideDeck
        
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Original')
        
        deck = SlideDeck()
        deck.add_from_file(md_file)
        
        watcher = FileWatcher(check_interval=0.1)
        for source_file in deck.source_files:
            watcher.watch(source_file)
        
        callback = Mock()
        watcher.on_change(callback)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            md_file.write_text('# Modified')
            await asyncio.sleep(0.25)
            
            assert callback.called
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class TestFileWatcherReload:
    """Test reload workflow simulation."""
    
    @pytest.mark.asyncio
    async def test_reload_on_change(self, tmp_path):
        """Simulates reload workflow when file changes."""
        from stagdeck import SlideDeck
        
        md_file = tmp_path / 'slides.md'
        md_file.write_text('''[name: intro]
# Original Title
''')
        
        # Create deck factory (like App.run uses)
        def create_deck():
            deck = SlideDeck()
            deck.add_from_file(md_file)
            return deck
        
        # Initial load
        deck = create_deck()
        assert deck.slides[0].title == 'Original Title'
        
        # Setup watcher
        watcher = FileWatcher(check_interval=0.1)
        for source_file in deck.source_files:
            watcher.watch(source_file)
        
        reload_count = [0]
        
        def on_change(path):
            nonlocal deck
            deck = create_deck()  # Reload
            reload_count[0] += 1
        
        watcher.on_change(on_change)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            
            # Modify the file
            md_file.write_text('''[name: intro]
# Updated Title
''')
            
            await asyncio.sleep(0.25)
            
            # Deck should have been reloaded
            assert reload_count[0] >= 1
            assert deck.slides[0].title == 'Updated Title'
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_add_slide_triggers_reload(self, tmp_path):
        """Adding a slide to markdown triggers reload."""
        from stagdeck import SlideDeck
        
        md_file = tmp_path / 'slides.md'
        md_file.write_text('# Slide 1')
        
        def create_deck():
            deck = SlideDeck()
            deck.add_from_file(md_file)
            return deck
        
        deck = create_deck()
        assert len(deck.slides) == 1
        
        watcher = FileWatcher(check_interval=0.1)
        watcher.watch(md_file)
        
        def on_change(path):
            nonlocal deck
            deck = create_deck()
        
        watcher.on_change(on_change)
        
        task = asyncio.create_task(watcher.start())
        
        try:
            await asyncio.sleep(0.15)
            
            # Add a slide
            md_file.write_text('''# Slide 1

---

# Slide 2
''')
            
            await asyncio.sleep(0.25)
            
            assert len(deck.slides) == 2
        finally:
            watcher.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
