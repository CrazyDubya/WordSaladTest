# Advanced Code Tests — feature-salad priming across 4 harder targets

Following the Pong arm, the 70B (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`) builds four harder
single-file apps, each **cold (A)** vs **salad-primed (B)** (shared seed; salad = ~50 terms about
building a polished version — UX, state, edge cases, accessibility, performance, code structure).
Reproducible via [`game.py --target all`](../../game.py).

> **⚠️ Methodology correction (see [Update](#update--re-run-with-a-real-associative-salad) at bottom).**
> The "B" salad here was produced by a prompt that *enumerated engineering dimensions* — a covert
> **spec**, not a free-association **word salad**. A corrected re-run with a genuinely associative
> salad (`<target>_Bprime.html`) **reverses the headline finding below**: the breakage was an
> artifact of the checklist, not of priming.

Two evaluations: **objective runtime** (each file run headless — load errors, render, interaction)
and a **blind 3-judge code panel** per target (files shown as impl1/impl2, order mixed, blind to
which is primed).

## Objective runtime (as-shipped)

| target | A (cold) | B (primed) |
|---|---|---|
| **Tetris** | ✅ playable | ⚠️ runs/animates but **logically broken** — 10×10 grid wiped every frame, pieces never lock, no line clears |
| **Markdown editor** | ✅ works (contenteditable, 7-button toolbar) | ✅ works (**`<textarea>`** + high-contrast a11y toggle, 5 buttons) |
| **Dashboard** | ❌ broken as-shipped (CDN dep + inline code before `<script>`) | ❌ broken as-shipped (same) |
| **Sortviz** | ✅ works (3 algos, animates) | ❌ **dead — fatal syntax error** (`await` outside `async`), script never parses |

Notes: both dashboards depend on the Chart.js CDN (violating "self-contained") *and* place the inline
`new Chart()` code before the library tag → both throw `Chart is not defined`. With script order fixed
and Chart.js vendored, both render, but **B's filter crashes** ("Canvas is already in use" — re-creates
charts without `destroy()`) while A's filter does not.

**Of the 4 advanced targets, the primed build is the broken/worse-on-correctness one in 3** (Tetris,
Dashboard, Sortviz). The cold build is broken only where *both* are (Dashboard).

## Blind code panel (3 judges/target, 12 total)

**Code quality / correctness**

| target | winner | vote | why |
|---|---|---|---|
| Tetris | **cold** | 3–0 | primed never locks pieces (grid rebuilt each frame) |
| Markdown | **primed** | 3–0 | primed uses correct `<textarea>` primitive + a11y; cold's contenteditable feeds dirty HTML to the parser |
| Dashboard | **cold** | 2–1 | primed re-creates charts without `destroy()` (leak/crash); cold uses `chart.update()` |
| Sortviz | **cold** | 3–0 | primed has `await` outside `async` → whole script fails to parse |

**Design / feature completeness**

| target | winner | vote |
|---|---|---|
| Tetris | cold | 3–0 (primed broken) |
| Markdown | cold | 3–0 (more toolbar buttons) |
| Dashboard | **primed** | 3–0 |
| Sortviz | **primed** | 2–1 (richer intent, though it doesn't run) |

**UI / UX**

| target | winner | vote |
|---|---|---|
| Tetris | cold | 3–0 |
| Markdown | **primed** | 3–0 |
| Dashboard | **primed** | 3–0 |
| Sortviz | **primed** | 3–0 (on paper — doesn't execute) |

## What it means

The Pong arm's clean trade — *primed = more features/UX, cold = more correct, both run* — **degrades
as complexity rises.** The extra ambition the salad induces increasingly ships code that doesn't work:
Tetris (logic broken), Dashboard (filter crashes), Sortviz (won't even parse). **Cold won code-quality
in 4 of 5 code targets** (incl. Pong); primed still won UI/UX in 4 of 5 and design in 3 of 5 — it
reliably adds polish and scope, *when the code runs.*

So "breadth up, depth down" sharpens into **"breadth up, depth collapses"** the harder the task: the
salad pushes the model to attempt more, and the more it attempts, the more likely a fatal bug.

**The exception that proves the rule: Markdown.** There priming *improved* correctness (3–0) — the
salad's "accessibility / state management / code structure" terms led the model to the right primitive
(`<textarea>`) and an a11y toggle, where the cold version reached for a buggy contenteditable. When the
salad surfaces a genuinely better approach that's still simple enough to execute, priming helps. When it
just inflates ambition past what the model can land, it breaks things.

Files: `<target>_A.html` (cold) / `<target>_B.html` (primed) for tetris, markdown, dashboard, sortviz.

---

## Update — re-run with a *real* (associative) salad

The salads above came from a prompt that **enumerated engineering dimensions** ("cover UX, state
management, edge cases, accessibility, performance, code structure"). That is a covert *spec*, not
a *word salad* — so the original "B" arm tested **checklist priming**, not word-salad priming. The
fix: regenerate with a free-association prompt — *"write a 50–100 word salad about {topic}"*, where
topic is the **subject** ("Tetris", "sorting algorithms"), not "build a polished version of X." The
result is genuinely associative (Tetris → *Soviet era, Alexey Pajitnov, Russian folk music, Game Boy
obsession*; sorting → *Bach's fugues, moonlit abacus, Tolstoyan complexity*). Same task / seed /
model; only the salad's **shape** changed. Builds saved as `<target>_Bprime.html`.

### Objective runtime (B′ = associative salad), as-shipped

| target | cold A | B (checklist) | **B′ (associative)** |
|---|---|---|---|
| **Tetris** | ✅ plays | ❌ never locks pieces | ✅ falls, moves, **locks & stacks** (verified 8→49 cells) |
| **Markdown** | ✅ works | ✅ works | ✅ works — textarea, live preview, 7-btn toolbar, word count |
| **Sortviz** | ✅ works | ❌ dead (`await` outside `async`) | ✅ parses, animates the sort |
| **Dashboard** | ❌ broken | ❌ broken | ❌ broken — same `Chart is not defined` (CDN + inline-before-`<script>`) |

**Checklist salad → working code in 1 of 4. Associative salad → 3 of 4.** The two B′ rescued
(Tetris, Sortviz) are exactly the ones the checklist *broke*.

### Blind code panel re-run (B′ vs cold A) — 3 judges, neutral filenames, mixed impl1/impl2 order

| target | correctness | design | UI/UX |
|---|---|---|---|
| Tetris | **B′** 3–0 | **B′** 3–0 | cold 3–0 |
| Markdown | **B′** 3–0 | **B′** 3–0 | **B′** 3–0 |
| Dashboard | **B′** 3–0¹ | cold 3–0 | **B′** 3–0 |
| Sortviz | **B′** 3–0 | **B′** 3–0 | **B′** 3–0 |

¹ both dashboards broken (`Chart is not defined`); judges scored cold *more* broken — it also calls a
nonexistent `barChart.getDataForPosition`.

**B′ won 10 of 12 axis contests**, including correctness in all 4 (outright in 3; less-broken in
Dashboard). Cold's only wins: Tetris UI/UX (B′ renders pieces flat black; cold uses 7 distinct
colors) and Dashboard design (B′ re-creates charts without `destroy()`; cold uses `chart.update()`).
Winners split across both impl slots, so the votes track the *primed condition*, not position. Judges
independently rediscovered the runtime bugs (dashboard script-order) and found one the headless probe
missed (cold Tetris rotation writing out of bounds).

### Corrected conclusion

The original panel had **cold winning code-quality in 4 of 5** targets. With a real associative salad
it **flips**: primed wins correctness in 3–4 of 4 and design/UX in 3 of 4. So *"breadth up, depth
collapses"* was an artifact of priming with an engineering **checklist** — the model dutifully
attempted every listed feature and shipped fatal bugs doing so. A genuine word salad does the
opposite: it doesn't inflate scope, and the blind panel judges its output **more correct and
better-designed** than cold. **Dashboard is the control** — both salad shapes hit the identical
base-model bug (inline `new Chart()` before the CDN `<script>`), so the difference on the other three
is attributable to salad *shape*, not chance. (Caveat: Dashboard's CDN dependency means no version is
truly self-contained regardless.)
