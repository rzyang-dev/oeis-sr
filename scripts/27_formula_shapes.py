#!/usr/bin/env python3
"""Shape inventory of OEIS formulas: what syntactic forms do they take?

For every 'a(n) = ...' formula line we extract a coarse shape:

    (leading construct, set of features)

and count how concentrated the distribution is.  If a few shapes cover most of
the corpus, a symbolic-regression system should enumerate shapes, not trees.

    python scripts/27_formula_shapes.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "formula_shapes.json"

ATTR = re.compile(r"\s*-\s*_[^_]+_,.*$")
REF = re.compile(r"A\d{6}")

FEATURES = [
    ("sum", lambda t: "Sum_{" in t or "sum_" in t.lower()),
    ("prod", lambda t: "Product_{" in t or "prod_" in t.lower()),
    ("binom", lambda t: "binomial(" in t or re.search(r"\bC\(", t)),
    ("fact", lambda t: "!" in t and "!=" not in t),
    ("pow", lambda t: "^" in t or "**" in t),
    ("div", lambda t: "/" in t),
    ("sqrt", lambda t: "sqrt" in t.lower()),
    ("floor", lambda t: "floor" in t.lower()),
    ("mod", lambda t: " mod " in t or "%" in t),
    ("log", lambda t: "log" in t.lower()),
    ("exp", lambda t: "exp(" in t.lower()),
    ("trig", lambda t: any(f in t for f in ("sin", "cos", "tan"))),
    ("ref", lambda t: bool(REF.search(t))),
    ("k", lambda t: bool(re.search(r"\bk\b", t))),
    ("prime", lambda t: "prime" in t.lower() or "A000040" in t),
    ("partition", lambda t: "partition" in t.lower()),
]


def shape_of(text: str):
    t = ATTR.sub("", text).strip()
    feats = frozenset(name for name, fn in FEATURES if fn(t))
    lead = "other"
    stripped = re.sub(r"^a\(n\)\s*=\s*", "", t)
    if stripped.startswith("Sum_"):
        lead = "sum"
    elif stripped.startswith("Product_"):
        lead = "prod"
    elif re.match(r"^\(?\s*[-+]?\d+\s*\)?\s*[*^]", stripped):
        lead = "scaled"
    elif REF.search(stripped[:20]):
        lead = "ref"
    elif "^" in stripped:
        lead = "pow"
    elif "/" in stripped:
        lead = "fraction"
    return lead, feats


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute(
        "select text from formula where text like 'a(n) =%'").fetchall()
    print("formula lines:", len(rows))

    counter = Counter()
    lead_counter = Counter()
    examples = {}
    for (text,) in rows:
        lead, feats = shape_of(text)
        lead_counter[lead] += 1
        key = (lead, tuple(sorted(feats)))
        counter[key] += 1
        examples.setdefault(key, text[:100])

    total = len(rows)
    print("\nleading construct:")
    for k, v in lead_counter.most_common():
        print(f"  {k:10} {v:>7}  ({100*v/total:.1f}%)")

    print("\ntop shapes:")
    acc = 0
    top = []
    for (lead, feats), v in counter.most_common(25):
        acc += v
        top.append({"lead": lead, "feats": list(feats), "n": v,
                    "cum_pct": round(100*acc/total, 1), "example": examples[(lead, feats)]})
        print(f"  {lead:9} +{','.join(feats)[:46]:46} {v:>7}  cum {100*acc/total:5.1f}%")

    print(f"\ndistinct shapes: {len(counter)}")
    for k in (10, 50, 100, 500):
        acc = sum(v for _, v in counter.most_common(k))
        print(f"  top {k:>3} shapes cover {100*acc/total:.1f}% of formulas")

    OUT.write_text(json.dumps({"total": total,
                               "leading": dict(lead_counter),
                               "n_shapes": len(counter),
                               "top": top}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
