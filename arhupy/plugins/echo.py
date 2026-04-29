"""Example echo plugin for arhupy."""

from .base import ArhupyPlugin


class EchoPlugin(ArhupyPlugin):
    """A simple plugin that echoes the provided text."""

    name = "echo"

    def run(self, text):
        """Return the provided text with an echo prefix."""
        return f"Echo: {text}"
