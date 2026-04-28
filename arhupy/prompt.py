"""Prompt templating utilities for arhupy."""


class Prompt:
    """A reusable prompt template with fill, preview, and reset helpers."""

    def __init__(self, template):
        """Create a prompt from a template string."""
        self.template = template
        self.values = {}
        self.filled_prompt = None

    def fill(self, **kwargs):
        """Replace template placeholders with keyword values and return text."""
        self.values = dict(kwargs)
        self.filled_prompt = self.template.format(**self.values)
        return self.filled_prompt

    def preview(self):
        """Print the current prompt in a clean, readable format."""
        prompt_text = str(self)
        border = "-" * 40
        print(border)
        print("Prompt Preview")
        print(border)
        print(prompt_text)
        print(border)

    def reset(self):
        """Clear filled values and restore the prompt to its template state."""
        self.values = {}
        self.filled_prompt = None

    def __str__(self):
        """Return the filled prompt when available, otherwise the template."""
        return self.filled_prompt if self.filled_prompt is not None else self.template
