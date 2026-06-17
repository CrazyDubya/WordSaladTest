# Hybrid arm — can a *weak* builder make Pong with a *strong* author's salad?

This crosses the two findings. The cross-author QA result
([`../cross_author.md`](../cross_author.md)) showed a borrowed **frontier** salad helps a weak
*answerer* where its own salad can't — killed only by headroom (the 70B ceiling). Here we ask the
same question on **code**: hand the salad to a weak *builder*.

**Setup.** The **1B** and **3B** each write a single-file HTML Pong three ways, shared seed 4242 so
**only the preamble differs** ([`../../hybrid.py`](../../hybrid.py)):

- **cold** — just the task.
- **own** — primed with a salad the builder generated itself (1B: 31 terms, 3B: 38).
- **claude** — primed with a fixed **Claude Opus 4.8**-authored Pong salad (50 terms, free-association
  — imagery / history / mechanics, *not* a build spec; committed in
  [`pong_hybrid_salads.json`](pong_hybrid_salads.json)).

**Verification is objective, not eyeballed.** Each file is served and loaded headless; we capture JS
console/page errors and read the canvas *backing store* (`getImageData`) at several time points —
foreground-pixel count, bounding box, a per-column histogram (paddle bars / center line), and
centroid shift between frames (a moving ball). A screenshot path was **not** trusted: headless 2D
canvas sometimes composites blank even when the buffer is drawn — `getImageData` is ground truth (a
blank game reads 0 foreground pixels; the working build reads ~2,125 white-on-black across the court).

## Result — 5 of 6 dead; the lone working Pong is **3B × Claude salad**

| builder | cond | loads | renders | JS error | outcome |
|---|---|---|---|---|---|
| 1B | cold   | ✓ | static frame only on keypress (1,140 px), no loop | — | non-functional |
| 1B | own    | ✓ | blank | `Unexpected identifier 'score'` | **syntax error** |
| 1B | claude | ✗ (token cap) | blank | — | **degenerate loop** (214× repeated `osc.onended` block) |
| 3B | cold   | ✓ | blank | `paddleX is not defined` | **runtime error** |
| 3B | own    | ✓ | blank | `playerY is not defined` | **runtime error** |
| **3B** | **claude** | ✓ | **black court + center line + paddles + moving ball** | none | **runs** |

The working build: 640×480 black canvas, white center divider (cols 315–324, 60 px tall), right
paddle (cols 630–639), a player paddle/ball on the left, white centroid shifting ~51 px between
frames. No console errors across the run.

## Finding — headroom, now with a *floor* as well as a ceiling

The QA story was "borrowed strong salad helps any non-saturated answerer, gone at the ceiling." Code
adds the other end:

- **3B (just below capable):** cold and its *own* salad both **crash** (`paddleX` / `playerY`
  undefined — the model loses track of its own variables mid-file). The **Claude salad rescues it** —
  the only run that produced a working, animated Pong. Same shape as QA: a borrowed strong salad pays
  off exactly where the builder is *almost* able but can't get there alone.
- **1B (below threshold):** no salad helps. Its own salad yields a syntax error; cold is inert; and
  the **rich Claude salad makes it *worse*** — the extra context tips the 1B into a degenerate
  repetition loop (200+ identical audio-oscillator blocks until the token cap). Too much to build
  with, not enough capacity to build.

So salad quality is a lever with a **window**: it lifts a builder near the capability threshold (3B)
and *destabilizes* one beneath it (1B). The ceiling (70B, where it's inert) and this new floor (1B,
where it backfires) bracket the regime where a borrowed strong salad actually helps.

**On the token cap:** the 1B/claude file hit `max_tokens=6000` — but raising it would not save the
build. The cap truncated a *runaway* (214 identical `osc.onended` blocks), not a build in progress;
more tokens would yield more of the same loop. The cap was the only thing that stopped it.

**Caveats.** n=1 build per cell (one shared-seed generation each) — a qualitative signal verified
objectively, not a measurement. Temp 0.6. The 1B's near-threshold behavior is exactly where single
draws are noisiest; the direction (Claude salad rescues 3B, destabilizes 1B) is the claim, not the
counts. Reproduce: [`../../hybrid.py`](../../hybrid.py).
