"""Cross-model salad: does a stronger model's word salad help a weaker answerer?

Generated Knowledge Prompting (Liu et al. 2022) found that knowledge produced by a
*large* model helps a *small* inference model far more than the small model's own
knowledge. This tests the keyword-salad version of that claim:

  the 3B model answers each question primed with the **70B**'s related-term salad
  (arm X), compared against its own arms from the main run:
      A  control (no preamble)
      B  3B's OWN salad
      X  70B's salad   <- new
      C  placebo (count-matched unrelated words)

Headline comparison is X vs B: is a stronger model's salad meaningfully better?

Reuses the 70B salads already in results/raw.jsonl (from `run.py --models llama-3.3-70b`);
generates one on the fly only if missing. Resumable via results/cross.jsonl.

Usage:
  CF_API_TOKEN=... CF_ACCOUNT_ID=... python cross.py [--limit N]
  python cross.py --report-only
"""
import argparse
import json
import os

import arms
import cf
import data
import grade
import run

ANSWERER = run.MODELS["llama-3.2-3b"]
SALAD_SRC = run.MODELS["llama-3.3-70b"]
BENCHMARKS = ["openbookqa", "commonsenseqa"]
CROSS = os.path.join(run.RESULTS, "cross.jsonl")


def _salads_from_raw(model):
    """{item_id: terms} for a given model's arm-S salads in raw.jsonl."""
    out = {}
    if not os.path.exists(run.RAW):
        return out
    with open(run.RAW) as f:
        for line in f:
            r = json.loads(line)
            if r["arm"] == "S" and r["model"] == model:
                out[r["id"]] = r["terms"]
    return out


def _cross_done():
    done = set()
    if os.path.exists(CROSS):
        with open(CROSS) as f:
            for line in f:
                r = json.loads(line)
                done.add((r["bench"], r["id"]))
    return done


def run_cross(limit=None):
    src_salads = _salads_from_raw(SALAD_SRC)
    done = _cross_done()
    missing = 0
    for bench in BENCHMARKS:
        items = data.load(bench, limit)
        for i, item in enumerate(items, 1):
            iid = item["id"]
            if (bench, iid) in done:
                continue
            terms = src_salads.get(iid)
            if terms is None:  # 70B salad not in raw yet -> make one
                missing += 1
                raw = cf.run(SALAD_SRC, arms.salad_messages(item["stem"]),
                             max_tokens=220, temperature=0.7,
                             seed=run._seed(SALAD_SRC, iid, "salad"))
                terms = arms.parse_terms(raw)
            raw, letter = run._answer(ANSWERER, item, terms)
            with open(CROSS, "a") as f:
                f.write(json.dumps({
                    "bench": bench, "id": iid, "arm": "X",
                    "answerer": ANSWERER, "salad_source": SALAD_SRC,
                    "gold": item["gold"], "raw": raw, "letter": letter,
                    "correct": letter == item["gold"], "terms": terms,
                    "n_terms": len(terms)}) + "\n")
            done.add((bench, iid))
            if i % 100 == 0:
                print(f"  {bench}: {i}/{len(items)}")
        print(f"done cross: {bench}")
    if missing:
        print(f"note: generated {missing} 70B salads on the fly (not in raw.jsonl)")


def _raw_3b_correct():
    """{(bench, arm): {id: bool}} for the 3B model's A/B/C in raw.jsonl."""
    out = {}
    with open(run.RAW) as f:
        for line in f:
            r = json.loads(line)
            if r["model"] == ANSWERER and r["arm"] in ("A", "B", "C"):
                out.setdefault((r["bench"], r["arm"]), {})[r["id"]] = bool(r["correct"])
    return out


def report():
    base = _raw_3b_correct()
    xcorr = {}  # (bench): {id: bool}
    with open(CROSS) as f:
        for line in f:
            r = json.loads(line)
            xcorr.setdefault(r["bench"], {})[r["id"]] = bool(r["correct"])

    md = ["# Cross-Model Salad — 3B answerer, 70B salad\n",
          "Arm **X** = 3B answers primed with the **70B**'s salad. Compared to the 3B's own "
          "arms (A control · B own salad · C placebo) from the main run.\n",
          "Headline: **X vs B** — does a stronger model's salad beat the 3B's own?\n"]
    summary = {}
    for bench in BENCHMARKS:
        cols = {"A": base.get((bench, "A"), {}), "B": base.get((bench, "B"), {}),
                "X": xcorr.get(bench, {}), "C": base.get((bench, "C"), {})}
        ids = set.intersection(*[set(d) for d in cols.values()]) if all(cols.values()) else set()
        n = len(ids)
        if n < 30:
            md.append(f"\n## {bench}: only {n} shared items — skip")
            continue
        acc = {k: sum(cols[k][i] for i in ids) / n for k in cols}
        md.append(f"\n## {bench}  (n={n})\n")
        md.append("| arm | source | acc | 95% CI |")
        md.append("|---|---|---|---|")
        labels = {"A": "control", "B": "3B own salad", "X": "70B salad", "C": "placebo"}
        for k in ("A", "B", "X", "C"):
            lo, hi = grade.wilson(sum(cols[k][i] for i in ids), n)
            md.append(f"| {k} | {labels[k]} | {acc[k]:.3f} | [{lo:.3f}, {hi:.3f}] |")
            summary[f"{bench}|{k}"] = {"acc": acc[k], "n": n, "ci": [lo, hi]}
        md.append("")
        for x, y, note in [("B", "X", "70B salad vs 3B's own salad"),
                           ("A", "X", "70B salad vs control"),
                           ("C", "X", "70B salad vs placebo")]:
            m = grade.mcnemar([cols[x][i] for i in ids], [cols[y][i] for i in ids])
            summary[f"{bench}|mcnemar_{x}{y}"] = m
            md.append(f"- **{x}→{y}** ({note}): X fixed {m['b01']}, broke {m['b10']}; "
                      f"Δacc {acc[y] - acc[x]:+.3f}; McNemar p = {m['p']:.4f}")

    with open(os.path.join(run.RESULTS, "cross_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(run.RESULTS, "cross_report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("wrote results/cross_report.md and results/cross_summary.json")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        report()
        return
    run_cross(args.limit)
    report()


if __name__ == "__main__":
    main()
