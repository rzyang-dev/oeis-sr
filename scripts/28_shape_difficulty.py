#!/usr/bin/env python3
"""Join formula shape with solvability on the hard track.

    python scripts/28_shape_difficulty.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "shape_difficulty.json"

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
    stripped = re.sub(r"^a\(n\)\s*=\s*", "", t)
    lead = "other"
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
    rows = con.execute("""
        SELECT h.aid, h.expr, s.method FROM hard_bench h
        JOIN hard_solved s ON s.aid = h.aid WHERE h.hard = 1""").fetchall()
    print("hard targets with solver results:", len(rows))

    by_lead = defaultdict(lambda: [0, 0])
    by_shape = defaultdict(lambda: [0, 0])
    for aid, expr, method in rows:
        lead, feats = shape_of(expr)
        solved = 1 if method else 0
        by_lead[lead][0] += solved
        by_lead[lead][1] += 1
        key = (lead, tuple(sorted(feats)))
        by_shape[key][0] += solved
        by_shape[key][1] += 1

    print("\nsolvability by leading construct:")
    out_lead = {}
    for lead, (ok, n) in sorted(by_lead.items(), key=lambda kv: -kv[1][1]):
        out_lead[lead] = {"solved": ok, "n": n, "rate": round(100*ok/n, 1)}
        print(f"  {lead:10} {ok:>5}/{n:<5}  {100*ok/n:5.1f}%")

    print("\nsolvability by top shapes (>=100 targets):")
    out_shape = []
    for (lead, feats), (ok, n) in sorted(by_shape.items(), key=lambda kv: -kv[1][1])[:25]:
        if n < 100:
            continue
        out_shape.append({"lead": lead, "feats": list(feats), "solved": ok,
                          "n": n, "rate": round(100*ok/n, 1)})
        print(f"  {lead:9} +{','.join(feats)[:44]:44} {ok:>4}/{n:<4} {100*ok/n:5.1f}%")

    OUT.write_text(json.dumps({"by_lead": out_lead, "by_shape": out_shape},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
