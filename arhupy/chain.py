"""Prompt chain utilities for combining multiple prompts."""

from .prompt import Prompt


class PromptChain:
    """A simple ordered collection of prompts."""

    def __init__(self, prompts):
        """Create a prompt chain from a list of Prompt objects."""
        self.prompts = list(prompts)

    def build(self):
        """Join all prompts into one string separated by newlines."""
        return "\n".join(str(prompt) for prompt in self.prompts)

    def add(self, prompt):
        """Add a Prompt object to the end of the chain."""
        self.prompts.append(prompt)

    def clear(self):
        """Remove all prompts from the chain."""
        self.prompts.clear()

    def to_dict(self):
        """Return this prompt chain as a dictionary for JSON export."""
        return {
            "prompts": [prompt.to_dict() for prompt in self.prompts],
        }

    @classmethod
    def from_dict(cls, data):
        """Create a PromptChain object from exported dictionary data."""
        if not isinstance(data, dict):
            raise ValueError("PromptChain data must be a dictionary.")

        prompt_data = data.get("prompts")
        if not isinstance(prompt_data, list):
            raise ValueError("PromptChain data must include a prompts list.")

        prompts = [Prompt.from_dict(item) for item in prompt_data]
        return cls(prompts)


def build_chain(prompts):
    """Build a combined prompt from a list of prompt strings."""
    return "\n".join(str(prompt) for prompt in prompts)
