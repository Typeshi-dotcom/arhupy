"""Interactive command-line session for arhupy."""

from .chain import build_chain
from .diff import compare_prompts
from .generator import generate_prompt
from .history import compare_history, export_history, import_history
from .improver import improve_prompt
from .library import save
from .prompt import Prompt
from .scorer import score_prompt
from .share import save_shared
from .templates import fill_template


def run_interactive():
    """Run an interactive prompt engineering session."""
    print("Welcome to arhupy interactive mode.")
    prompt_text = input("Enter prompt: ").strip()

    while True:
        _print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            _handle_score(prompt_text)
        elif choice == "2":
            _handle_improve(prompt_text)
        elif choice == "3":
            _handle_compare(prompt_text)
        elif choice == "4":
            _handle_save(prompt_text)
        elif choice == "5":
            print("Goodbye.")
            break
        elif choice == "6":
            _handle_fill_template()
        elif choice == "7":
            _handle_build_chain()
        elif choice == "8":
            _handle_compare_history()
        elif choice == "9":
            _handle_export_history()
        elif choice == "10":
            _handle_import_history()
        elif choice == "11":
            _handle_share(prompt_text)
        elif choice == "12":
            _handle_generate()
        else:
            print("Invalid option. Please choose a number from 1 to 12.")


def _print_menu():
    """Print the interactive menu."""
    print()
    print("1. Score prompt")
    print("2. Improve prompt")
    print("3. Compare with another prompt")
    print("4. Save prompt")
    print("5. Exit")
    print("6. Fill template")
    print("7. Build prompt chain")
    print("8. Compare history prompts")
    print("9. Export history")
    print("10. Import history")
    print("11. Share prompt")
    print("12. Generate prompt from idea")


def _handle_score(prompt_text):
    """Score the current prompt and print the result."""
    result = score_prompt(prompt_text)
    print(f"Score: {result['overall_score']}/10")
    print("Strengths:")
    for strength in result["strengths"]:
        print(f"- {strength}")
    print("Improvements:")
    for suggestion in result["feedback"]:
        print(f"- {suggestion}")


def _handle_improve(prompt_text):
    """Improve the current prompt using Claude."""
    api_key = input("Enter Claude API key: ").strip()
    try:
        improved = improve_prompt(prompt_text, api_key)
    except Exception as exc:
        print(f"Error: {exc}")
        return

    print("Improved prompt:")
    print(improved)


def _handle_compare(prompt_text):
    """Compare the current prompt with another prompt."""
    second_prompt = input("Enter second prompt: ").strip()
    result = compare_prompts(prompt_text, second_prompt)
    print(f"Length difference: {result['length_diff']}")
    print(f"Word difference: {result['word_diff']}")
    print(f"Common words: {_format_words(result['common_words'])}")
    print(f"Unique to prompt 1: {_format_words(result['unique_to_p1'])}")
    print(f"Unique to prompt 2: {_format_words(result['unique_to_p2'])}")


def _handle_save(prompt_text):
    """Save the current prompt to the local prompt library."""
    name = input("Enter prompt name: ").strip()
    if not name:
        print("Prompt name is required.")
        return

    save(name, Prompt(prompt_text))
    print(f"Saved prompt: {name}")


def _handle_fill_template():
    """Fill a built-in prompt template interactively."""
    template_name = input("Enter template name: ").strip()
    try:
        filled = fill_template(template_name)
    except Exception as exc:
        print(f"Error: {exc}")
        return

    print("Filled prompt:")
    print(filled)


def _handle_build_chain():
    """Build and print a prompt chain from user-entered prompts."""
    prompts = []
    index = 1
    while True:
        prompt = input(f"Enter prompt {index}: ")
        if not prompt:
            break
        prompts.append(prompt)
        index += 1

    if not prompts:
        print("No prompts entered.")
        return

    print("Final prompt chain:")
    print(build_chain(prompts))


def _handle_compare_history():
    """Compare two prompts from prompt history."""
    index_1 = input("Enter first history index: ").strip()
    index_2 = input("Enter second history index: ").strip()
    try:
        result = compare_history(index_1, index_2)
    except Exception as exc:
        print(f"Error: {exc}")
        return

    _print_history_comparison(result)


def _print_history_comparison(result):
    """Print comparison output for history prompts."""
    prompt_1 = result["prompt_1"]
    prompt_2 = result["prompt_2"]
    comparison = result["comparison"]
    score_1 = score_prompt(prompt_1)["overall_score"]
    score_2 = score_prompt(prompt_2)["overall_score"]

    print("Prompt 1:")
    print(prompt_1)
    print("Prompt 2:")
    print(prompt_2)
    print(f"Length difference: {comparison['length_diff']}")
    print(f"Word difference: {comparison['word_diff']}")
    print("Score comparison:")
    print(f"Prompt 1 score: {score_1}/10")
    print(f"Prompt 2 score: {score_2}/10")
    if score_1 > score_2:
        print("Better prompt: Prompt 1")
    elif score_2 > score_1:
        print("Better prompt: Prompt 2")
    else:
        print("Better prompt: Tie")


def _handle_export_history():
    """Export prompt history to a JSON file."""
    filepath = input("Enter export file path: ").strip()
    try:
        export_history(filepath)
    except Exception as exc:
        print(f"Error: {exc}")
        return
    print(f"Exported history to {filepath}")


def _handle_import_history():
    """Import prompt history from a JSON file."""
    filepath = input("Enter import file path: ").strip()
    try:
        result = import_history(filepath)
    except Exception as exc:
        print(f"Error: {exc}")
        return
    print(f"Imported history entries: {len(result['imported'])}")
    print(f"Skipped duplicates: {result['skipped']}")


def _handle_share(prompt_text):
    """Create and print a local share link for the current prompt."""
    if not prompt_text:
        print("Prompt text is required.")
        return

    share_id = save_shared(prompt_text)
    print(f"Share link: http://localhost:8000/share/{share_id}")


def _handle_generate():
    """Generate and print a prompt from a user idea."""
    idea = input("Enter prompt idea: ").strip()
    api_key = input("Enter API key: ").strip()
    try:
        generated = generate_prompt(idea, api_key)
    except Exception as exc:
        print(f"Error: {exc}")
        return

    print("Generated prompt:")
    print(generated)


def _format_words(words):
    """Format a list of words for interactive output."""
    return ", ".join(words) if words else "None"
