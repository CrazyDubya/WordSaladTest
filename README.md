# WordSaladTest

Does priming a model's context with a self-generated "word salad" of *related terms*
make it answer better — and is any gain actually about **relevance**, or just about
**having more tokens in front of the question**?

A small, controlled, reproducible A/B(/C) experiment on open multiple-choice benchmarks,
run against small instruction-tuned models via the [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/) REST API.

## The idea

The treatment is close to **Generated Knowledge Prompting** (Liu et al., ACL 2022,
[arXiv:2110.08387](https://arxiv.org/abs/2110.08387)) — but instead of coherent knowledge
*sentences*, the model emits a bag of ~50 associated *keywords*, which are then prepended
to a fresh context before the question is asked.

The catch GKP's own ablation warns about: a gain could come from the extra tokens / shifted
position rather than the *content*. So this design adds a **placebo arm** to separate the two.

## Arms (same item, paired)

| arm | what the model sees before the question |
|-----|------------------------------------------|
| **A — control** | nothing extra; answer directly |
| **B — treatment** | turn 1: model generates ~50 related terms; turn 2: those terms prepended, then the question |
| **C — placebo** | the *same number* of **unrelated** mundane words, same position, same `Related terms:` framing |

B and C are structurally identical and **count- and position-matched** — they differ *only*
in whether the words are related. So **B − C isolates relevance** from the extra-tokens /
position confound. Placebo words are sampled independently of the question (and any word in
the question stem is excluded, since topical name/number overlap is the strongest distractor —
Shi et al., ICML 2023, [arXiv:2302.00093](https://arxiv.org/abs/2302.00093)).

## Setup

- **Models:** `@cf/meta/llama-3.2-1b-instruct`, `@cf/meta/llama-3.2-3b-instruct`,
  `@cf/meta/llama-3.1-8b-instruct-fp8`, `@cf/meta/llama-3.3-70b-instruct-fp8-fast`
- **Benchmarks:** OpenBookQA (`allenai/openbookqa`, test, 500) and CommonsenseQA
  (`tau/commonsense_qa`, validation, 1,221) — both auto-graded by exact answer-letter match.
- **Scoring:** accuracy with Wilson 95% CIs; paired **McNemar** exact test for A-vs-B and
  the decisive **C-vs-B**.

## Pre-registered predictions

- B > A by a small margin on these knowledge/commonsense tasks.
- The effect is **larger on smaller models** (less parametric knowledge to fall back on).
- The decisive test is **B vs C**: if B > C significantly → relevance matters. If B ≈ C and
  both ≥ A → it's a context/length artifact. C is expected to sit at or *below* A (mild distraction).

## Run it

```bash
pip install -r requirements.txt

export CF_API_TOKEN=...        # token with Workers AI (Account → Workers AI → Edit)
export CF_ACCOUNT_ID=...       # your Cloudflare account id

python run.py --limit 20 --models llama-3.2-3b   # quick pilot
python run.py                                    # full run (resumable)
python run.py --report-only                      # rebuild report from results/raw.jsonl
```

The run is **resumable**: every record is appended to `results/raw.jsonl` and completed
`(model, benchmark, arm, item)` cells are skipped on the next invocation — so an interruption
(including hitting the Workers AI free-tier daily allocation) just continues where it left off.
The whole run is well under ~$1 in Workers AI usage.

## Layout

| file | role |
|------|------|
| `cf.py` | Workers AI client — POST, backoff, scope check, throttle |
| `data.py` | load + normalize OpenBookQA / CommonsenseQA to one item shape |
| `arms.py` | salad / placebo / answer prompt builders + word bank |
| `grade.py` | answer-letter extraction, Wilson CI, exact McNemar |
| `run.py` | main loop, checkpoint/resume, report generation |

Cross-model experiment: `cross.py` (3B answers using the 70B's salads). Per-item records and
generated reports are in `results/`.

## Results

Main run: **4 models × 2 benchmarks × 3 arms = 20,652 graded answers** (paired per item),
0.05% parse failures. Accuracy and exact paired McNemar p:

| model | benchmark | n | A (ctrl) | B (salad) | C (placebo) | B−A (p) | B−C (p) | C−A |
|-------|-----------|---|---------|-----------|-------------|---------|---------|-----|
| 1B  | OpenBookQA    |  500 | .354 | **.444** | .350 | **+.090** (.0000) | **+.094** (.0000) | −.004 |
| 1B  | CommonsenseQA | 1221 | .387 | **.417** | .375 | **+.030** (.0148) | **+.042** (.0006) | −.011 |
| 3B  | OpenBookQA    |  500 | .748 | .768 | .708 | +.020 (.275) | **+.060** (.0016) | −.040 |
| 3B  | CommonsenseQA | 1221 | .736 | .732 | .702 | −.004 (.780) | **+.030** (.0122) | −.034 |
| 8B  | OpenBookQA    |  500 | .774 | .802 | .748 | +.028 (.109) | **+.054** (.0045) | −.026 |
| 8B  | CommonsenseQA | 1221 | .752 | .750 | .712 | −.002 (.944) | **+.038** (.0021) | −.040 |
| 70B | OpenBookQA    |  500 | .934 | .920 | .904 | −.014 (.281) | +.016 (.302) | −.030 |
| 70B | CommonsenseQA | 1221 | .839 | .826 | .824 | −.013 (.133) | +.002 (.871) | −.015 |

**Priming is a knowledge-gap crutch — it has a life cycle in model scale:**

| scale | accuracy | priming vs control (B−A) | relevance vs placebo (B−C) |
|-------|----------|--------------------------|----------------------------|
| 1B    | ~.37 | **helps** (+3 to +9, sig) | **significant** |
| 3B / 8B | ~.75 | neutral | **significant** (placebo drags) |
| 70B   | ~.84–.93 | slightly negative | **gone** (ns on both) |

1. **Relevance beats a matched placebo at every scale up to 8B** (B−C significant, p .0000–.0122) —
   but **vanishes at 70B** (p .30 / .87). Since C is count- and position-matched to B, where the gap
   exists it is the *content* of the terms, not the extra tokens. At the 70B ceiling there is no gap
   to exploit.

2. **Priming beats plain answering (B−A) only for the 1B model.** Null at 3B/8B, slightly negative at
   70B. Self-generated keyword priming helps *only* a knowledge-starved model; as parametric
   knowledge fills in, the benefit fades, then the preamble becomes pure noise.

3. **Irrelevant priming hurts up to 8B** (placebo below control, C−A −.004 → −.040), but even that
   distraction **disappears at 70B** — a capable model ignores the preamble entirely and answers
   from its own knowledge.

### Cross-model salad — does a *stronger* model's salad help a weaker answerer?

Generated Knowledge Prompting (Liu et al. 2022) found big-model *knowledge* helps small models more
than their own. We tested the keyword-salad version: the **3B** answers primed with the **70B's**
salad (arm **X**), vs its own arms. See [`cross.py`](cross.py) / [`results/cross_report.md`](results/cross_report.md).

| benchmark | A ctrl | B 3B-own | X 70B-salad | C placebo | X−B (p) | X−A (p) | X−C (p) |
|-----------|--------|----------|-------------|-----------|---------|---------|---------|
| OpenBookQA    | .748 | .768 | .774 | .708 | +.006 (.78) | +.026 (.16) | **+.066** (.0003) |
| CommonsenseQA | .736 | .732 | .741 | .702 | +.009 (.42) | +.005 (.73) | **+.039** (.0014) |

The 70B salads were genuinely different — longer (53 vs 35 terms), broader, **11% term overlap**
(Jaccard 0.11) with the 3B's own — yet they gave the 3B **no significant lift over its own salad**
(X−B ≈ +.01, p .4–.8). They still beat the random placebo (X−C significant), so relevance holds; but
**salad *quality* is not the lever.** The bottleneck is the answerer's capacity to use the
priming, not how good the terms are — the 3B already knows most of these answers, so richer terms
fill no gap.

**Overall verdict.** Related-term priming "activates relevant pathways" only in the narrow regime
where the model is *knowledge-limited*. The relevance signal is real where there's headroom (related
beats random up to 8B), but the *net* gain over simply answering exists only on the smallest model,
and a *better* salad from a stronger model does not change that. Priming a capable model is neutral
at best.

All per-item records are in [`results/`](results/): `raw.jsonl` (main run), `cross.jsonl`
(cross-salad), plus generated `report.md` / `summary.json` / `cross_report.md` / `cross_summary.json`.

## License

MIT — see [LICENSE](LICENSE).
