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
than their own. We tested the keyword-salad version: a weak model answers primed with the **70B's**
salad (arm **X**), vs its own arms. The 70B salads are genuinely different — longer (53 vs ~22–35
terms), broader, **~11% term overlap** (Jaccard 0.11) with the small model's own. Run with
[`cross.py --answerer <model>`](cross.py); reports in `results/cross_<tag>_report.md`.

**3B answerer** — the 70B salad gives **no lift over the 3B's own** (X−B ns on both):

| benchmark | A ctrl | B 3B-own | X 70B-salad | C placebo | X−B (p) | X−C (p) |
|-----------|--------|----------|-------------|-----------|---------|---------|
| OpenBookQA    | .748 | .768 | .774 | .708 | +.006 (.78) | **+.066** (.0003) |
| CommonsenseQA | .736 | .732 | .741 | .702 | +.009 (.42) | **+.039** (.0014) |

**1B answerer** — the result *splits by task*:

| benchmark | A ctrl | B 1B-own | X 70B-salad | C placebo | X−B (p) | X−A (p) |
|-----------|--------|----------|-------------|-----------|---------|---------|
| OpenBookQA    | .354 | .444 | .434 | .350 | −.010 (.58) | **+.080** (.0000) |
| CommonsenseQA | .387 | .417 | **.500** | .375 | **+.083** (.0000) | **+.113** (.0000) |

**Salad quality *is* a lever — but only in a specific regime.** For the 1B on CommonsenseQA, the
70B's salad lifts accuracy from .417 (its own salad) to **.500** — +8.3 pts from *changing only who
wrote the salad*, the genuine Generated-Knowledge-Prompting effect (a strong model's knowledge
helping a weak one). But it appears **only** when the answerer has a real knowledge gap (1B, not 3B)
**and** the task rewards broad associative context (commonsense) rather than one specific retrieved
fact (OpenBookQA, where even the 1B sees no benefit from the richer salad). The 3B null was a
masked case: the 3B already knew the commonsense answers, so a better salad filled no gap.

**Overall verdict.** Related-term priming is a **knowledge-gap crutch** with three gates: it helps
only where (1) the model is knowledge-limited (net benefit at 1B; neutral by 3B; inert at 70B), (2)
the terms are *relevant* (related beats a matched placebo up to 8B, gone at the 70B ceiling), and
(3) — for salad *quality* to matter — the task rewards breadth of association. Hit all three (1B ×
CommonsenseQA × 70B-authored salad) and you get a double-digit gain; miss any one and the effect
shrinks to neutral. Priming a capable model is neutral at best.

All per-item records are in [`results/`](results/): `raw.jsonl` (main run), `cross_3b.jsonl` /
`cross_1b.jsonl` (cross-salad), plus generated `report.md` / `summary.json` / `cross_<tag>_report.md`.

## Creative-writing coda (no ground truth — qualitative)

A subjective companion to the QA runs: does **genre-salad priming** improve the 70B's *short stories*?
For noir and cosmic horror, the 70B writes one story cold (A) and one primed with ~50 genre-evocative
terms (B), same seed. There is no objective metric, so judging is a **blind LLM panel** — 3 independent
judges per genre, shown the pair unlabeled, picking the better / more genre-authentic story.

**Result (original salad): 12/12 blind votes for the *unprimed* story**, both genres, both questions.
A **denser free-association re-run** (40–60 phrases, same seed so the cold stories are unchanged) was
later run with a fresh 3-judge × 3-axis panel: it **replicates the direction — cold wins overall 5–1**
— but cracks the shutout, with the better salad winning noir **craft** 3–0 on concrete imagery while
still losing the *story*. The mechanism is explicit in the text: the primed noir closes on the verbatim
salad phrases *"moral ambiguity"* and *"gritty realism"* — the salad becomes a list of tropes to **name**
rather than dramatize. Reproducible in [`story.py`](story.py); both runs, full stories, and panel
verdicts in [`results/stories/creative_writing.md`](results/stories/creative_writing.md).

## Code-generation coda — and a methodology correction

Does salad priming change the 70B's *code*? First pass: it writes a single-file HTML/Canvas **Pong**
cold (A) vs. primed (B), same seed; both run headless, then a blind panel scores them. Primed won
design + UX 3–0, cold won correctness 3–0 — the first arm where priming the 70B clearly helped, but
only on scope ([`results/games/pong.md`](results/games/pong.md)). **Four harder targets** (Tetris,
Markdown, Dashboard, Sortviz) seemed to sharpen a *"breadth up, depth collapses"* story: the primed
build was the broken one in 3 of 4.

**Then the confound surfaced.** Those code salads were generated by a prompt that *enumerated
engineering dimensions* ("cover UX, state management, edge cases, accessibility, performance, code
structure") — a covert **spec**, not a word salad. So that arm tested *checklist* priming, not
word-salad priming. Re-running with a genuine free-association salad (*"50–100 word salad about
{topic}"*, topic = the subject, not "build a polished version of X") **reverses the finding**:

| of the 4 advanced targets | checklist salad (old B) | **associative salad (B′)** |
|---|---|---|
| runs as-shipped | 1 / 4 | **3 / 4** |
| blind-panel axis wins (of 12) | — | **10 / 12** (incl. correctness in all 4) |

The two B′ rescued (Tetris never-locks, Sortviz won't-parse) are exactly the ones the checklist broke.
Dashboard is the **control** — both salad shapes hit the *same* base-model bug (inline `new Chart()`
before the CDN `<script>`), untouched by salad shape. So *"breadth up, depth collapses"* was an
artifact of the **checklist**: a real word salad doesn't inflate scope, and the blind panel judges its
output **more correct and better-designed** than cold. Full correction in
[`results/games/advanced.md`](results/games/advanced.md); reproducible via [`game.py`](game.py).

**The unifying lever.** Priming with a bag of related terms is **one lever** — but its sign flips with
what those terms *mean in the medium*:

| domain | a bag of related terms is… | priming a capable model |
|---|---|---|
| QA (one right answer) | noise, unless there's a knowledge gap | neutral → negative (helps only the 1B) |
| Prose (craft = restraint) | **props** — things to name | **worse** (trope-stuffing; cold wins overall) |
| Code (product = a built thing) | **ingredients** — a better approach | **better** (correct + complete; B′ wins 10/12) |

The earlier "salad = checklist coverage" read was itself an artifact of a checklist-shaped salad. The
truer statement: a real associative salad **helps when the terms are *ingredients* the model can build
with** (code) and **hurts when they're *props* the model merely names** (prose) — and is inert when the
model already knows the answer (QA at the ceiling). Same lever, three signs.

## License

MIT — see [LICENSE](LICENSE).
