"""AI-powered prompt improvement helpers."""

from .claude import ClaudeClient

PLACEHOLDER_API_KEYS = {"YOUR_KEY", "YOUR_API_KEY"}

IMPROVEMENT_TEMPLATE = """Improve this prompt to make it clearer, more structured, and more effective:

PROMPT:
{text}

Return only the improved version."""


def improve_prompt(text, api_key):
    """Improve a prompt using Claude and return the improved prompt text."""
    prompt_text = "" if text is None else str(text).strip()
    if not prompt_text:
        raise Exception("Prompt text is required to improve prompts.")
    if not api_key or not str(api_key).strip():
        raise Exception("A Claude API key is required to improve prompts.")

    api_key_text = str(api_key).strip()
    if _is_placeholder_key(api_key_text):
        return _demo_improvement(prompt_text)

    client = ClaudeClient(api_key=api_key_text)
    request_text = IMPROVEMENT_TEMPLATE.format(text=prompt_text)
    try:
        return client.ask(request_text)
    except Exception as exc:
        raise Exception(f"Could not improve prompt: {exc}") from exc


def _is_placeholder_key(api_key):
    """Return True when the API key is a documented placeholder value."""
    return api_key.upper() in PLACEHOLDER_API_KEYS


def _demo_improvement(prompt_text):
    """Return a local demo improvement without calling the Claude API."""
    return (
        f"{prompt_text}\n\n"
        "Please provide a clear, structured, and actionable response. "
        "Include relevant context, practical examples, and any important constraints."
    )
