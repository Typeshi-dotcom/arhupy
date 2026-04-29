"""Local share-link storage for prompts."""

import json
import random
import string

SHARED_FILE = "arhupy_shared.json"


def generate_id():
    """Generate a short random share ID."""
    alphabet = string.ascii_lowercase + string.digits
    length = random.randint(6, 8)
    return "".join(random.choice(alphabet) for _ in range(length))


def save_shared(prompt):
    """Save a prompt and return its share ID."""
    prompt_text = str(prompt)
    data = _read_shared()
    share_id = generate_id()
    while share_id in data:
        share_id = generate_id()

    data[share_id] = {
        "id": share_id,
        "prompt": prompt_text,
        "upvotes": 0,
    }
    _write_shared(data)
    return share_id


def get_shared(share_id):
    """Return a shared prompt by ID."""
    return _get_shared_entry(share_id)["prompt"]


def get_all_shared():
    """Return all shared prompts with IDs, prompt text, and upvotes."""
    data = _read_shared()
    return [
        _normalize_entry(share_id, value)
        for share_id, value in sorted(data.items())
    ]


def upvote_prompt(share_id):
    """Increment and return the upvote count for a shared prompt."""
    data = _read_shared()
    if share_id not in data:
        raise Exception(f"Shared prompt not found: {share_id}")

    entry = _normalize_entry(share_id, data[share_id])
    entry["upvotes"] += 1
    data[share_id] = entry
    _write_shared(data)
    return entry["upvotes"]


def get_trending():
    """Return shared prompts sorted by upvotes, highest first."""
    return sorted(
        get_all_shared(),
        key=lambda item: (-item["upvotes"], item["id"]),
    )


def _get_shared_entry(share_id):
    """Return normalized shared prompt data by ID."""
    data = _read_shared()
    value = data.get(share_id)
    if value is None:
        raise Exception(f"Shared prompt not found: {share_id}")
    return _normalize_entry(share_id, value)


def _normalize_entry(share_id, value):
    """Normalize legacy and current shared prompt entries."""
    if isinstance(value, str):
        return {
            "id": share_id,
            "prompt": value,
            "upvotes": 0,
        }

    if not isinstance(value, dict):
        raise Exception(f"Shared prompt entry is invalid: {share_id}")

    prompt = value.get("prompt", "")
    if not isinstance(prompt, str):
        prompt = str(prompt)

    try:
        upvotes = int(value.get("upvotes", 0))
    except (TypeError, ValueError):
        upvotes = 0

    return {
        "id": share_id,
        "prompt": prompt,
        "upvotes": max(upvotes, 0),
    }


def _read_shared():
    """Read shared prompt data from local JSON storage."""
    try:
        with open(SHARED_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise Exception(f"{SHARED_FILE} is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise Exception(f"{SHARED_FILE} must contain a JSON object.")
    return data


def _write_shared(data):
    """Write shared prompt data to local JSON storage."""
    normalized = {
        share_id: _normalize_entry(share_id, value)
        for share_id, value in data.items()
    }
    with open(SHARED_FILE, "w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2)
        file.write("\n")
