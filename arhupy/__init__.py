"""arhupy: A prompt engineering toolkit for LLMs."""

from .api import run_api_server
from .chain import PromptChain, build_chain
from .claude import ClaudeClient
from .diff import compare_prompts
from .exporter import export_chain, export_prompt, import_chain, import_prompt
from .history import (
    add_history,
    compare_history,
    export_history,
    get_history as get_prompt_history,
    get_prompt_by_index,
    import_history,
)
from .improver import improve_prompt
from .interactive import run_interactive
from .library import delete, export_all, import_all, list_all, load, save
from .plugins import ArhupyPlugin, get_plugin, load_plugins
from .prompt import Prompt
from .scorer import score_prompt
from .share import get_shared, save_shared
from .templates import fill_template, get_template, list_templates
from .tokens import estimate_tokens
from .versioning import get_history as get_version_history, print_history, save_version

__version__ = "2.3.0"


def get_history(*args, **kwargs):
    """Return prompt history, or version history when called with a prompt name."""
    if (args and isinstance(args[0], str)) or "name" in kwargs:
        return get_version_history(*args, **kwargs)
    return get_prompt_history(*args, **kwargs)


__all__ = [
    "Prompt",
    "PromptChain",
    "run_api_server",
    "ArhupyPlugin",
    "load_plugins",
    "get_plugin",
    "build_chain",
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
    "save_shared",
    "get_shared",
    "compare_prompts",
    "improve_prompt",
    "list_templates",
    "get_template",
    "fill_template",
    "add_history",
    "compare_history",
    "export_history",
    "import_history",
    "get_prompt_by_index",
    "get_version_history",
    "run_interactive",
]
