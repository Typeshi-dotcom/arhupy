"""Prompt history helpers for recently used prompts."""

import json
from datetime import datetime, timezone
from pathlib import Path

from .diff import compare_prompts

HISTORY_FILE = "arhupy_history.json"


def _history_path():
    """Return the history file path in the current working directory."""
    return Path.cwd() / HISTORY_FILE


def _read_history():
    """Read prompt history from the local history JSON file."""
    path = _history_path()
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise Exception(f"History file is not valid JSON: {path}") from exc
    except OSError as exc:
        raise Exception(f"Could not read history file: {path}") from exc

    if not isinstance(data, list):
        raise Exception(f"History file must contain a list: {path}")
    return data


def _write_history(entries):
    """Write prompt history to the local history JSON file."""
    _write_json_file(_history_path(), entries)


def _read_json_file(path):
    """Read JSON data from a file path."""
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise Exception(f"History file is not valid JSON: {path}") from exc
    except OSError as exc:
        raise Exception(f"Could not read history file: {path}") from exc


def _write_json_file(path, data):
    """Write JSON data to a file path."""
    try:
        with Path(path).open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError as exc:
        raise Exception(f"Could not write history file: {path}") from exc


def _validate_history_entries(entries):
    """Validate history data loaded from JSON."""
    if not isinstance(entries, list):
        raise Exception("History data must be a list.")
    for entry in entries:
        if not isinstance(entry, dict):
            raise Exception("Each history entry must be a dictionary.")
        if not isinstance(entry.get("prompt"), str):
            raise Exception("Each history entry must include prompt text.")
        if not isinstance(entry.get("timestamp"), str):
            raise Exception("Each history entry must include a timestamp.")
    return entries


def add_history(prompt):
    """Save a prompt to history with a timestamp."""
    prompt_text = "" if prompt is None else str(prompt).strip()
    if not prompt_text:
        return None

    entries = _read_history()
    entry = {
        "prompt": prompt_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entries.insert(0, entry)
    _write_history(entries)
    return entry


def get_history(limit=None):
    """Return recent prompt history entries, optionally limited."""
    entries = _read_history()
    if limit is None:
        return entries

    try:
        count = int(limit)
    except (TypeError, ValueError) as exc:
        raise Exception("History limit must be an integer.") from exc

    if count < 0:
        raise Exception("History limit must be zero or greater.")
    return entries[:count]


def get_prompt_by_index(index):
    """Return the prompt at a one-based history index, where latest is 1."""
    try:
        prompt_index = int(index)
    except (TypeError, ValueError) as exc:
        raise Exception("History index must be an integer.") from exc

    if prompt_index < 1:
        raise Exception("History index must be 1 or greater.")

    entries = _read_history()
    if prompt_index > len(entries):
        raise Exception(f"No prompt found at history index {index}.")
    return entries[prompt_index - 1]["prompt"]


def compare_history(index1, index2):
    """Compare two prompts from history by one-based indexes."""
    prompt_1 = get_prompt_by_index(index1)
    prompt_2 = get_prompt_by_index(index2)
    return {
        "prompt_1": prompt_1,
        "prompt_2": prompt_2,
        "comparison": compare_prompts(prompt_1, prompt_2),
    }


def export_history(filepath):
    """Export the full prompt history to a JSON file."""
    entries = _read_history()
    _write_json_file(filepath, entries)


def import_history(filepath):
    """Import prompt history from JSON, merging without duplicates."""
    incoming = _validate_history_entries(_read_json_file(filepath))
    current = _read_history()
    seen = {
        (entry.get("prompt"), entry.get("timestamp"))
        for entry in current
    }
    imported = []

    for entry in incoming:
        key = (entry["prompt"], entry["timestamp"])
        if key in seen:
            continue
        current.append(entry)
        seen.add(key)
        imported.append(entry)

    _write_history(current)
    return {
        "imported": imported,
        "skipped": len(incoming) - len(imported),
    }
