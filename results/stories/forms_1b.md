# Forms — does the *same* salad help a poem but hurt a story?

The [prose arm](creative_writing.md) explained its result mechanistically: a genre salad hurts
*narrative* because naming a trope is **telling**, not dramatizing. But imagist **poetry** rewards
naming concrete images. So the mechanism makes a **falsifiable bet**: hand a model the same noir
salad and it should *help the poem* and *hurt the story*. If both move the same way, the
props-vs-ingredients story is incomplete.

The **1B** wrote four texts — {poem, story} × {cold, salad-primed} — shared seed within a form, one
fixed Claude-authored noir salad (32 terms) for both. Texts in [`forms_1b.json`](forms_1b.json); code
[`../../forms.py`](../../forms.py). Blind LLM panel: 3 judges per form, order mixed per judge, no
mention of priming.

## Result — both forms favored the salad (prediction NOT cleanly confirmed)

| form | blind panel | winner |
|---|---|---|
| **Poem**  | salad **3–0** | salad-primed |
| **Story** | salad **2–1** | salad-primed |

The poem panel was unanimous, praising exactly the salad-injected images ("a cigarette's red ember",
"a gun in the glovebox", "blood-stained shirt") over the cold poem's stacked abstractions ("lonely…
desolate… lost souls"). But the *story* also went to the salad — the opposite of the predicted hurt.

## Why the dissociation didn't appear — the prose penalty is competence-gated

The 1B's **cold** story is incoherent: "a320-free laborer", "my name was waiting for me outside",
random "vinyl records". Judges dinged it for *glitchy incoherence*, not for craft. Against that, the
salad-primed story at least sustains a single dramatized scene (a .38 in the glovebox, a ringing
payphone, a coherent menace), so it won 2–1.

That is the key lesson: **naming a prop is only a sin when the writer is good enough that restraint is
the operative virtue.** On the 70B (the [prose arm](creative_writing.md)) the cold story was already
coherent and craftful, so the salad's trope-naming was a net *negative* (12/12, then 5–1 against). On
the 1B the cold story is barely coherent, so the salad's concrete nouns are scaffolding — they *raise*
the floor. The prose-hurt effect needs headroom, exactly like every other lever in this project: it
appears once the model is competent enough for the penalty to bite.

Directionally there is still a gradient in the predicted direction — the salad helped the poem *more*
(3–0) than the story (2–1) — but on n=1 pairs that gap is not a result. **The clean poem-vs-story
dissociation test wants a competent writer (the 70B), not the 1B floor**, where material, not
restraint, is the bottleneck for both forms.

**Caveats.** One text-pair per form (n=1 per cell), judges share a model family (correlated taste).
A qualitative probe of the *mechanism*, not a measurement — and an honest non-confirmation: scoping
the test to the 1B answered a different question (salad helps a floundering writer in any form) than
the one the prediction was about.
