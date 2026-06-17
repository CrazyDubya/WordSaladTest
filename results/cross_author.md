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

## Full attenuation curve — Claude's salad across all four answerers

Holding the *author* fixed (Claude) and sweeping the **answerer** (same 500-item sample, salads reused;
arms in `cross_{1b,3b,8b,70b}_claude.jsonl`):

| answerer | bench | control | own salad | **Claude** | Claude − control | Claude − own |
|---|---|---|---|---|---|---|
| 1B  | OpenBookQA    | .305 | .430 | .410 | **+.105** (p<.001) | −.020 (.57) |
| 1B  | CommonsenseQA | .417 | .463 | **.563** | **+.147** (p<.001) | **+.100** (p<.001) |
| 3B  | OpenBookQA    | .745 | .755 | .780 | +.035 (.27) | +.025 (.41) |
| 3B  | CommonsenseQA | .713 | .727 | .757 | +.043 (.13) | +.030 (.25) |
| 8B  | OpenBookQA    | .800 | .825 | .860 | **+.060** (.02) | +.035 (.17) |
| 8B  | CommonsenseQA | .703 | .743 | .790 | **+.087** (.001) | +.047 (.07) |
| 70B | OpenBookQA    | .930 | .930 | .935 | +.005 (1.0) | +.005 (1.0) |
| 70B | CommonsenseQA | .843 | .853 | .847 | +.003 (1.0) | −.007 (.82) |

## Verdict — two effects, two different decays

**1. Borrow-a-salad (Claude − control):** a frontier-authored salad helps *any non-saturated* answerer —
significant at the 1B (+.10/+.15) **and the 8B** (+.06/+.09), positive-but-ns at the 3B, and **zero at
the 70B ceiling** (+.005/+.003). The benefit is killed by *headroom* (gone once the model saturates),
not by answerer strength as such.

**2. Author premium (Claude − own salad):** beating the model's *own* salad is large only at the **1B**
(+.100 on CommonsenseQA, p<.001), fades to marginal at the 8B (+.047, p=.07) and ns at the 3B, and is
zero at the 70B. So **who writes the salad matters most exactly where the answerer is least able to
write a good one itself.**

This **revises** the pilot's first guess that the author effect would "vanish for capable answerers" —
it does **not**: Claude's salad significantly beats control even at the 8B, *where the 8B's own salad
never did* (main-run B−A was ns for 8B). What attenuates is the *premium over self-authoring*; the
borrow-a-salad benefit persists until the model saturates. As always, the task matters — CommonsenseQA
(broad association) shows larger effects than OpenBookQA (one retrieved fact).

**Caveats:** Claude's salads are model generations (not seed-reproducible like the Llama arms; committed
in [`cross_1b_claude_salads.json`](cross_1b_claude_salads.json) for exact reuse — the same 500 salads
were reused across all four answerers). Cells are n=200 (OBQA) / 300 (CSQA); the 3B's positive-but-ns
deltas and the 3B<8B dip on Claude−control are within noise (both 3B ps non-significant). The
Claude-vs-70B *author* comparison on the 1B (+3.7, p=.14 at n=300) remains unresolved at this n.
Sampled ids in [`cross_1b_claude_sample.json`](cross_1b_claude_sample.json).
