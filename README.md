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
  `@cf/meta/llama-3.1-8b-instruct-fp8`
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

Results (`results/raw.jsonl`, `summary.json`, `report.md`) are committed once the full run
completes.

## Results

Full run: 3 models × 2 benchmarks × 3 arms = **15,489 graded answers** (paired per item),
0.05% answer-parse failures, salads averaging 36 terms. Accuracy and exact paired McNemar p:

| model | benchmark | n | A (ctrl) | B (salad) | C (placebo) | B−A (p) | B−C (p) | C−A |
|-------|-----------|---|---------|-----------|-------------|---------|---------|-----|
| 1B | OpenBookQA    |  500 | .354 | **.444** | .350 | **+.090** (.0000) | **+.094** (.0000) | −.004 |
| 1B | CommonsenseQA | 1221 | .387 | **.417** | .375 | **+.030** (.0148) | **+.042** (.0006) | −.011 |
| 3B | OpenBookQA    |  500 | .748 | .768 | .708 | +.020 (.275) | **+.060** (.0016) | −.040 |
| 3B | CommonsenseQA | 1221 | .736 | .732 | .702 | −.004 (.780) | **+.030** (.0122) | −.034 |
| 8B | OpenBookQA    |  500 | .774 | .802 | .748 | +.028 (.109) | **+.054** (.0045) | −.026 |
| 8B | CommonsenseQA | 1221 | .752 | .750 | .712 | −.002 (.944) | **+.038** (.0021) | −.040 |

**Three findings:**

1. **Relevance beats a matched placebo in every cell** (B−C significant, p .0000–.0122). Since
   C is count- and position-matched to B, the gain is the *content* of the terms — not the extra
   tokens or shifted position. The confound is ruled out.

2. **Priming beats plain answering (B−A) only for the 1B model** (significant on both benchmarks).
   At 3B and 8B it is null (p .11–.94). Self-generated keyword priming helps *only the smallest
   model* — consistent with knowledge augmentation: small models lack the knowledge and the terms
   supply it; larger models already have it.

3. **Irrelevant priming hurts, and more so with scale** — the placebo sits below control in all six
   cells (C−A from −.004 at 1B to −.040 at 8B). That is why B−C stays significant even where B−A is
   null: at 3B/8B the salad is neutral (B ≈ A) but the random words drag accuracy down (C < A).

**Verdict.** The hypothesis — related-term priming "activates relevant pathways" and improves
answers — holds for *net* benefit **only on the smallest model**. The relevance signal itself is
real and robust at every scale (related terms always beat random ones), but a measurable gain over
simply answering exists only where the model is knowledge-limited. For capable models, priming is
neutral at best, and the *wrong* priming is a real drag.

Raw per-item records, the generated `report.md`, and `summary.json` are in [`results/`](results/).

## License

MIT — see [LICENSE](LICENSE).
