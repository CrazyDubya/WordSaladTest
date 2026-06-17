"""Floor experiments — characterize the 1B builder, the hybrid arm's failure floor.

In hybrid.py the 1B failed Pong in every condition, and the rich 50-term Claude salad
made it *worse* (a degenerate repetition loop). These three probes, all 1B Pong, pick
that floor apart. Shared seed isolates the one varying factor in each probe.

  ablate : the 50-term Claude salad split by category -- mechanics / imagery / history
           (~17 each, roughly length-matched, so CONTENT is the variable).
  dose   : length prefixes of the salad (5/15/30/50), same seed -> LENGTH is the variable.
  rep    : cold / own / claude across several build seeds -> is the floor reliable?

Reuses the full-salad seed-4242 build from hybrid.py (results/games/pong_1b_claude.html)
as the ablate/dose N=50 and the rep seed-4242 'claude' cell, so it is not regenerated.

Usage:  CF_API_TOKEN=... CF_ACCOUNT_ID=... python floor.py
Output: results/games/floor/<name>.html + floor_index.json
"""
import json
import os

import cf
from hybrid import CLAUDE_SALAD, salad, DESC, BUILDERS

M1B = BUILDERS["1b"]
SEED = 4242

# --- the 50-term Claude salad partitioned by category (sums to all 50) ---
MECH = [  # structural / gameplay -- the terms that could scaffold code
    "two paddles", "square ball", "center dashed line", "ricochet",
    "angle off the paddle edge", "English on the ball", "accelerating volley",
    "first to eleven", "serve", "the miss", "ball sails past", "reset to center",
    "top and bottom walls", "bounce", "vector of reflection", "simple physics",
    "deflection", "mirror symmetry",
]
IMG = [  # visual / sensory / mood
    "white rectangle", "black void", "blip", "beep", "the satisfying pock",
    "CRT phosphor", "scanlines", "monochrome", "glow", "afterimage", "pixel dust",
    "dim arcade", "the hypnotic back-and-forth", "the moment before the bounce",
    "rhythm of the rally", "no music, only the beat", "score in chunky digits",
]
HIST = [  # culture / history / experiential
    "electronic tennis", "Atari 1972", "Allan Alcorn", "coin slot",
    "wood-grain cabinet", "knob controller", "two players hunched", "Magnavox Odyssey",
    "minimalism", "geometry as sport", "hand-eye", "latency", "reflex",
    "anticipation", "primitive perfection",
]
assert sorted(MECH + IMG + HIST) == sorted(CLAUDE_SALAD), "partition must cover the salad"

REP_SEEDS = [7, 13, 21, 99]  # plus 4242 reused from hybrid.py = 5 seeds total


def _clean(code):
    import re
    m = re.search(r"```(?:html)?\s*(.*?)```", code, re.S)
    if m:
        code = m.group(1)
    return code.strip()


def generate(terms, seed):
    task = (f"Create a complete, polished version of the following as a SINGLE "
            f"self-contained HTML file (HTML + CSS + JavaScript, canvas where "
            f"appropriate): {DESC} Output ONLY the HTML file content, nothing else.")
    content = ("Relevant terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return _clean(cf.run(M1B, [{"role": "user", "content": content}],
                         max_tokens=6000, temperature=0.6, seed=seed))


def emit(name, terms, seed, index):
    html = generate(terms, seed)
    path = f"results/games/floor/{name}.html"
    open(path, "w").write(html)
    # cheap degeneration signal: the most-repeated nonblank line's share of all lines
    lines = [l.strip() for l in html.splitlines() if l.strip()]
    from collections import Counter
    top = Counter(lines).most_common(1)
    dup = top[0][1] if top else 0
    index[name] = {"terms": len(terms) if terms else 0, "seed": seed, "lines": len(lines),
                   "complete": html.rstrip().endswith("</html>"),
                   "top_dup_line": dup}
    print(f"{name:22} terms={(len(terms) if terms else 0):3} seed={seed:>4} "
          f"lines={len(lines):4} dup={dup:3} complete={index[name]['complete']}")


def main():
    os.makedirs("results/games/floor", exist_ok=True)
    idx = {}
    # 1 -- ablation (content varied, length ~matched)
    emit("ablate_mech", MECH, SEED, idx)
    emit("ablate_img", IMG, SEED, idx)
    emit("ablate_hist", HIST, SEED, idx)
    # 4 -- dose (length varied; N=50 reused from hybrid pong_1b_claude.html)
    for n in (5, 15, 30):
        emit(f"dose_{n:02d}", CLAUDE_SALAD[:n], SEED, idx)
    # 2 -- replication (own salad fixed by salad()'s seed=11; build seed varies)
    own = salad(M1B)
    idx["_own_salad_terms"] = own
    for s in REP_SEEDS:
        emit(f"rep_cold_{s}", None, s, idx)
        emit(f"rep_own_{s}", own, s, idx)
        emit(f"rep_claude_{s}", CLAUDE_SALAD, s, idx)
    json.dump(idx, open("results/games/floor/floor_index.json", "w"), indent=2)
    print("saved results/games/floor/floor_index.json")


if __name__ == "__main__":
    main()
