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

    data[share_id] = prompt_text
    _write_shared(data)
    return share_id


def get_shared(share_id):
    """Return a shared prompt by ID."""
    data = _read_shared()
    prompt = data.get(share_id)
    if prompt is None:
        raise Exception(f"Shared prompt not found: {share_id}")
    return prompt


def get_all_shared():
    """Return all shared prompts with their IDs and prompt text."""
    data = _read_shared()
    return [
        {"id": share_id, "prompt": prompt}
        for share_id, prompt in sorted(data.items())
    ]


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
    with open(SHARED_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
