"""
NextPy Enhanced Development Server with hot reload and optimization
"""

import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable, List


class OptimizedDevServer(FileSystemEventHandler):
    """Development server with file watching and hot reload"""
    
    def __init__(self, on_change: Callable):
        self.on_change = on_change
        self.debounce_timer = None
        self.debounce_delay = 0.5  # seconds
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        # Debounce rapid changes
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = asyncio.Timer(
            self.debounce_delay,
            lambda: self.on_change(event.src_path)
        )
        self.debounce_timer.start()
    
    @staticmethod
    def watch_directories(paths: List[Path], on_change: Callable):
        """Watch multiple directories for changes"""
        observer = Observer()
        handler = OptimizedDevServer(on_change)
        
        for path in paths:
            observer.schedule(handler, str(path), recursive=True)
        
        observer.start()
        return observer


class DevServerStats:
    """Track development server statistics"""
    
    def __init__(self):
        self.hot_reloads = 0
        self.build_time = 0
        self.files_changed = []
    
    def record_reload(self, file_path: str, build_time: float):
        """Record a hot reload event"""
        self.hot_reloads += 1
        self.build_time = build_time
        self.files_changed.append(file_path)
    
    def get_stats(self) -> dict:
        """Get server statistics"""
        return {
            "hot_reloads": self.hot_reloads,
            "last_build_time_ms": round(self.build_time * 1000, 2),
            "files_changed": len(self.files_changed),
            "recent_changes": self.files_changed[-5:]
        }
