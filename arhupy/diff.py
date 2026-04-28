"""Prompt comparison helpers."""


def compare_prompts(p1, p2):
    """Compare two prompt strings and return simple word and length differences."""
    prompt_1 = str(p1)
    prompt_2 = str(p2)
    words_1 = prompt_1.split()
    words_2 = prompt_2.split()
    word_set_1 = set(words_1)
    word_set_2 = set(words_2)

    return {
        "length_diff": len(prompt_1) - len(prompt_2),
        "word_diff": len(words_1) - len(words_2),
        "common_words": sorted(word_set_1 & word_set_2),
        "unique_to_p1": sorted(word_set_1 - word_set_2),
        "unique_to_p2": sorted(word_set_2 - word_set_1),
    }
