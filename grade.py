"""Answer extraction + statistics (no scipy)."""
import math
import re


def extract_letter(text, valid):
    """First plausible answer letter restricted to the valid set, else None."""
    if not text:
        return None
    up = text.upper()
    valid = set(valid)
    # 1: a standalone single letter ("A", "A)", "A.")
    for m in re.finditer(r"\b([A-E])\b", up):
        if m.group(1) in valid:
            return m.group(1)
    # 2: parenthesized "(A)"
    for m in re.finditer(r"\(([A-E])\)", up):
        if m.group(1) in valid:
            return m.group(1)
    # 3: "answer/option/choice ... X"
    m = re.search(r"(?:ANSWER|OPTION|CHOICE)\D{0,12}([A-E])", up)
    if m and m.group(1) in valid:
        return m.group(1)
    return None


def wilson(k, n, z=1.96):
    """Wilson score 95% CI for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((center - half) / denom, (center + half) / denom)


def mcnemar(a_correct, b_correct):
    """Exact two-sided McNemar test on paired booleans (a -> b).

    b01 = a wrong, b right (b fixed it). b10 = a right, b wrong (b broke it).
    """
    b01 = sum(1 for a, b in zip(a_correct, b_correct) if (not a) and b)
    b10 = sum(1 for a, b in zip(a_correct, b_correct) if a and (not b))
    n = b01 + b10
    if n == 0:
        return {"b01": 0, "b10": 0, "p": 1.0}
    k = min(b01, b10)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return {"b01": b01, "b10": b10, "p": min(p, 1.0)}
