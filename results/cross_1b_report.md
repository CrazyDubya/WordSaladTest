# Cross-Model Salad — 1b answerer, 70B salad

Arm **X** = the 1b model answers primed with the **70B**'s salad. Compared to its own arms (A control · B own salad · C placebo) from the main run.

Headline: **X vs B** — does a stronger model's salad beat the answerer's own?


## openbookqa  (n=500)

| arm | source | acc | 95% CI |
|---|---|---|---|
| A | control | 0.354 | [0.313, 0.397] |
| B | 1b own salad | 0.444 | [0.401, 0.488] |
| X | 70B salad | 0.434 | [0.391, 0.478] |
| C | placebo | 0.350 | [0.309, 0.393] |

- **B→X** (70B salad vs 1b's own salad): X fixed 23, broke 28; Δacc -0.010; McNemar p = 0.5758
- **A→X** (70B salad vs control): X fixed 53, broke 13; Δacc +0.080; McNemar p = 0.0000
- **C→X** (70B salad vs placebo): X fixed 54, broke 12; Δacc +0.084; McNemar p = 0.0000

## commonsenseqa  (n=1221)

| arm | source | acc | 95% CI |
|---|---|---|---|
| A | control | 0.387 | [0.360, 0.414] |
| B | 1b own salad | 0.417 | [0.390, 0.445] |
| X | 70B salad | 0.500 | [0.472, 0.528] |
| C | placebo | 0.375 | [0.348, 0.403] |

- **B→X** (70B salad vs 1b's own salad): X fixed 164, broke 63; Δacc +0.083; McNemar p = 0.0000
- **A→X** (70B salad vs control): X fixed 221, broke 83; Δacc +0.113; McNemar p = 0.0000
- **C→X** (70B salad vs placebo): X fixed 225, broke 73; Δacc +0.124; McNemar p = 0.0000
