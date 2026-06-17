# Advanced Code Tests — feature-salad priming across 4 harder targets

Following the Pong arm, the 70B (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`) builds four harder
single-file apps, each **cold (A)** vs **salad-primed (B)** (shared seed; salad = ~50 terms about
building a polished version — UX, state, edge cases, accessibility, performance, code structure).
Reproducible via [`game.py --target all`](../../game.py).

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
