"""Command line interface for arhupy."""

import argparse

from .diff import compare_prompts
from .scorer import score_prompt


def main(argv=None):
    """Run the arhupy command line interface."""
    parser = argparse.ArgumentParser(prog="arhupy")
    subparsers = parser.add_subparsers(dest="command")

    score_parser = subparsers.add_parser("score", help="Score a prompt")
    score_parser.add_argument("prompt", nargs="*", help="Prompt text to score")

    diff_parser = subparsers.add_parser("diff", help="Compare two prompts")
    diff_parser.add_argument("prompt1", help="First prompt text")
    diff_parser.add_argument("prompt2", help="Second prompt text")

    args = parser.parse_args(argv)
    if args.command == "score":
        result = score_prompt(" ".join(args.prompt))
        _print_score(result)
        return 0
    if args.command == "diff":
        result = compare_prompts(args.prompt1, args.prompt2)
        score_1 = score_prompt(args.prompt1)["overall_score"]
        score_2 = score_prompt(args.prompt2)["overall_score"]
        _print_diff(result, score_1, score_2)
        return 0

    parser.print_help()
    return 0


def _print_score(result):
    """Print prompt scoring results in a clean readable format."""
    print(f"Score: {result['overall_score']}/10")
    print(f"Length: {result['length_score']}/10")
    print(f"Clarity: {result['clarity_score']}/10")
    print(f"Structure: {result['structure_score']}/10")
    print("Suggestions:")
    for suggestion in result["feedback"]:
        print(f"  - {suggestion}")


def _print_diff(result, score_1, score_2):
    """Print prompt comparison results in a clean readable format."""
    print(f"Length difference: {result['length_diff']}")
    print(f"Word difference: {result['word_diff']}")
    print(f"Common words: {_format_words(result['common_words'])}")
    print(f"Unique to prompt 1: {_format_words(result['unique_to_p1'])}")
    print(f"Unique to prompt 2: {_format_words(result['unique_to_p2'])}")
    print(f"Prompt 1 score: {score_1}/10")
    print(f"Prompt 2 score: {score_2}/10")
    if score_1 > score_2:
        print("Better prompt: Prompt 1")
    elif score_2 > score_1:
        print("Better prompt: Prompt 2")
    else:
        print("Better prompt: Tie")


def _format_words(words):
    """Format a list of words for CLI output."""
    return ", ".join(words) if words else "None"


if __name__ == "__main__":
    main()
