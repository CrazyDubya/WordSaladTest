"""Hybrid arm: can a *weak* model build Pong better when primed with a *strong*
author's word salad?

This crosses the two findings. The cross-author QA result (results/cross_author.md)
showed a borrowed *frontier* salad helps a weak answerer where its own salad can't.
Here we ask the same on CODE: the 1B and 3B each build a single-file HTML Pong three
ways (shared seed -> only the preamble differs):
  cold   : just the task.
  own    : primed with a salad the builder generated itself.
  claude : primed with a fixed Claude (Opus 4.8)-authored Pong salad (CLAUDE_SALAD).

The Claude salad is hand-authored (committed below for reproducibility), in the same
free-association shape the models were asked for -- imagery/mood/history/mechanics,
NOT a build spec.

Usage:  CF_API_TOKEN=... CF_ACCOUNT_ID=... python hybrid.py
Output: results/games/pong_<builder>_<cond>.html + pong_hybrid_salads.json
"""
import json
import os

import cf

DESC = "Pong game. Player vs CPU, scoring, keyboard controls."
TOPIC = "Pong, the arcade video game"
SEED = 4242
BUILDERS = {
    "1b": "@cf/meta/llama-3.2-1b-instruct",
    "3b": "@cf/meta/llama-3.2-3b-instruct",
}

# Claude (Opus 4.8) free-association salad about Pong -- imagery, history, mechanics,
# mood. Authored by hand in the same shape the models got; fixed for reproducibility.
CLAUDE_SALAD = [
    "two paddles", "white rectangle", "square ball", "black void", "center dashed line",
    "electronic tennis", "blip", "beep", "the satisfying pock", "ricochet",
    "angle off the paddle edge", "English on the ball", "accelerating volley",
    "CRT phosphor", "scanlines", "Atari 1972", "Allan Alcorn", "coin slot",
    "dim arcade", "wood-grain cabinet", "knob controller", "two players hunched",
    "score in chunky digits", "first to eleven", "serve", "the miss",
    "ball sails past", "reset to center", "monochrome", "rhythm of the rally",
    "latency", "reflex", "anticipation", "mirror symmetry", "top and bottom walls",
    "bounce", "vector of reflection", "simple physics", "Magnavox Odyssey",
    "minimalism", "geometry as sport", "the hypnotic back-and-forth", "hand-eye",
    "the moment before the bounce", "glow", "afterimage", "pixel dust",
    "deflection", "no music, only the beat", "primitive perfection",
]


def salad(model):
    raw = cf.run(model, [{"role": "user", "content":
        f"Write a 50 to 100 word word salad about {TOPIC}. Free-associate: imagery, "
        f"mood, sensory detail, history, culture, mechanics -- whatever the topic "
        f"evokes. Output ONLY a comma-separated list of words and short phrases, no "
        f"sentences, no numbering."}],
        max_tokens=400, temperature=1.0, seed=11)
    return [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()][:100]


def _clean(code):
    import re
    m = re.search(r"```(?:html)?\s*(.*?)```", code, re.S)
    if m:
        code = m.group(1)
    return code.strip()


def generate(model, terms=None):
    task = (f"Create a complete, polished version of the following as a SINGLE "
            f"self-contained HTML file (HTML + CSS + JavaScript, canvas where "
            f"appropriate): {DESC} Output ONLY the HTML file content, nothing else.")
    content = ("Relevant terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return _clean(cf.run(model, [{"role": "user", "content": content}],
                         max_tokens=6000, temperature=0.6, seed=SEED))


def main():
    os.makedirs("results/games", exist_ok=True)
    salads = {"claude": CLAUDE_SALAD}
    for tag, model in BUILDERS.items():
        own = salad(model)
        salads[f"{tag}_own"] = own
        conds = {"cold": None, "own": own, "claude": CLAUDE_SALAD}
        for cond, terms in conds.items():
            html = generate(model, terms)
            path = f"results/games/pong_{tag}_{cond}.html"
            open(path, "w").write(html)
            complete = html.rstrip().endswith("</html>")
            has_canvas = "<canvas" in html.lower()
            print(f"[{tag}/{cond}] {html.count(chr(10))+1}L "
                  f"complete={complete} canvas={has_canvas}")
    json.dump(salads, open("results/games/pong_hybrid_salads.json", "w"), indent=2)
    print("saved results/games/pong_hybrid_salads.json")


if __name__ == "__main__":
    main()
