# Word-Salad Priming — Results

Arms: **A** direct · **B** related-term salad · **C** placebo (count/position-matched unrelated words).


## @cf/meta/llama-3.1-8b-instruct-fp8 — commonsenseqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 1221 | 0.752 | [0.727, 0.775] | 1 |
| B | 1221 | 0.750 | [0.725, 0.774] | 2 |
| C | 1221 | 0.712 | [0.686, 0.736] | 1 |

- **A→B** (does the salad help vs control): B fixed 101, broke 103 (of 1221 paired); McNemar p = 0.9442
- **C→B** (does relevance beat a matched placebo): B fixed 136, broke 89 (of 1221 paired); McNemar p = 0.0021

## @cf/meta/llama-3.1-8b-instruct-fp8 — openbookqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 500 | 0.774 | [0.735, 0.808] | 0 |
| B | 500 | 0.802 | [0.765, 0.835] | 0 |
| C | 500 | 0.748 | [0.708, 0.784] | 0 |

- **A→B** (does the salad help vs control): B fixed 40, broke 26 (of 500 paired); McNemar p = 0.1089
- **C→B** (does relevance beat a matched placebo): B fixed 56, broke 29 (of 500 paired); McNemar p = 0.0045

## @cf/meta/llama-3.2-1b-instruct — commonsenseqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 1221 | 0.387 | [0.360, 0.414] | 1 |
| B | 1221 | 0.417 | [0.390, 0.445] | 1 |
| C | 1221 | 0.375 | [0.348, 0.403] | 1 |

- **A→B** (does the salad help vs control): B fixed 128, broke 91 (of 1221 paired); McNemar p = 0.0148
- **C→B** (does relevance beat a matched placebo): B fixed 132, broke 81 (of 1221 paired); McNemar p = 0.0006

## @cf/meta/llama-3.2-1b-instruct — openbookqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 500 | 0.354 | [0.313, 0.397] | 0 |
| B | 500 | 0.444 | [0.401, 0.488] | 0 |
| C | 500 | 0.350 | [0.309, 0.393] | 0 |

- **A→B** (does the salad help vs control): B fixed 56, broke 11 (of 500 paired); McNemar p = 0.0000
- **C→B** (does relevance beat a matched placebo): B fixed 57, broke 10 (of 500 paired); McNemar p = 0.0000

## @cf/meta/llama-3.2-3b-instruct — commonsenseqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 1221 | 0.736 | [0.711, 0.760] | 0 |
| B | 1221 | 0.732 | [0.707, 0.756] | 0 |
| C | 1221 | 0.702 | [0.676, 0.727] | 0 |

- **A→B** (does the salad help vs control): B fixed 100, broke 105 (of 1221 paired); McNemar p = 0.7800
- **C→B** (does relevance beat a matched placebo): B fixed 122, broke 85 (of 1221 paired); McNemar p = 0.0122

## @cf/meta/llama-3.2-3b-instruct — openbookqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 500 | 0.748 | [0.708, 0.784] | 0 |
| B | 500 | 0.768 | [0.729, 0.803] | 0 |
| C | 500 | 0.708 | [0.667, 0.746] | 0 |

- **A→B** (does the salad help vs control): B fixed 39, broke 29 (of 500 paired); McNemar p = 0.2750
- **C→B** (does relevance beat a matched placebo): B fixed 58, broke 28 (of 500 paired); McNemar p = 0.0016

## @cf/meta/llama-3.3-70b-instruct-fp8-fast — commonsenseqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 1221 | 0.839 | [0.818, 0.859] | 0 |
| B | 1221 | 0.826 | [0.804, 0.847] | 1 |
| C | 1221 | 0.824 | [0.802, 0.844] | 0 |

- **A→B** (does the salad help vs control): B fixed 42, broke 58 (of 1221 paired); McNemar p = 0.1332
- **C→B** (does relevance beat a matched placebo): B fixed 77, broke 74 (of 1221 paired); McNemar p = 0.8708

## @cf/meta/llama-3.3-70b-instruct-fp8-fast — openbookqa

| arm | n | acc | 95% CI | parse-fail |
|---|---|---|---|---|
| A | 500 | 0.934 | [0.909, 0.953] | 1 |
| B | 500 | 0.920 | [0.893, 0.941] | 0 |
| C | 500 | 0.904 | [0.875, 0.927] | 7 |

- **A→B** (does the salad help vs control): B fixed 12, broke 19 (of 500 paired); McNemar p = 0.2810
- **C→B** (does relevance beat a matched placebo): B fixed 27, broke 19 (of 500 paired); McNemar p = 0.3020
