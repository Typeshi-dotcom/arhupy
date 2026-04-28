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

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise Exception(f"Prompt library '{LIBRARY_FILE}' is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise Exception(f"Prompt library '{LIBRARY_FILE}' must contain a JSON object.")
    return data


def _write_library(data):
    """Write prompt templates to the local library JSON file."""
    path = _library_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
        file.write("\n")


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
    count = len(data)
    if not data:
        print("Saved prompts: 0")
        print("No saved prompts found.")
        return

    label = "prompt" if count == 1 else "prompts"
    print(f"Saved prompts: {count} {label}")
    for name in sorted(data):
        print(f"- {name}")


def delete(name):
    """Remove a prompt from the local prompt library."""
    data = _read_library()
    if name not in data:
        raise KeyError(f"Prompt '{name}' was not found in the library.")

    del data[name]
    _write_library(data)


def export_all(filepath):
    """Export the entire local prompt library to a JSON file."""
    data = _read_library()
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
            file.write("\n")
    except OSError as exc:
        raise Exception(f"Could not export prompt library to '{filepath}': {exc}") from exc


def import_all(filepath):
    """Import prompts from a JSON file without overwriting existing names."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            incoming = json.load(file)
    except OSError as exc:
        raise Exception(f"Could not read prompt library file '{filepath}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise Exception(f"Prompt library file '{filepath}' is not valid JSON.") from exc

    if not isinstance(incoming, dict):
        raise Exception(f"Prompt library file '{filepath}' must contain a JSON object.")

    data = _read_library()
    imported = []
    skipped = []
    for name, template in incoming.items():
        if not isinstance(name, str) or not isinstance(template, str):
            skipped.append(str(name))
            continue
        if name in data:
            skipped.append(name)
            continue
        data[name] = template
        imported.append(name)

    _write_library(data)
    return {
        "imported": sorted(imported),
        "skipped": sorted(skipped),
    }
