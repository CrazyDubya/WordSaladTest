# Creative-Writing Arm — does genre-salad priming improve the 70B's short stories?

A qualitative companion to the QA experiments. The 70B (`@cf/meta/llama-3.3-70b-instruct-fp8-fast`)
writes a short story two ways per genre:

- **A (cold):** *"Write a short story of about 350 words in the &lt;genre&gt; genre."*
- **B (primed):** the same task, prepended with ~50 genre-evocative terms the 70B generates first.

A and B share a sampling seed, so **only the priming differs**. Generation is reproducible
([`story.py`](../../story.py)); judging is **not** — there is no ground truth here.

## ⚠️ Judging caveat

Unlike the QA runs (labels, paired McNemar, p-values), "better story" has **no objective signal**.
Verdicts below come from a **blind LLM panel**: 3 independent judges per genre saw the two stories
as *Story 1 / Story 2* (order mixed, no mention of priming or word-salad) and picked the better /
more genre-authentic one. This is subjective, judges share a model family (correlated taste), and
it is **one story-pair per genre** — a strong qualitative signal, not a measurement.

## Result: 12/12 votes for the UNPRIMED story

| genre | blind-panel verdict |
|---|---|
| noir / hardboiled detective | 3/3 judges → cold (A) for better story AND more authentic |
| cosmic horror (Lovecraftian) | 3/3 judges → cold (A) for better story AND more authentic |

Across both genres and both questions (better story + more genre-authentic), every one of the 6
blind judges preferred the **cold** story. Strikingly, they judged the cold versions *more
authentically* noir / cosmic-horror **even though the primed versions contain more genre
vocabulary** — the salad pushed the 70B to *name* genre tropes ("inventoried clichés", "betrays the
genre by naming its own machinery") instead of dramatizing a scene. More signifiers, weaker story.

This mirrors the QA finding: priming a **capable** model doesn't help and mildly hurts. At the QA
ceiling that was flat/negative accuracy; in prose it's a vocabulary costume that degrades the craft.

---

## Noir / Hardboiled Detective

**Genre salad (50 terms):** rain-soaked streets, femme fatale, whiskey-stained glass, crumpled fedora, cigarette smoke, dark alleyways, trench coat, private eye, jazz club, lonely saxophone, city nightlife, corruption, moral ambiguity, gunslinger, film noir, rainy nights, crime scene, hard-boiled, gumshoe, mysterious stranger, seductive voice, smoky barroom, crime lord, leather-bound wallet, revolver, trenchcoat collar, midnight hour, cigarette butts, lonely office, streetwise, gruff detective, whiskey on the rocks, city streets at night, corrupt cop, mysterious woman, low-key lighting, mean streets, crime-ridden city, dark secrets, double-cross, femme fatale smile, cigarette ash, solitary figure, urban decay, worn leather, lonely hotel room, whiskey-breathed, dark shadows, tough talk, crime fiction

**Blind presentation:** Story 1 = B (primed), Story 2 = A (cold)

### A — cold (no priming)

> Rain poured down like a dirty blanket, shrouding the city in a damp gloom. I stood outside the Red Diamond nightclub, a crummy joint that reeked of stale cigarettes and broken dreams. A femme fatale with legs that went on forever and a smile that could freeze your blood had walked into my office that morning, begging for help. Her sister, a looker named Lola, had gone missing and the cops didn't care.
> 
> I lit a cigarette and watched as the rain-soaked crowd spilled out of the club. A burly bouncer with a face like a slab of granite eyed me from the doorway. I flashed my PI badge and he nodded, stepping aside to let me in.
> 
> The air inside was thick with smoke and desperation. I spotted the owner, a slick operator named Vinnie, holding court at the bar. He was a small-time hood with a reputation for being ruthless. I slid onto the stool next to him and ordered a whiskey.
> 
> Vinnie looked me up and down before nodding at the bartender. "What can I do for you, gumshoe?" he asked, his voice like silk wrapped around a razor.
> 
> "I'm looking for a girl," I said, pulling out a photo of Lola. "She was last seen here, and I heard she might have been in a tight spot with one of your boys."
> 
> Vinnie's smile never wavered, but his eyes flicked to the photo and back to me. "Don't know what you're talking about," he said, his voice dripping with innocence.
> 
> I leaned in close, my eyes locked on his. "Don't play dumb, Vinnie. I know you're hiding something. And if I don't find out what happened to Lola, things are gonna get ugly."
> 
> The bouncer loomed behind me, his massive paws resting on my shoulders. I knew I was taking a risk, but I had to push Vinnie's buttons. The rain pounded against the roof, and for a moment, it was the only sound in the room. Then Vinnie's smile grew wider, and he nodded at the bouncer. "Take our friend here for a little walk," he said, his voice dripping with malice.

### B — genre-salad primed

> It was a rainy night, the kind that made a gumshoe like me want to stay in and drink cheap whiskey. But I had a job to do, and that job was to find the mysterious woman who'd walked into my office earlier that evening. She was a looker, a real femme fatale with a smile that could stop a clock and a voice that could seduce the devil himself.
> 
> She'd come to me with a problem - her sister was missing, and the cops didn't seem to care. I'd taken the case, mostly because I had nothing better to do, and also because I couldn't resist those piercing green eyes. Now, I was standing outside a crummy jazz club on the mean streets of the city, a place where only the desperate and the corrupt came to play.
> 
> I pushed open the door, and a wave of cigarette smoke and stale air washed over me. The sound of a lonely saxophone drifted through the room, and I spotted my quarry sitting at the bar, nursing a whiskey-stained glass. She looked up, caught my eye, and smiled - that femme fatale smile that had gotten me into this mess in the first place.
> 
> I walked over, my trench coat dripping with rain, and sat down beside her. "You're a hard woman to find," I said, signaling the bartender for a drink.
> 
> She laughed, a low, throaty sound. "I'm a hard woman, period," she replied, her eyes glinting in the low-key lighting.
> 
> I raised an eyebrow. "Is that so?" I said, taking a sip of my whiskey. "Well, I'm a hard man. And I aim to find your sister, no matter what it takes."
> 
> She leaned in close, her breath warm against my ear. "Be careful, detective," she whispered. "This city's got a way of eating people alive. And I'm not just talking about the crime lords and the corrupt cops."
> 
> I nodded, feeling a shiver run down my spine. I knew what she was talking about. This city was a dark and twisted place, full of dark secrets and double-crosses. But I was a hard-boiled detective, and I wasn't about to let it get the best of me. Not yet, anyway.

---

## Cosmic Horror (Lovecraftian)

**Genre salad (50 terms):** Eldritch, cyclopean, non-Euclidean, eerie, abyssal, forbidden knowledge, ancient tomes, cursed relics, otherworldly, malevolent deities, sanity-blasting, eerie silences, dimly lit chambers, grotesque, twisted creatures, unfathomable voids, existential dread, macabre, mystical symbols, eerie green glow, abandoned cities, crumbling ruins, forsaken landscapes, eerie whispers, unutterable horrors, eldritch abominations, dark cults, human sacrifices, mysterious artifacts, blasphemous rituals, supernatural entities, unnamable terrors, abyssal horrors, dark dimensions, eerie atmospheres, forsaken souls, haunted minds, paranormal occurrences, unexplained phenomena, cryptic messages, ancient evils, malevolent forces, supernatural powers, occult practices, forbidden rituals, dark magic, eerie shadows, ghostly apparitions, unsettling silence, unutterable names

**Blind presentation:** Story 1 = A (cold), Story 2 = B (primed)

### A — cold (no priming)

> The village of Ravenshurst lay shrouded in an eternal, eerie mist that clung to its crumbling spires like a damp, gray blanket. It was a place where the fabric of reality seemed to unravel, where the skies raged with an otherworldly green glow, and the trees twisted into grotesque, eldritch shapes. I had always been drawn to such forsaken locales, driven by a morbid fascination with the forbidden and the unknown.
> 
> As I delved deeper into the village, the air grew thick with an unsettling, pungent scent, like ozone and decay. The buildings seemed to loom over me, their walls adorned with strange, cyclopean symbols that pulsed with a malevolent energy. Every step I took echoed through the deserted streets, as if I was being herded towards some ancient, eldritch altar.
> 
> I stumbled upon a tattered, leather-bound tome in the ruins of a crumbling church. The cover was embossed with a symbol that seemed to sear itself into my brain, filling my mind with visions of writhing, tentacled horrors that defied human comprehension. As I opened the book, the words within seemed to shift and writhe, like living serpents. The language was unknown, yet I felt an unholy understanding of its dark, arcane secrets.
> 
> The words spoke of Zha'thik, a deity from beyond the stars, who had lain dormant for eons, waiting for the celestial alignments to unleash its unholy power upon the world. The ritual to summon Zha'thik was described in gruesome, meticulous detail, and I felt an overwhelming compulsion to perform it, to unlock the gates of madness and unleash the horror upon the world.
> 
> As I read the final words, the mist around me began to churn and boil, like a living thing. The green glow in the sky intensified, and I felt the weight of Zha'thik's gaze upon me, boring into my soul. I knew then that I was doomed, that I had unleashed a terror beyond human comprehension, and that Ravenshurst would soon be consumed by an eternal, eldritch darkness. The last thing I heard was the sound of my own sanity shattering, like fragile glass dropped upon cold, unforgiving stone.

### B — genre-salad primed

> In the dimly lit chamber, surrounded by ancient tomes and cursed relics, I stumbled upon the forbidden knowledge that would shatter my sanity. The eerie green glow emanating from the mystical symbols etched into the walls seemed to pulse with a malevolent energy, drawing me deeper into the abyssal horrors that lurked within. As I delved into the cryptic messages and blasphemous rituals described in the ancient texts, I began to feel an existential dread that threatened to consume me whole.
> 
> The air was thick with an unsettling silence, punctuated only by the faint whispers of forsaken souls trapped in the dark dimensions that existed beyond our mortal realm. I felt the presence of eldritch abominations lurking just beyond the veil of reality, their twisted creatures and grotesque forms waiting to unleash a terror beyond human comprehension.
> 
> As I read on, the words began to blur and distort, revealing hidden truths that defied the laws of non-Euclidean geometry. The cyclopean ruins that lay hidden beneath the abandoned city seemed to shift and twist, like a living entity, as I uncovered the dark secrets of the supernatural entities that had once worshipped there.
> 
> The more I learned, the more I realized that I was not alone in my quest for knowledge. Dark cults, hiding in the shadows, waited for the perfect moment to strike, using human sacrifices to summon the unnamable terrors that lurked in the void. I felt my mind begin to unravel, haunted by the ghostly apparitions of those who had come before me, their minds shattered by the unutterable horrors they had uncovered.
> 
> And then, I saw it: the eerie silhouette of a malevolent deity, its presence filling the chamber with an unspeakable evil. The last thing I remembered was the feeling of my sanity blasting apart, leaving me a shattered, forsaken soul, lost in a realm of unexplained phenomena and paranormal occurrences, forever trapped in a living nightmare of cosmic horror.

---

