"""JSON export and import helpers for prompts and prompt chains."""

import json

from .chain import PromptChain
from .prompt import Prompt


def export_prompt(prompt, filepath):
    """Save a Prompt object to a pretty-formatted JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(prompt.to_dict(), file, indent=2, sort_keys=True)
            file.write("\n")
    except OSError as exc:
        raise Exception(f"Could not export prompt to '{filepath}': {exc}") from exc


def import_prompt(filepath):
    """Load a Prompt object from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise Exception(f"Could not read prompt file '{filepath}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise Exception(f"Prompt file '{filepath}' is not valid JSON.") from exc

    try:
        return Prompt.from_dict(data)
    except ValueError as exc:
        raise Exception(f"Prompt file '{filepath}' is not valid prompt data: {exc}") from exc


def export_chain(chain, filepath):
    """Save a PromptChain object to a pretty-formatted JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(chain.to_dict(), file, indent=2, sort_keys=True)
            file.write("\n")
    except OSError as exc:
        raise Exception(f"Could not export prompt chain to '{filepath}': {exc}") from exc


def import_chain(filepath):
    """Load a PromptChain object from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise Exception(f"Could not read prompt chain file '{filepath}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise Exception(f"Prompt chain file '{filepath}' is not valid JSON.") from exc

    try:
        return PromptChain.from_dict(data)
    except ValueError as exc:
        message = f"Prompt chain file '{filepath}' is not valid chain data: {exc}"
        raise Exception(message) from exc
