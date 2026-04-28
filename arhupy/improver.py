"""AI-powered prompt improvement helpers."""

from .claude import ClaudeClient

IMPROVEMENT_TEMPLATE = """Improve this prompt to make it clearer, more structured, and more effective:

PROMPT:
{text}

Return only the improved version."""


def improve_prompt(text, api_key):
    """Improve a prompt using Claude and return the improved prompt text."""
    prompt_text = str(text)
    if not api_key or not str(api_key).strip():
        raise Exception("A Claude API key is required to improve prompts.")
    if str(api_key).strip().upper() in {"YOUR_KEY", "YOUR_API_KEY"}:
        raise Exception("Please provide a real Claude API key, not the placeholder.")

    client = ClaudeClient(api_key=str(api_key).strip())
    request_text = IMPROVEMENT_TEMPLATE.format(text=prompt_text)
    try:
        return client.ask(request_text)
    except Exception as exc:
        raise Exception(f"Could not improve prompt: {exc}") from exc
