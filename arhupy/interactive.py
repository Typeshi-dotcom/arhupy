"""Interactive command-line session for arhupy."""

from .diff import compare_prompts
from .improver import improve_prompt
from .library import save
from .prompt import Prompt
from .scorer import score_prompt


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
        else:
            print("Invalid option. Please choose 1, 2, 3, 4, or 5.")


def _print_menu():
    """Print the interactive menu."""
    print()
    print("1. Score prompt")
    print("2. Improve prompt")
    print("3. Compare with another prompt")
    print("4. Save prompt")
    print("5. Exit")


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


def _format_words(words):
    """Format a list of words for interactive output."""
    return ", ".join(words) if words else "None"
