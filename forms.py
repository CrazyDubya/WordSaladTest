"""Forms experiment — does the SAME salad help a poem but hurt a story?

The prose arm's claim is mechanistic: a genre salad hurts narrative because naming a
trope is *telling*. But imagist poetry *rewards* naming concrete images. So the theory
makes a falsifiable bet: hand the 1B the same noir salad and it should HELP the poem and
HURT the story. If both degrade (or both improve), the props/ingredients story is wrong.

The 1B writes four texts -- {poem, story} x {cold, salad} -- shared seed within a form so
only the priming differs. One fixed Claude (Opus 4.8)-authored noir salad for both forms.
Judging is a blind LLM panel (run separately); this script only generates.

Usage:  CF_API_TOKEN=... CF_ACCOUNT_ID=... python forms.py
Output: results/stories/forms_1b.json
"""
import json
import os

import cf

M1B = "@cf/meta/llama-3.2-1b-instruct"
SEED = 4242

# Claude (Opus 4.8) free-association noir salad -- imagery/mood, shared by both forms.
NOIR_SALAD = [
    "rain-slicked asphalt", "neon bleeding into puddles", "venetian-blind shadows",
    "a cigarette's red ember", "cheap whiskey", "the click of a .38",
    "femme fatale in the doorway", "a payphone ringing in an empty hall",
    "fog off the harbor", "a fedora's brim", "smoke under a desk lamp",
    "the city that never forgives", "double-cross", "a body in the trunk",
    "the long shadow of a streetlight", "jazz from a third-floor window",
    "blood on a white shirt", "an empty bottle", "everybody lied",
    "a gun in the glovebox", "the morning after", "hard rain, soft betrayal",
    "a detective who's seen too much", "ash on the floorboards", "the meter running",
    "a deal gone wrong", "sirens two blocks over", "the wrong side of midnight",
    "a kiss that costs you", "cold coffee", "a confession nobody believes",
    "the gutter and the gun",
]

TASKS = {
    "poem": "Write a short noir poem, about 12 to 16 lines. Just the poem.",
    "story": "Write a short noir story of about 250 words. Just the story.",
}


def write(task, terms=None, mt=600):
    content = ("Evocative terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return cf.run(M1B, [{"role": "user", "content": content}],
                  max_tokens=mt, temperature=0.9, seed=SEED).strip()


def main():
    out = {"salad": NOIR_SALAD}
    for form, task in TASKS.items():
        out[form] = {"cold": write(task), "salad": write(task, NOIR_SALAD)}
        print(f"{form}: cold ~{len(out[form]['cold'].split())}w | "
              f"salad ~{len(out[form]['salad'].split())}w")
    os.makedirs("results/stories", exist_ok=True)
    json.dump(out, open("results/stories/forms_1b.json", "w"), indent=2)
    print("saved results/stories/forms_1b.json")


if __name__ == "__main__":
    main()
