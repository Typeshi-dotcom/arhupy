"""Built-in prompt templates for common use cases."""

TEMPLATES = {
    "fitness": "You are a fitness coach. Create a {plan} for {goal}.",
    "coding": "You are a senior developer. Explain {concept} in simple terms.",
    "writing": "You are a writer. Write a {type} about {topic}.",
    "business": "You are a business expert. Analyze {idea} and suggest improvements.",
}


def list_templates():
    """Return the names of all available built-in templates."""
    return sorted(TEMPLATES)


def get_template(name):
    """Return a built-in template by name."""
    template_name = str(name).strip().lower()
    try:
        return TEMPLATES[template_name]
    except KeyError as exc:
        raise Exception(f"Template not found: {name}") from exc
