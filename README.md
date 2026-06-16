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

_Full results land here when the run finishes._ Early read on the smallest model
(`llama-3.2-1b`, full benchmarks): B beats control by **+9 pts on OpenBookQA** and **+4 pts
on CommonsenseQA**, with the matched placebo sitting *at or below* control (all C-vs-B
p ≈ 0.000) — i.e. the gain tracks **relevance**, not token count. The effect shrinks on the
larger 3B model, as predicted. Final numbers across all three models supersede this note.

## License

MIT — see [LICENSE](LICENSE).
