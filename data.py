"""Benchmark loaders, normalized to one item shape.

item = {
  "id": str, "bench": str, "stem": str,
  "choices": [(letter, text), ...], "gold": letter
}
"""
from datasets import load_dataset


def _normalize(row, bench, stem_field):
    labels = row["choices"]["label"]
    texts = row["choices"]["text"]
    return {
        "id": row["id"],
        "bench": bench,
        "stem": row[stem_field],
        "choices": list(zip(labels, texts)),
        "gold": row["answerKey"].strip(),
    }


def _openbookqa():
    ds = load_dataset("allenai/openbookqa", "main", split="test")  # 500, labeled
    return [_normalize(r, "openbookqa", "question_stem") for r in ds]


def _commonsenseqa():
    ds = load_dataset("tau/commonsense_qa", split="validation")  # 1221, labeled
    return [_normalize(r, "commonsenseqa", "question") for r in ds]


LOADERS = {"openbookqa": _openbookqa, "commonsenseqa": _commonsenseqa}


def load(bench, limit=None):
    items = LOADERS[bench]()
    return items[:limit] if limit else items
