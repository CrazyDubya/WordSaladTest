"""Prompt builders for the three arms.

A (control)   : answer_messages(item)            -> no preamble
B (treatment) : salad_messages(stem) -> parse_terms -> answer_messages(item, terms)
C (placebo)   : placebo_terms(stem, n) -> answer_messages(item, placebo)

B and C are structurally identical ("Related terms: ...") and differ ONLY in
whether the words are actually related — that is what isolates relevance from
the extra-tokens / position confound. Placebo count is matched to B per item.
"""
import random
import re

# Mundane, mostly non-scientific everyday words. Sampled (not question-targeted)
# to serve as a count- and position-matched placebo. Any word appearing in the
# question stem is removed before sampling (avoids accidental topical overlap).
WORD_BANK = [
    "table", "chair", "sofa", "lamp", "curtain", "pillow", "blanket", "carpet",
    "drawer", "shelf", "mirror", "clock", "basket", "bucket", "broom", "towel",
    "spoon", "fork", "plate", "mug", "kettle", "napkin", "jar", "bottle",
    "shirt", "trousers", "jacket", "sweater", "scarf", "glove", "hat", "shoe",
    "sock", "belt", "button", "zipper", "pocket", "collar", "sleeve", "ribbon",
    "bread", "butter", "cheese", "soup", "noodle", "sandwich", "cookie", "jam",
    "pepper", "onion", "carrot", "lettuce", "pickle", "raisin", "waffle", "syrup",
    "bus", "tram", "ferry", "wagon", "bicycle", "scooter", "trailer", "canoe",
    "ticket", "luggage", "parcel", "envelope", "stamp", "postcard", "ledger", "folder",
    "garden", "fence", "gate", "hedge", "lawn", "patio", "porch", "alley",
    "village", "harbor", "market", "bakery", "library", "cinema", "stadium", "cottage",
    "morning", "evening", "weekend", "holiday", "birthday", "season", "calendar", "minute",
    "laughter", "whisper", "giggle", "yawn", "sneeze", "wink", "shrug", "nod",
    "happy", "tired", "curious", "calm", "eager", "shy", "proud", "gentle",
    "painter", "baker", "tailor", "plumber", "barber", "farmer", "sailor", "juggler",
    "puppet", "balloon", "marble", "kite", "crayon", "sticker", "domino", "yoyo",
    "umbrella", "raincoat", "sandal", "slipper", "mitten", "apron", "bonnet", "cloak",
    "guitar", "drum", "flute", "trumpet", "harp", "banjo", "whistle", "tambourine",
    "pebble", "feather", "acorn", "thread", "candle", "ribbon", "lantern", "compass",
    "diary", "novel", "comic", "poster", "magazine", "notebook", "bookmark", "pencil",
    "muffin", "pretzel", "popcorn", "lollipop", "biscuit", "custard", "pudding", "toffee",
    "hammock", "ladder", "anchor", "barrel", "crate", "trolley", "wheelbarrow", "shovel",
    "kitten", "puppy", "hamster", "parrot", "goldfish", "turtle", "rabbit", "ladybug",
    "sweater", "quilt", "cushion", "doormat", "wallpaper", "doorbell", "mailbox", "keychain",
]


def parse_terms(text):
    """Split a comma/newline list into clean terms, dropping bullets/numbering."""
    out = []
    for chunk in re.split(r"[,\n]", text or ""):
        t = re.sub(r"^[\s\-\*•\d\.\)]+", "", chunk).strip().strip(" .;:")
        if t and len(t) <= 40:
            out.append(t)
    return out


def salad_messages(stem):
    return [{
        "role": "user",
        "content": (
            "List 50 single words or short phrases closely related to the topic "
            "of this question. Output ONLY a comma-separated list of terms — no "
            "sentences, no numbering, no explanation.\n\n"
            f"Question: {stem}"
        ),
    }]


def placebo_terms(stem, n, seed):
    """n mundane words sampled deterministically, excluding stem tokens."""
    stop = set(re.findall(r"[a-z]+", stem.lower()))
    pool = [w for w in WORD_BANK if w.lower() not in stop]
    rng = random.Random(seed)
    if n <= 0:
        return []
    if n <= len(pool):
        return rng.sample(pool, n)
    return [rng.choice(pool) for _ in range(n)]


def _format_choices(choices):
    return "\n".join(f"{lab}) {txt}" for lab, txt in choices)


def answer_messages(item, preamble=None):
    letters = "/".join(lab for lab, _ in item["choices"])
    system = {
        "role": "system",
        "content": (
            f"You are answering a multiple-choice question. Respond with ONLY the "
            f"single letter ({letters}) of the correct answer. No explanation."
        ),
    }
    parts = []
    if preamble:
        parts.append("Related terms: " + ", ".join(preamble) + "\n\n")
    parts.append(f"Question: {item['stem']}\n{_format_choices(item['choices'])}\nAnswer:")
    return [system, {"role": "user", "content": "".join(parts)}]
