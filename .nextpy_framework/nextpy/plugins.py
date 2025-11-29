"""
NextPy Plugin System - Extend framework functionality
"""

from typing import Callable, Dict, Any, List
from abc import ABC, abstractmethod


class Plugin(ABC):
    """Base plugin class"""
    
    name: str = "Plugin"
    version: str = "1.0.0"
    
    @abstractmethod
    def on_init(self, app):
        """Called when app initializes"""
        pass
    
    @abstractmethod
    def on_request(self, request):
        """Called on each request"""
        pass
    
    @abstractmethod
    def on_response(self, response):
        """Called on each response"""
        pass


class PluginManager:
    """Manage plugins"""
    
    def __init__(self):
        self.plugins: List[Plugin] = []
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins.append(plugin)
    
    def register_hook(self, name: str, callback: Callable):
        """Register a hook"""
        if name not in self.hooks:
            self.hooks[name] = []
        self.hooks[name].append(callback)
    
    async def trigger(self, name: str, *args, **kwargs):
        """Trigger a hook"""
        if name in self.hooks:
            for callback in self.hooks[name]:
                await callback(*args, **kwargs)


# Global plugin manager
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager"""
    return _plugin_manager
