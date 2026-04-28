"""Token estimation helpers."""

import math


def estimate_tokens(text):
    """Estimate token count as len(text) / 4, rounded up."""
    count = int(math.ceil(len(text) / 4))
    print(f"Estimated tokens: {count}")
    return count
