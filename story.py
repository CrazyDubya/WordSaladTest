"""Creative-writing arm: does genre-salad priming improve the 70B's short stories?

For each genre, the 70B (a) writes a short story cold (arm A), and (b) writes one
primed with ~50 genre-evocative terms it generates first (arm B). A and B share a
seed so only the priming differs. Unlike the QA experiments there is NO ground
truth — judging is qualitative (a blind LLM panel; see results/stories/creative_writing.md).

Usage:
  CF_API_TOKEN=... CF_ACCOUNT_ID=... python story.py
Output: results/stories/stories.json  (salad terms + story A + story B per genre)
"""
import json
import os

import cf

MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
GENRES = {
    "noir": "noir / hardboiled detective fiction",
    "cosmic": "cosmic horror / Lovecraftian weird fiction",
}
SEED = 4242  # shared by A and B within a genre -> isolates the priming


def genre_salad(genre):
    raw = cf.run(MODEL, [{"role": "user", "content":
        f"Write a word salad of 40 to 60 short phrases about {genre}. Free-associate: "
        f"imagery, mood, atmosphere, objects, settings, character types, sensory detail, "
        f"weather, light -- whatever the genre evokes. Output ONLY a comma-separated list "
        f"of words and short phrases, no sentences, no numbering."}],
        max_tokens=500, temperature=1.0, seed=11)
    return [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()][:60]


def story(genre, terms=None):
    task = f"Write a short story of about 350 words in the {genre} genre. Just the story."
    content = ("Evocative terms: " + ", ".join(terms) + "\n\n" + task) if terms else task
    return cf.run(MODEL, [{"role": "user", "content": content}],
                  max_tokens=700, temperature=0.9, seed=SEED).strip()


def main():
    out = {}
    for key, genre in GENRES.items():
        terms = genre_salad(genre)
        out[key] = {"genre": genre, "terms": terms,
                    "A": story(genre), "B": story(genre, terms)}
        print(f"{key}: {len(terms)} salad terms | "
              f"A ~{len(out[key]['A'].split())}w | B ~{len(out[key]['B'].split())}w")
    os.makedirs("results/stories", exist_ok=True)
    json.dump(out, open("results/stories/stories.json", "w"), indent=2)
    print("saved results/stories/stories.json")


if __name__ == "__main__":
    main()
