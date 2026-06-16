"""Word-salad priming experiment: run arms A/B/C and report.

Usage:
  CF_API_TOKEN=... python run.py --limit 20 --models llama-3.2-3b   # pilot
  CF_API_TOKEN=... python run.py                                     # full run (resumes)
  python run.py --report-only                                        # rebuild report from raw.jsonl

Always resumable: every record is appended to results/raw.jsonl and completed
(model, bench, arm, item) keys are skipped on the next run.
"""
import argparse
import json
import os
import zlib

import arms
import cf
import data
import grade

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RAW = os.path.join(RESULTS, "raw.jsonl")

MODELS = {
    "llama-3.2-1b": "@cf/meta/llama-3.2-1b-instruct",
    "llama-3.2-3b": "@cf/meta/llama-3.2-3b-instruct",
    "llama-3.1-8b": "@cf/meta/llama-3.1-8b-instruct-fp8",
}
BENCHMARKS = ["openbookqa", "commonsenseqa"]
ARMS = ["A", "B", "C"]


def _seed(*parts):
    return zlib.crc32("|".join(parts).encode()) % 2_000_000_000 + 1


def _load_done():
    """Return (done_keys, salads) from any existing raw.jsonl."""
    done, salads = set(), {}
    if not os.path.exists(RAW):
        return done, salads
    with open(RAW) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            done.add((rec["model"], rec["bench"], rec["arm"], rec["id"]))
            if rec["arm"] == "S":
                salads[(rec["model"], rec["id"])] = rec["terms"]
    return done, salads


def _append(rec):
    with open(RAW, "a") as f:
        f.write(json.dumps(rec) + "\n")


def _answer(model, item, preamble):
    raw = cf.run(model, arms.answer_messages(item, preamble), max_tokens=8,
                 temperature=0.0, seed=42)
    valid = [lab for lab, _ in item["choices"]]
    letter = grade.extract_letter(raw, valid)
    return raw, letter


def run_experiment(model_keys, benchmarks, limit):
    os.makedirs(RESULTS, exist_ok=True)
    done, salads = _load_done()
    for mkey in model_keys:
        model = MODELS[mkey]
        for bench in benchmarks:
            items = data.load(bench, limit)
            for i, item in enumerate(items, 1):
                iid = item["id"]
                # Arm S: generate (or reuse) the related-terms salad once per item.
                terms = salads.get((model, iid))
                if terms is None:
                    raw = cf.run(model, arms.salad_messages(item["stem"]),
                                 max_tokens=220, temperature=0.7,
                                 seed=_seed(model, iid, "salad"))
                    terms = arms.parse_terms(raw)
                    salads[(model, iid)] = terms
                    _append({"model": model, "bench": bench, "arm": "S",
                             "id": iid, "terms": terms, "n_terms": len(terms),
                             "raw": raw})
                placebo = arms.placebo_terms(item["stem"], len(terms),
                                             seed=_seed(model, iid, "placebo"))
                preambles = {"A": None, "B": terms, "C": placebo}
                for arm in ARMS:
                    if (model, bench, arm, iid) in done:
                        continue
                    raw, letter = _answer(model, item, preambles[arm])
                    rec = {"model": model, "bench": bench, "arm": arm, "id": iid,
                           "gold": item["gold"], "raw": raw, "letter": letter,
                           "correct": letter == item["gold"], "n_terms": len(terms)}
                    if arm == "B":
                        rec["terms"] = terms
                    if arm == "C":
                        rec["terms"] = placebo
                    _append(rec)
                    done.add((model, bench, arm, iid))
                if i % 50 == 0:
                    print(f"  {mkey} / {bench}: {i}/{len(items)}")
            print(f"done: {mkey} / {bench}")


def report():
    """Aggregate raw.jsonl into summary.json + report.md."""
    by = {}          # (model,bench,arm) -> {"correct":[], "id_correct":{id:bool}, "parse_fail":int}
    if not os.path.exists(RAW):
        raise SystemExit("no results/raw.jsonl yet")
    with open(RAW) as f:
        for line in f:
            rec = json.loads(line)
            if rec["arm"] == "S":
                continue
            key = (rec["model"], rec["bench"], rec["arm"])
            d = by.setdefault(key, {"id_correct": {}, "parse_fail": 0})
            d["id_correct"][rec["id"]] = bool(rec["correct"])
            if rec["letter"] is None:
                d["parse_fail"] += 1

    models = sorted({k[0] for k in by})
    benches = sorted({k[1] for k in by})
    summary, md = {}, []
    md.append("# Word-Salad Priming — Results\n")
    md.append("Arms: **A** direct · **B** related-term salad · **C** placebo "
              "(count/position-matched unrelated words).\n")

    for model in models:
        for bench in benches:
            arms_present = {a: by[(model, bench, a)] for a in ARMS
                            if (model, bench, a) in by}
            if not arms_present:
                continue
            md.append(f"\n## {model} — {bench}\n")
            md.append("| arm | n | acc | 95% CI | parse-fail |")
            md.append("|---|---|---|---|---|")
            accs = {}
            for a in ARMS:
                if a not in arms_present:
                    continue
                d = arms_present[a]
                vals = d["id_correct"]
                n = len(vals)
                k = sum(vals.values())
                lo, hi = grade.wilson(k, n)
                accs[a] = (k, n)
                summary[f"{model}|{bench}|{a}"] = {
                    "n": n, "correct": k, "acc": k / n if n else 0,
                    "ci": [lo, hi], "parse_fail": d["parse_fail"]}
                md.append(f"| {a} | {n} | {k / n:.3f} | [{lo:.3f}, {hi:.3f}] | "
                          f"{d['parse_fail']} |")

            # paired McNemar on the shared item set
            def paired(x, y):
                dx, dy = arms_present[x]["id_correct"], arms_present[y]["id_correct"]
                ids = sorted(set(dx) & set(dy))
                return (grade.mcnemar([dx[i] for i in ids], [dy[i] for i in ids]),
                        len(ids))

            md.append("")
            for x, y, note in [("A", "B", "does the salad help vs control"),
                               ("C", "B", "does relevance beat a matched placebo")]:
                if x in arms_present and y in arms_present:
                    m, npair = paired(x, y)
                    summary[f"{model}|{bench}|mcnemar_{x}{y}"] = m
                    md.append(f"- **{x}→{y}** ({note}): {y} fixed {m['b01']}, "
                              f"broke {m['b10']} (of {npair} paired); "
                              f"McNemar p = {m['p']:.4f}")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(RESULTS, "report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("wrote results/summary.json and results/report.md")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(MODELS),
                    help="comma list of short model keys")
    ap.add_argument("--benchmarks", default=",".join(BENCHMARKS))
    ap.add_argument("--limit", type=int, default=None,
                    help="cap items per benchmark")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    if args.report_only:
        report()
        return

    model_keys = [m.strip() for m in args.models.split(",") if m.strip()]
    benches = [b.strip() for b in args.benchmarks.split(",") if b.strip()]
    bad = [m for m in model_keys if m not in MODELS]
    if bad:
        raise SystemExit(f"unknown models {bad}; choose from {list(MODELS)}")
    run_experiment(model_keys, benches, args.limit)
    report()


if __name__ == "__main__":
    main()
