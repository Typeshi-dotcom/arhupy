"""Command line interface for arhupy."""

import argparse

from .scorer import score_prompt


def main(argv=None):
    """Run the arhupy command line interface."""
    parser = argparse.ArgumentParser(prog="arhupy")
    subparsers = parser.add_subparsers(dest="command")

    score_parser = subparsers.add_parser("score", help="Score a prompt")
    score_parser.add_argument("prompt", nargs="*", help="Prompt text to score")

    args = parser.parse_args(argv)
    if args.command == "score":
        result = score_prompt(" ".join(args.prompt))
        _print_score(result)
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


if __name__ == "__main__":
    main()
