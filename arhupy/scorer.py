"""Prompt scoring helpers for simple prompt quality feedback."""

import re


def score_prompt(text):
    """Score a prompt with simple length, clarity, and structure heuristics."""
    prompt_text = str(text)
    length_score = _score_length(prompt_text)
    clarity_score = _score_clarity(prompt_text)
    structure_score = _score_structure(prompt_text)
    overall_score = round((length_score + clarity_score + structure_score) / 3)

    return {
        "length_score": length_score,
        "clarity_score": clarity_score,
        "structure_score": structure_score,
        "overall_score": overall_score,
        "feedback": _build_feedback(
            prompt_text,
            length_score,
            clarity_score,
            structure_score,
        ),
    }


def _score_length(text):
    """Score prompt length, with 20 to 200 characters treated as ideal."""
    length = len(text.strip())
    if 20 <= length <= 200:
        return 10
    if length == 0:
        return 0
    if length < 20:
        return max(1, round((length / 20) * 10))
    if length <= 400:
        return max(5, 10 - round((length - 200) / 40))
    return 4


def _score_clarity(text):
    """Score prompt clarity by checking for clear instruction phrases."""
    lowered = text.lower()
    instruction_phrases = [
        "you are",
        "answer",
        "explain",
        "summarize",
        "write",
        "create",
        "list",
        "analyze",
        "respond",
        "provide",
    ]
    matches = sum(1 for phrase in instruction_phrases if phrase in lowered)
    if matches >= 3:
        return 10
    if matches == 2:
        return 8
    if matches == 1:
        return 7
    return 3


def _score_structure(text):
    """Score prompt structure by checking for reusable placeholders."""
    placeholders = re.findall(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", text)
    if len(placeholders) >= 3:
        return 10
    if len(placeholders) == 2:
        return 8
    if len(placeholders) == 1:
        return 6
    return 3


def _build_feedback(text, length_score, clarity_score, structure_score):
    """Build readable suggestions from the individual prompt scores."""
    feedback = []
    length = len(text.strip())

    if length_score < 8:
        if length < 20:
            feedback.append("Add more detail so the prompt is easier to follow.")
        else:
            feedback.append("Shorten the prompt so the main request is clearer.")
    if clarity_score < 8:
        feedback.append("Add a clear instruction such as answer, explain, or write.")
    if structure_score < 8:
        feedback.append("Use placeholders like {role}, {task}, or {question}.")
    if not feedback:
        feedback.append("Prompt looks clear and reusable.")

    return feedback
