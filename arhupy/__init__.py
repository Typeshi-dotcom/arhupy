"""arhupy: A prompt engineering toolkit for LLMs."""

from .chain import PromptChain
from .claude import ClaudeClient
from .diff import compare_prompts
from .exporter import export_chain, export_prompt, import_chain, import_prompt
from .history import add_history, get_history as get_prompt_history, get_prompt_by_index
from .improver import improve_prompt
from .library import delete, export_all, import_all, list_all, load, save
from .prompt import Prompt
from .scorer import score_prompt
from .templates import get_template, list_templates
from .tokens import estimate_tokens
from .versioning import get_history as get_version_history, print_history, save_version

__version__ = "1.3.0"


def get_history(*args, **kwargs):
    """Return prompt history, or version history when called with a prompt name."""
    if (args and isinstance(args[0], str)) or "name" in kwargs:
        return get_version_history(*args, **kwargs)
    return get_prompt_history(*args, **kwargs)


__all__ = [
    "Prompt",
    "PromptChain",
    "ClaudeClient",
    "save",
    "load",
    "list_all",
    "delete",
    "export_all",
    "import_all",
    "estimate_tokens",
    "save_version",
    "get_history",
    "print_history",
    "export_prompt",
    "import_prompt",
    "export_chain",
    "import_chain",
    "score_prompt",
    "compare_prompts",
    "improve_prompt",
    "list_templates",
    "get_template",
    "add_history",
    "get_prompt_by_index",
    "get_version_history",
]
