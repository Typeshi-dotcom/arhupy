"""Prompt history helpers for recently used prompts."""

import json
from datetime import datetime, timezone
from pathlib import Path

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
    path = _history_path()
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(entries, file, indent=2)
    except OSError as exc:
        raise Exception(f"Could not write history file: {path}") from exc


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
