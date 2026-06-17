# Code-Generation Arm — does feature-salad priming change the 70B's Pong?

The 70B (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`) writes a single-file HTML/Canvas Pong two ways
(shared seed, so only the priming differs). Reproducible via [`game.py`](../../game.py).

- **A (cold):** *"Create a complete, polished Pong game as a single self-contained HTML file…"*
- **B (primed):** same task, prepended with ~50 terms about building a polished Pong.

**Feature salad (50 terms):** ball physics, collision detection, paddle movement, scoring system, AI opponent, game loop, frame rate, smooth animation, user interface, graphics rendering, sound effects, collision response, bounce logic, velocity calculation, acceleration, deceleration, friction, boundary checking, win condition, lose condition, game over screen, restart mechanism, pause feature, UI buttons, font rendering, text display, scorekeeping, leaderboard, high score tracking, audio feedback, sound waves, collision audio, paddle audio, background music, music volume, sound volume, mute option, game difficulty, AI difficulty levels, easy mode, hard mode, normal mode, paddle speed, ball speed, ball size, paddle size, color scheme, graphics quality, rendering mode, fullscreen mode

## Objective checks (both RUN headless)

Unlike prose, code is partially measurable — both were loaded in a headless browser:

| | A (cold) | B (primed) |
|---|---|---|
| lines | ~152 | ~208 |
| loads without JS errors | yes | yes |
| canvas animating (game loop runs) | yes (600×400) | yes (800×600) |
| DOM UI chrome | none (bare canvas) | scoreboard + Pause button + game-over modal |
| game loop | `requestAnimationFrame` | `setInterval` |
| win condition | none | first to 11 |
| paddle bounds-clamped | yes (player) | **no (player slides off-screen)** |

## Blind panel (3 judges, implementations shown unlabeled, order mixed)

| axis | winner | vote |
|---|---|---|
| Code quality / correctness | **cold (A)** | 3–0 |
| Design / feature completeness | **primed (B)** | 3–0 |
| UI / UX | **primed (B)** | 3–0 |

Unanimous, and split cleanly by axis. Judges independently flagged the cold version's correctness
edge (`requestAnimationFrame`, both paddles clamped, tighter collision) and the primed version's
greater scope (win condition, pause, game-over modal, restart/quit, difficulty scaffold) — *and*
its real flaws: `setInterval`, unclamped player paddle, dead `aiDifficulty` (no control exposes it),
dead canvas-font code, and `position:absolute` UI with no positioned ancestor (anchors to the
viewport, not the game).

## Verdict

**First arm where priming the capable 70B clearly *helped* on an axis.** The salad acted as a
**feature checklist** and the model implemented more of it — winning design and UI/UX — but spread
the same effort over more surface area, *losing* code correctness. Breadth up, depth down.

This is the same lever as the QA and prose arms, with the sign flipped by what the domain rewards:
for a single right answer the salad is noise (neutral/negative); for prose craft it stuffs tropes
(worse); for a software product it adds real features (more complete) at a correctness cost. Priming
redirects effort toward **coverage**, which helps only where coverage is the goal.

Playable files: [`pong_A.html`](pong_A.html) (cold) · [`pong_B.html`](pong_B.html) (primed).

