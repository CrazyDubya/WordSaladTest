"""Code-generation arm: does feature-salad priming change the 70B's game code?

For a target game, the 70B writes a single self-contained HTML/Canvas file two ways:
  A (cold)   : just the task.
  B (primed) : same task, prepended with ~50 terms about building a polished version
               (mechanics, physics, UI/UX, game feel, scoring, AI, code structure).
A and B share a seed, so only the priming differs. Unlike the QA runs there is no
ground truth, but code is partially objective: both files are RUN (headless) to check
they load without errors, and a blind LLM panel judges quality/design/UX. See
results/games/<target>.md.

Usage:
  CF_API_TOKEN=... CF_ACCOUNT_ID=... python game.py [--target pong]
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
    "tetris": "Tetris game. Falling tetrominoes, rotation, line clears, scoring, levels.",
}


def salad(target_desc):
    raw = cf.run(MODEL, [{"role": "user", "content":
        f"List 50 single words or short phrases relevant to building a polished, "
        f"high-quality {target_desc} — mechanics, physics, collision, UI/UX, game "
        f"feel/juice, sound, scoring, AI, code structure. Output ONLY a comma-separated "
        f"list, no numbering."}], max_tokens=240, temperature=0.8, seed=11)
    return [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()][:50]


def _clean(code):
    m = re.search(r"```(?:html)?\s*(.*?)```", code, re.S)
    if m:
        code = m.group(1)
    return code.strip()


def generate(target_desc, terms=None):
    task = (f"Create a complete, polished {target_desc} as a SINGLE self-contained HTML "
            f"file (HTML + CSS + JavaScript using <canvas>). Output ONLY the HTML file "
            f"content, nothing else.")
    content = ("Relevant terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return _clean(cf.run(MODEL, [{"role": "user", "content": content}],
                         max_tokens=6000, temperature=0.6, seed=SEED))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="pong", choices=list(TARGETS))
    args = ap.parse_args()
    desc = TARGETS[args.target]
    terms = salad(desc)
    A = generate(desc)
    B = generate(desc, terms)
    os.makedirs("results/games", exist_ok=True)
    open(f"results/games/{args.target}_A.html", "w").write(A)
    open(f"results/games/{args.target}_B.html", "w").write(B)
    json.dump({"terms": terms}, open(f"results/games/{args.target}_salad.json", "w"), indent=2)
    for name, code in (("A cold", A), ("B primed", B)):
        print(f"{name}: {len(code)} chars, ~{code.count(chr(10))+1} lines, "
              f"complete={code.rstrip().endswith('</html>')}")
    print(f"saved results/games/{args.target}_*.html")


if __name__ == "__main__":
    main()
