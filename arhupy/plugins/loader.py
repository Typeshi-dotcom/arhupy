"""Plugin loading helpers for arhupy."""

import importlib
import inspect
from pathlib import Path
import pkgutil

from .base import ArhupyPlugin

_PLUGINS = {}


def load_plugins():
    """Load available plugins and return a dictionary of plugin instances."""
    global _PLUGINS

    plugins = {}
    package_name = __package__
    package_path = [str(Path(__file__).resolve().parent)]

    for module_info in pkgutil.iter_modules(package_path):
        module_name = module_info.name
        if module_name.startswith("_") or module_name in {"base", "loader"}:
            continue

        module = importlib.import_module(f"{package_name}.{module_name}")
        for _, plugin_class in inspect.getmembers(module, inspect.isclass):
            if not issubclass(plugin_class, ArhupyPlugin) or plugin_class is ArhupyPlugin:
                continue
            plugin = plugin_class()
            if plugin.name and plugin.name not in plugins:
                plugins[plugin.name] = plugin

    _PLUGINS = plugins
    return dict(_PLUGINS)


def get_plugin(name):
    """Return a loaded plugin by name."""
    if not _PLUGINS:
        load_plugins()

    plugin = _PLUGINS.get(name)
    if plugin is None:
        raise Exception(f"Plugin not found: {name}")
    return plugin
