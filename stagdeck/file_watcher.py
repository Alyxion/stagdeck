"""👁️ FileWatcher - Watch files for changes and trigger hot-reload."""

import asyncio
from pathlib import Path
from typing import Callable


class FileWatcher:
    """Watch files for changes and trigger callbacks.
    
    Each DeckViewer instance has its own FileWatcher.
    Components register files via the viewer's `register_watched_file()` method.
    
    Example:
        >>> watcher = FileWatcher()
        >>> watcher.watch(Path('slides.md'))
        >>> watcher.on_change(lambda p: print(f'Changed: {p}'))
        >>> await watcher.start()
    """
    
    def __init__(self, check_interval: float = 0.5):
        """Initialize the file watcher.
        
        :param check_interval: How often to check for changes (seconds).
        """
        self.check_interval = check_interval
        self._files: dict[Path, float] = {}  # path -> last mtime
        self._callbacks: list[Callable[[Path], None]] = []
        self._running = False
    
    def watch(self, path: Path | str) -> None:
        """Add a file to watch.
        
        :param path: Path to the file to watch.
        """
        path = Path(path).resolve()
        if path.exists() and path not in self._files:
            self._files[path] = path.stat().st_mtime
    
    def on_change(self, callback: Callable[[Path], None]) -> None:
        """Register a callback for file changes.
        
        :param callback: Function called with the changed file path.
        """
        self._callbacks.append(callback)
    
    async def start(self) -> None:
        """Start watching files for changes."""
        self._running = True
        while self._running:
            await asyncio.sleep(self.check_interval)
            for path, last_mtime in list(self._files.items()):
                if path.exists():
                    current_mtime = path.stat().st_mtime
                    if current_mtime > last_mtime:
                        self._files[path] = current_mtime
                        for callback in self._callbacks:
                            callback(path)
    
    def stop(self) -> None:
        """Stop watching files."""
        self._running = False
