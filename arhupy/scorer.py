"""Prompt scoring helpers for simple prompt quality feedback."""

import re

ROLE_PHRASES = ["you are", "act as", "role"]
TASK_WORDS = ["write", "explain", "generate", "analyze", "give"]
OUTPUT_PHRASES = ["format", "in bullet points", "step by step"]
CONSTRAINT_WORDS = ["limit", "max", "within", "only"]


def score_prompt(text):
    """Score a prompt with realistic prompt-quality heuristics."""
    prompt_text = "" if text is None else str(text)
    analysis = _analyze_prompt(prompt_text)

    length_score = _score_length(prompt_text)
    clarity_score = _score_clarity(analysis)
    structure_score = _score_structure(analysis)
    overall_score = round((length_score + clarity_score + structure_score) / 3)

    return {
        "length_score": length_score,
        "clarity_score": clarity_score,
        "structure_score": structure_score,
        "overall_score": overall_score,
        "feedback": _build_feedback(prompt_text, analysis),
        "strengths": _build_strengths(prompt_text, analysis),
    }


def _score_length(text):
    """Score prompt length, with 20 to 200 characters treated as ideal."""
    length = len(text.strip())
    if 20 <= length <= 200:
        return 10
    if length == 0:
        return 0
    if length < 10:
        return 2
    if length < 20:
        return 6
    if length <= 300:
        return 8
    return 7


def _score_clarity(analysis):
    """Score prompt clarity from role, task, output, and constraint signals."""
    if not analysis["text"]:
        return 0

    score = 2
    if analysis["has_role"]:
        score += 2
    if analysis["has_task"]:
        score += 3
    if analysis["has_output_instruction"]:
        score += 2
    if analysis["has_constraints"]:
        score += 1
    return min(score, 10)


def _score_structure(analysis):
    """Score prompt structure by checking reusable and formatting signals."""
    if not analysis["text"]:
        return 0

    placeholder_count = len(analysis["placeholders"])
    score = 5
    if placeholder_count >= 3:
        score += 3
    elif placeholder_count == 2:
        score += 2
    elif placeholder_count == 1:
        score += 1
    if analysis["has_output_instruction"]:
        score += 1
    if analysis["has_constraints"]:
        score += 1
    return min(score, 10)


def _analyze_prompt(text):
    """Return reusable prompt analysis flags for scoring and feedback."""
    stripped = text.strip()
    lowered = stripped.lower()
    placeholders = re.findall(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", stripped)
    return {
        "text": stripped,
        "has_role": _contains_any(lowered, ROLE_PHRASES),
        "has_task": _contains_any(lowered, TASK_WORDS),
        "has_output_instruction": _contains_any(lowered, OUTPUT_PHRASES),
        "has_constraints": _contains_any(lowered, CONSTRAINT_WORDS),
        "placeholders": placeholders,
    }


def _contains_any(text, phrases):
    """Return True when any phrase appears in the text."""
    return any(phrase in text for phrase in phrases)


def _build_feedback(text, analysis):
    """Build readable improvement suggestions from prompt analysis."""
    feedback = []
    length = len(text.strip())

    if length == 0:
        feedback.append("Add prompt text before scoring.")
    elif length < 10:
        feedback.append("Add more detail so the prompt is easier to follow.")
    elif length < 20:
        feedback.append("Add a little more context to make the request clear.")
    elif length > 300:
        feedback.append("Shorten the prompt so the main request is easier to scan.")

    if not analysis["has_role"]:
        feedback.append("Add a role such as 'you are' or 'act as'.")
    if not analysis["has_task"]:
        feedback.append("Add a clear task such as write, explain, generate, analyze, or give.")
    if not analysis["placeholders"]:
        feedback.append("Use placeholders like {role}, {task}, or {question}.")
    if not analysis["has_output_instruction"]:
        feedback.append("Add an output format such as bullet points or step by step.")
    if not analysis["has_constraints"]:
        feedback.append("Add constraints such as limits, maximum length, or what to include only.")

    if not feedback:
        feedback.append("Prompt looks strong and ready to use.")

    return feedback


def _build_strengths(text, analysis):
    """Build a readable list of prompt strengths."""
    strengths = []
    length = len(text.strip())

    if 20 <= length <= 200:
        strengths.append("Good prompt length")
    if analysis["has_role"]:
        strengths.append("Role is defined")
    if analysis["has_task"]:
        strengths.append("Clear task defined")
    if analysis["placeholders"]:
        strengths.append("Good structure")
    if analysis["has_output_instruction"]:
        strengths.append("Output format is specified")
    if analysis["has_constraints"]:
        strengths.append("Useful constraints included")

    if not strengths:
        strengths.append("Ready for improvement")

    return strengths
