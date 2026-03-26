"""
Plugin system for claude-wrap input filters.

To create a custom filter plugin:

    from claude_wrap.plugins import FilterPlugin, registry

    class MyFilter(FilterPlugin):
        def filter(self, data: bytes) -> bytes:
            # transform data here
            return data

    registry.register(MyFilter())

Plugins are applied in registration order on every stdin chunk
before it reaches the Claude Code process.
"""

from abc import ABC, abstractmethod


class FilterPlugin(ABC):
    """Base class for all stdin filter plugins."""

    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def filter(self, data: bytes) -> bytes:
        """Transform raw stdin bytes. Return the (possibly modified) bytes."""
        ...


class PluginRegistry:
    """Ordered registry of active FilterPlugin instances."""

    def __init__(self) -> None:
        self._plugins: list[FilterPlugin] = []

    def register(self, plugin: FilterPlugin) -> None:
        """Append a plugin to the filter pipeline."""
        self._plugins.append(plugin)

    def unregister(self, name: str) -> bool:
        """Remove the first plugin whose name matches. Returns True if removed."""
        for i, p in enumerate(self._plugins):
            if p.name == name:
                del self._plugins[i]
                return True
        return False

    def apply(self, data: bytes) -> bytes:
        """Run data through all registered plugins in order."""
        for plugin in self._plugins:
            data = plugin.filter(data)
        return data

    def list_plugins(self) -> list[str]:
        return [p.name for p in self._plugins]


# Global registry — import this to add your own plugins
registry = PluginRegistry()
