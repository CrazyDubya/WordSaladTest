# Cross-Author Salad — does it matter *who wrote the salad*?

The [cross-model experiment](../cross.py) showed a stronger *answerer*-vs-*author* split: the 70B's
salad helped the 1B but not the 3B. This arm isolates the **author** axis directly — hold the
answerer fixed (the weak **1B**) and swap only **who authored** the related-term salad:

| arm | salad author | source |
|---|---|---|
| A | — (control, no preamble) | main run |
| C | placebo (count-matched mundane words) | main run |
| B | **the 1B itself** | main run |
| X | **the 70B** | [`cross_1b.jsonl`](cross_1b.jsonl) |
| **Z** | **Claude (Opus 4.8)** | [`cross_1b_claude.jsonl`](cross_1b_claude.jsonl) |

Claude's salads were authored by fanned-out Claude subagents following the **same 50-term spec** the
Llama models got (`arms.salad_messages`: "List 50 single words or short phrases closely related to the
topic… comma-separated", **choices withheld** so the salad can't leak the answer). The 1B then answers
each item primed with that salad (temp 0, seed 42 — identical to every other arm). Sample: **200
OpenBookQA + 300 CommonsenseQA**, seeded (1234). Paired exact **McNemar** on the shared items.

## CommonsenseQA (n=300) — author quality has a large, significant effect

| author | acc | 95% CI | vs control | vs 1B-own |
|---|---|---|---|---|
| control | .417 | [.362, .473] | — | — |
| placebo | .413 | [.359, .470] | — | — |
| 1B's own | .463 | [.408, .520] | +.047 (p=.076) | — |
| 70B | .527 | [.470, .582] | +.110 (p<.0001) | +.064 |
| **Claude** | **.563** | [.507, .618] | **+.147 (p<.0001)** | **+.100 (p=.0003)** |

**Ranking: Claude > 70B > 1B-own > control ≈ placebo.** Claude's salad lifts the 1B **+14.7 pts over
control** and **+10.0 over the 1B's own salad** — both significant. Claude edges the 70B by +3.7 but
that is **not** significant (p=.14): Claude and 70B are statistically tied at the top, both clearly
above the model's own salad.

## OpenBookQA (n=200) — author is irrelevant

| author | acc | 95% CI |
|---|---|---|
| control | .305 | [.245, .372] |
| placebo | .310 | [.250, .377] |
| 1B's own | .430 | [.363, .499] |
| 70B | .410 | [.344, .479] |
| Claude | .410 | [.344, .479] |

Every salad helps over control (~+.10), but **no author beats another**: Claude vs 1B-own p=.57,
Claude vs 70B p=1.00. Fact-retrieval (OpenBookQA) doesn't care who wrote the associations; broad
commonsense reasoning does.

## Verdict

**Salad author is a real lever — but gated by *(weak answerer) × (association-heavy task)*.** A
stronger author (70B or Claude) lifts the knowledge-starved 1B by ~10–15 pts on CommonsenseQA, where
broad associative context substitutes for missing knowledge; it does nothing extra on OpenBookQA,
where the task is one specific retrieved fact. This is the Generated-Knowledge-Prompting effect
(Liu et al. 2022) sharpened to the author axis: *whose* knowledge you borrow matters, when you have a
gap and the task rewards breadth.

The same gating predicts most of a full author×answerer matrix would be **null**: the cross-model run
already showed the 70B's salad gave the *3B* no lift (its own knowledge sufficed), so for capable
answerers the author effect should vanish regardless of who writes the salad. Targeted follow-ups
(full-CSQA Claude-vs-70B on the 1B; an 8B answerer to confirm the effect disappears) test that
directly instead of grinding the grid.

**Caveats:** Claude's salads are model generations (not seed-reproducible like the Llama arms — the
salads themselves are committed in [`cross_1b_claude_salads.json`](cross_1b_claude_salads.json) for
exact reuse). CommonsenseQA cell is n=300 (pilot); the Claude-vs-70B gap (+3.7, p=.14) is unresolved
at this n. Sampled item ids in [`cross_1b_claude_sample.json`](cross_1b_claude_sample.json).
