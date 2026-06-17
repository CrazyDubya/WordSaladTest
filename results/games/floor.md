# Floor experiments — picking apart the 1B builder

The [hybrid arm](hybrid_pong.md) found a capability *window*: a borrowed Claude salad rescued the **3B**
builder but destabilized the **1B** into a degenerate repetition loop. That was n=1 per cell. These
three probes pin down the 1B floor — all 1B Pong, served and verified headless (JS-error capture +
`getImageData` backing-store probe; same method as the hybrid arm). Code in [`../../floor.py`](../../floor.py),
per-build verdicts in [`floor/floor_verify.json`](floor/floor_verify.json).

## #2 Replication — the floor is real; the salad never rescues the 1B

cold / own / claude across 5 build seeds (4242 from the hybrid run + 7/13/21/99), shared-seed within
a cell so only the preamble varies:

| seed | cold | own salad | Claude salad |
|---|---|---|---|
| 4242 | blank | syntax error | **degenerate loop** |
| 7    | **animated ✓** | blank | **degenerate loop** |
| 13   | blank (404) | syntax error | runtime error |
| 21   | empty (13 lines) | syntax error | syntax error |
| 99   | runtime error | syntax error | runtime error |

**1 working Pong in 15 cells — and it was *cold*.** The 1B can *occasionally* stumble into a running
Pong with no preamble (1/5 seeds), but the Claude salad produces a working build **0/5** times —
degenerate twice, error three times. So on the 1B the rich salad doesn't just fail to help, it
**lowers the hit rate** (1/5 cold → 0/5 claude). Its own salad is the most reliably broken (syntax
error 4/5). This is the exact mirror of the 3B, where the Claude salad was the *only* thing that
worked — a genuine sign flip across one model size.

## #4 Dose — failure severity scales with salad length

Length prefixes of the same 50-term Claude salad, seed 4242 (N=50 is the hybrid `pong_1b_claude` build):

| terms | outcome |
|---|---|
| 5  | blank (ignored — like cold) |
| 15 | runtime error (`game.init is not a function`) |
| 30 | runtime error (`Cannot read properties of null`) |
| 50 | **degenerate repetition loop** |

A clean dose-response in *how it breaks*: a short salad is inert (the 1B ignores it, same as cold);
as length grows the 1B attempts more and breaks harder, tipping into the runaway loop only at full
length. The destabilization is a function of dose — the same shape as a context getting long enough
to collapse coherent generation, now in code.

## #1 Ablation — no category of term rescues the 1B

The 50-term salad split by category (~length-matched so *content* is the variable), seed 4242:

| sub-salad | terms | outcome |
|---|---|---|
| mechanics (paddles, bounce, vector of reflection…) | 18 | syntax error (`Unexpected identifier 'paddle1'`) |
| imagery (scanlines, phosphor, pixel dust…) | 17 | syntax error (`'rect' already declared`) |
| history (Atari 1972, Allan Alcorn, Odyssey…) | 15 | blank (ignored) |

None rescues. Weakly suggestive: the *actionable* categories (mechanics, imagery) push the 1B to
attempt more structure — and break it (syntax errors) — while *history* terms it simply ignores
(blank, like cold). But "attempt more and fail" is not a rescue. **The mechanism question — does
mechanics-content specifically rescue a builder — belongs on the 3B, where the rescue actually
happened.** This 1B ablation only confirms the floor: below the capability threshold, term *content*
changes the failure mode, not the outcome.

## Synthesis — a floor to match the 70B ceiling

Priming-with-a-salad helps code generation only inside a capability window. Above it (70B) salad is
inert; at the threshold (3B) a *strong* salad rescues; **below it (1B) a strong salad backfires** —
inert when short, breaking when longer, looping at full length, and net-negative versus cold. The
"ingredients help" story for code holds only where the builder is good enough to cook with them.

**Caveats.** Single build per cell except the 1B replication (5 seeds). The headless classifier flags
any console error — including resource-404s (the two `cold` 404 cells) — as a failure; those may be
blank rather than crashed, but neither renders. The 3B side of the crossover is still n=1 (the hybrid
build); replicating the 3B rescue across seeds is the natural next step.
