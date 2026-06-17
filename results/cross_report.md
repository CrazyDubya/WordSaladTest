# Cross-Model Salad — 3B answerer, 70B salad

Arm **X** = 3B answers primed with the **70B**'s salad. Compared to the 3B's own arms (A control · B own salad · C placebo) from the main run.

Headline: **X vs B** — does a stronger model's salad beat the 3B's own?


## openbookqa  (n=500)

| arm | source | acc | 95% CI |
|---|---|---|---|
| A | control | 0.748 | [0.708, 0.784] |
| B | 3B own salad | 0.768 | [0.729, 0.803] |
| X | 70B salad | 0.774 | [0.735, 0.808] |
| C | placebo | 0.708 | [0.667, 0.746] |

- **B→X** (70B salad vs 3B's own salad): X fixed 27, broke 24; Δacc +0.006; McNemar p = 0.7798
- **A→X** (70B salad vs control): X fixed 43, broke 30; Δacc +0.026; McNemar p = 0.1597
- **C→X** (70B salad vs placebo): X fixed 56, broke 23; Δacc +0.066; McNemar p = 0.0003

## commonsenseqa  (n=1221)

| arm | source | acc | 95% CI |
|---|---|---|---|
| A | control | 0.736 | [0.711, 0.760] |
| B | 3B own salad | 0.732 | [0.707, 0.756] |
| X | 70B salad | 0.741 | [0.716, 0.765] |
| C | placebo | 0.702 | [0.676, 0.727] |

- **B→X** (70B salad vs 3B's own salad): X fixed 83, broke 72; Δacc +0.009; McNemar p = 0.4219
- **A→X** (70B salad vs control): X fixed 106, broke 100; Δacc +0.005; McNemar p = 0.7277
- **C→X** (70B salad vs placebo): X fixed 133, broke 85; Δacc +0.039; McNemar p = 0.0014
