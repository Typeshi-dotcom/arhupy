"""Base plugin class for arhupy plugins."""


class ArhupyPlugin:
    """Base class for all arhupy plugins."""

    name = "base"

    def run(self, *args):
        """Run the plugin with the provided arguments."""
        raise NotImplementedError
