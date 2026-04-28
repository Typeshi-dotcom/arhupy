"""Local JSON prompt library helpers."""

import json
from pathlib import Path

from .prompt import Prompt

LIBRARY_FILE = "arhupy_library.json"


def _library_path():
    """Return the library file path in the current working directory."""
    return Path.cwd() / LIBRARY_FILE


def _read_library():
    """Read prompt templates from the local library JSON file."""
    path = _library_path()
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_library(data):
    """Write prompt templates to the local library JSON file."""
    path = _library_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)


def save(name, prompt):
    """Save a Prompt template to the local prompt library."""
    data = _read_library()
    data[name] = prompt.template
    _write_library(data)


def load(name):
    """Load a Prompt object from the local prompt library by name."""
    data = _read_library()
    if name not in data:
        raise KeyError(f"Prompt '{name}' was not found in the library.")
    return Prompt(data[name])


def list_all():
    """Print all saved prompt names in the local prompt library."""
    data = _read_library()
    if not data:
        print("No saved prompts found.")
        return

    for name in sorted(data):
        print(name)


def delete(name):
    """Remove a prompt from the local prompt library."""
    data = _read_library()
    if name not in data:
        raise KeyError(f"Prompt '{name}' was not found in the library.")

    del data[name]
    _write_library(data)
