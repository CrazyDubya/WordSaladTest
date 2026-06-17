"""Code-generation arm: does feature-salad priming change the 70B's code?

For a target, the 70B writes a single self-contained HTML file two ways (shared seed,
so only the priming differs):
  A (cold)   : just the task.
  B (primed) : same task, prepended with ~50 terms about building a polished version.
Unlike the QA runs there is no ground truth, but code is partially objective: both files
are RUN (headless) to check they load without errors, and a blind LLM panel judges
quality / design / UX. See results/games/<target>.md.

Usage:
  CF_API_TOKEN=... CF_ACCOUNT_ID=... python game.py --target tetris   # or: --target all
Output: results/games/<target>_A.html, <target>_B.html, <target>_salad.json
"""
import argparse
import json
import os
import re

import cf

MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
SEED = 4242

TARGETS = {
    "pong": "Pong game. Player vs CPU, scoring, keyboard controls.",
    "tetris": "Tetris game with falling tetrominoes, rotation, line clears, scoring, "
              "levels, and a next-piece preview.",
    "markdown": "Markdown editor web app with a live preview pane, a formatting toolbar, "
                "and a word count.",
    "dashboard": "interactive data dashboard that visualizes a small built-in sample "
                 "dataset with at least two chart types, a filter control, and tooltips.",
    "sortviz": "sorting-algorithm visualizer with multiple algorithms (bubble, quick, "
               "merge), animated bars, a speed control, and a shuffle button.",
}

# Free-association topics for the salad (the *subject*, not a build spec).
TOPICS = {
    "pong": "Pong, the arcade video game",
    "tetris": "Tetris, the falling-block puzzle game",
    "markdown": "Markdown and writing in a plain-text editor",
    "dashboard": "data dashboards and charts",
    "sortviz": "sorting algorithms",
}


def salad(topic):
    raw = cf.run(MODEL, [{"role": "user", "content":
        f"Write a 50 to 100 word word salad about {topic}. Free-associate: imagery, "
        f"mood, sensory detail, history, culture, mechanics -- whatever the topic "
        f"evokes. Output ONLY a comma-separated list of words and short phrases, no "
        f"sentences, no numbering."}],
        max_tokens=400, temperature=1.0, seed=11)
    return [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()][:100]


def _clean(code):
    m = re.search(r"```(?:html)?\s*(.*?)```", code, re.S)
    if m:
        code = m.group(1)
    return code.strip()


def generate(desc, terms=None):
    task = (f"Create a complete, polished version of the following as a SINGLE "
            f"self-contained HTML file (HTML + CSS + JavaScript, canvas where "
            f"appropriate): {desc} Output ONLY the HTML file content, nothing else.")
    content = ("Relevant terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return _clean(cf.run(MODEL, [{"role": "user", "content": content}],
                         max_tokens=6000, temperature=0.6, seed=SEED))


def build(target):
    desc = TARGETS[target]
    terms = salad(TOPICS[target])
    A = generate(desc)
    B = generate(desc, terms)
    os.makedirs("results/games", exist_ok=True)
    open(f"results/games/{target}_A.html", "w").write(A)
    open(f"results/games/{target}_B.html", "w").write(B)
    json.dump({"terms": terms}, open(f"results/games/{target}_salad.json", "w"), indent=2)
    print(f"[{target}] salad={len(terms)} | "
          f"A {A.count(chr(10))+1}L complete={A.rstrip().endswith('</html>')} | "
          f"B {B.count(chr(10))+1}L complete={B.rstrip().endswith('</html>')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="pong")
    args = ap.parse_args()
    targets = [t for t in TARGETS if t != "pong"] if args.target == "all" else [args.target]
    for t in targets:
        build(t)
    print("done:", ", ".join(targets))


if __name__ == "__main__":
    main()
