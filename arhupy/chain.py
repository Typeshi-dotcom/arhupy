"""Prompt chain utilities for combining multiple prompts."""


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
