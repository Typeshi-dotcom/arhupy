"""Version tracking helpers for prompts."""

import json
from pathlib import Path

VERSIONS_FILE = "arhupy_versions.json"


def _versions_path():
    """Return the versions file path in the current working directory."""
    return Path.cwd() / VERSIONS_FILE


def _read_versions():
    """Read prompt version data from the local versions JSON file."""
    path = _versions_path()
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_versions(data):
    """Write prompt version data to the local versions JSON file."""
    path = _versions_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)


def save_version(name, prompt, version, notes=""):
    """Save a versioned snapshot of a Prompt template."""
    data = _read_versions()
    history = data.setdefault(name, [])
    history.append(
        {
            "version": version,
            "template": prompt.template,
            "notes": notes,
        }
    )
    _write_versions(data)


def get_history(name):
    """Return all saved versions for a prompt name."""
    data = _read_versions()
    return data.get(name, [])


def print_history(name):
    """Print a clean readable version history for a prompt name."""
    history = get_history(name)
    if not history:
        print(f"No version history found for '{name}'.")
        return

    print(f"Version history for '{name}':")
    for entry in history:
        version = entry.get("version", "")
        notes = entry.get("notes", "")
        template = entry.get("template", "")
        print(f"- Version {version}")
        print(f"  Template: {template}")
        if notes:
            print(f"  Notes: {notes}")
