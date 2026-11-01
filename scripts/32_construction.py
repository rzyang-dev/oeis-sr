#!/usr/bin/env python3
"""Classify the non-C-finite part of OEIS by construction type.

Uses the entry name and all formula lines.  The categories are heuristic but
interpretable; the goal is to see WHAT the combinatorial core is made of.

    python scripts/32_construction.py
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
OUT = ROOT / "reports" / "constructions.json"

RULES = [
    ("set_partition", re.compile(r"stirling|bell number|set partition|partitions? of the set|partitions? of \[n\]", re.I)),
    ("partition", re.compile(r"\bpartition", re.I)),
    ("prime", re.compile(r"\bprime|\bprimes\b", re.I)),
    ("divisor", re.compile(r"\bdivisor|sigma|\bphi\(|totient|mobius|\bmu\(|\bomega\b|\bOmega\b", re.I)),
    ("graph", re.compile(r"\bgraph|\btree|\bposet|\bforest|digraph|hypergraph|\bmatroid", re.I)),
    ("permutation", re.compile(r"permutation|involution|derangement", re.I)),
    ("path", re.compile(r"\bwalk|\bpath\b|lattice|motzkin|dyck|polyomino", re.I)),
    ("digit", re.compile(r"\bdigit|decimal|binary|\bbase\b|number of 1's", re.I)),
    ("arrangement", re.compile(r"polygon|polytope|tiling|tessellat|arrangement|covering|packing", re.I)),
    ("words", re.compile(r"\bword|\bstring|sequence of 0|binary sequence|composition", re.I)),
    ("automaton", re.compile(r"cellular automaton|\brule \d+|\bautomaton", re.I)),
    ("matrix", re.compile(r"\bmatrix|determinant|permanent|eigenvalue", re.I)),
    ("game", re.compile(r"\bgame|\bnim\b|chess|queen|knight|maze|puzzle", re.I)),
    ("table", re.compile(r"triangle|array|table read by|square array|read by antidiagonals", re.I)),
    ("counting", re.compile(r"^number of|number of ways|counts the number|number of such", re.I)),
    ("continued_fraction", re.compile(r"continued fraction|convergents", re.I)),
    ("cyclotomic", re.compile(r"cyclotomic|chebyshev|legendre|hermite|\bbessel", re.I)),
    ("zeolite", re.compile(r"zeolite|coordination sequence", re.I)),
    ("moonshine", re.compile(r"mckay|moonshine|\bmonster\b|thompson series", re.I)),
    ("lexicographic", re.compile(r"lexicographically earliest|earliest infinite|earliest sequence", re.I)),
    ("floor_round", re.compile(r"\bfloor\b|nearest integer|\bround\b|\bceiling\b", re.I)),
    ("modular", re.compile(r"\bmod\b|modulo|congruent|\bresidue", re.I)),
    ("expansion", re.compile(r"expansion of|generating function|g\.f\.", re.I)),
    ("sum_convolution", re.compile(r"Sum_\{|convolution|binomial transform|inverse binomial", re.I)),
    ("recurrence", re.compile(r"a\(n\)\s*=\s*a\(n\s*-", re.I)),
]


def classify(name: str, formulas: str) -> str:
    text = name + " " + formulas
    for cat, rx in RULES:
        if rx.search(text):
            return cat
    return "other"


def main() -> int:
    con = sqlite3.connect(str(DB))
    noncf = [r[0] for r in con.execute(
        "select aid from seq_exact where method='' or method is null")]
    print("non-C-finite sequences:", len(noncf))

    names = dict(con.execute("select aid, name from seq"))
    ftext = defaultdict(list)
    for aid, text in con.execute("select aid, text from formula"):
        ftext[aid].append(text)

    cat = {}
    for aid in noncf:
        cat[aid] = classify(names.get(aid, ""), " ".join(ftext.get(aid, []))[:2000])

    con.execute("DROP TABLE IF EXISTS construction")
    con.execute("CREATE TABLE construction (aid TEXT PRIMARY KEY, category TEXT, n_formulas INTEGER)")
    con.executemany("INSERT INTO construction VALUES (?,?,?)",
                    [(a, c, len(ftext.get(a, []))) for a, c in cat.items()])
    con.execute("CREATE INDEX idx_constr ON construction(category)")
    con.commit()

    cnt = Counter(cat.values())
    print("\nconstruction categories (non-C-finite):")
    for k, v in cnt.most_common():
        print(f"  {k:16} {v:>6} ({100*v/len(noncf):5.1f}%)")

    # growth and solvability cross-tabs
    print("\nby growth class (top categories):")
    tab = defaultdict(Counter)
    for aid, g in con.execute("""select c.aid, f.growth from construction c
            join seq_fingerprint f on f.aid=c.aid"""):
        pass
    for aid, category in cat.items():
        pass
    rows = con.execute("""select c.category, f.growth, count(*) from construction c
            join seq_fingerprint f on f.aid=c.aid group by 1,2""").fetchall()
    tot = Counter()
    for category, g, n in rows:
        tab[category][g] += n
        tot[category] += n
    for category in [k for k, _ in cnt.most_common(8)]:
        tot_c = tot[category]
        top = tab[category].most_common(3)
        s = ", ".join(f"{g} {100*n/tot_c:.0f}%" for g, n in top)
        print(f"  {category:16} {s}")

    print("\nsolvability on hard targets by category:")
    rows = con.execute("""select c.category,
              sum(case when s.method<>'' then 1 else 0 end), count(*)
            from construction c join hard_solved s on s.aid=c.aid group by 1""").fetchall()
    for category, ok, n in sorted(rows, key=lambda r: -r[2]):
        if n >= 50:
            print(f"  {category:16} {ok:>4}/{n:<5} {100*ok/n:5.1f}%")

    OUT.write_text(json.dumps({"n_noncf": len(noncf), "counts": dict(cnt)},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
