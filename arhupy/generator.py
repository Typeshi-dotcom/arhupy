"""AI-powered prompt generation helpers."""

from .claude import ClaudeClient

PLACEHOLDER_API_KEYS = {"YOUR_KEY", "YOUR_API_KEY"}

GENERATION_TEMPLATE = """Create a clear, structured, and effective LLM prompt from this user idea:

IDEA:
{user_input}

Return only the finished prompt. Include a clear role, task, output structure, and useful constraints."""


def generate_prompt(user_input, api_key=None):
    """Generate a complete prompt from a short user idea."""
    idea = "" if user_input is None else str(user_input).strip()
    if not idea:
        raise Exception("User input is required to generate prompts.")
    if not api_key or not str(api_key).strip():
        raise Exception("An API key is required to generate prompts.")

    api_key_text = str(api_key).strip()
    if _is_placeholder_key(api_key_text):
        return _demo_generation(idea)

    client = ClaudeClient(api_key=api_key_text)
    request_text = GENERATION_TEMPLATE.format(user_input=idea)
    try:
        return client.ask(request_text)
    except Exception as exc:
        raise Exception(f"Could not generate prompt: {exc}") from exc


def _is_placeholder_key(api_key):
    """Return True when the API key is a documented placeholder value."""
    return api_key.upper() in PLACEHOLDER_API_KEYS


def _demo_generation(idea):
    """Return a realistic local demo prompt without calling an external API."""
    return (
        f"You are a professional {idea}. Create a clear, structured response for the user.\n\n"
        "Task:\n"
        f"- Turn the user's goal related to {idea} into a practical, actionable plan.\n"
        "- Explain the key steps in simple language.\n"
        "- Include examples where helpful.\n\n"
        "Output format:\n"
        "- Start with a short summary.\n"
        "- Use bullet points for the main steps.\n"
        "- End with one next action the user can take today.\n\n"
        "Constraints:\n"
        "- Keep the answer beginner friendly.\n"
        "- Avoid vague advice.\n"
        "- Make the response specific and useful."
    )
