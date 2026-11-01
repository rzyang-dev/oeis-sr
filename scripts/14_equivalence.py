#!/usr/bin/env python3
"""Equivalence classes over sequences, from the exact numeric relations.

Two notions are built:

  exact_class   union over {equal, affine} relations -- the same sequence up to a
                scaling/translation, i.e. the real "duplicate" unit
  leak_group    union over {equal, affine, prefix} -- also merges a sequence with
                the one it is the prefix sum of, because knowing one makes the
                other trivial.  This is the unit for train/test splitting.

Writes table seq_class(aid, exact_class, leak_group) and
reports/equivalence.json.

    python scripts/14_equivalence.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "equivalence.json"


class DSU:
    def __init__(self) -> None:
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        p = self.p
        p.setdefault(x, x)
        root = x
        while p[root] != root:
            root = p[root]
        while p[x] != root:
            p[x], x = root, p[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def main() -> int:
    con = sqlite3.connect(str(DB))
    pairs = con.execute("select aid, dst, kind from numeric_relation").fetchall()
    print("numeric pairs:", len(pairs))

    exact, leak = DSU(), DSU()
    for a, b, kind in pairs:
        if kind in ("equal", "affine"):
            exact.union(a, b)
        leak.union(a, b)

    # every sequence is in its own class by default
    all_ids = [r[0] for r in con.execute("select aid from seq")]
    for aid in all_ids:
        exact.find(aid)
        leak.find(aid)

    def classes(dsu: DSU):
        groups = defaultdict(list)
        for x in dsu.p:
            groups[dsu.find(x)].append(x)
        return groups

    ce, cl = classes(exact), classes(leak)
    print(f"exact classes: {len(ce):,}  (multi-member: {sum(1 for v in ce.values() if len(v)>1):,})")
    print(f"leak groups:   {len(cl):,}  (multi-member: {sum(1 for v in cl.values() if len(v)>1):,})")
    print("exact size hist:", sorted(__import__('collections').Counter(len(v) for v in ce.values()).items())[:6])
    print("leak  size hist:", sorted(__import__('collections').Counter(len(v) for v in cl.values()).items())[:6])

    con.execute("DROP TABLE IF EXISTS seq_class")
    con.execute("CREATE TABLE seq_class (aid TEXT PRIMARY KEY, exact_class INTEGER, leak_group INTEGER)")
    rows = []
    for i, (root, members) in enumerate(ce.items()):
        for m in members:
            rows.append((m, i, None))
    # reassign leak group ids
    leak_id = {root: i for i, root in enumerate(cl)}
    rows = [(a, ec, leak_id[leak.find(a)]) for a, ec, _ in rows]
    con.executemany("INSERT INTO seq_class VALUES (?,?,?)", rows)
    con.execute("CREATE INDEX idx_seqclass_exact ON seq_class(exact_class)")
    con.execute("CREATE INDEX idx_seqclass_leak ON seq_class(leak_group)")
    con.commit()
    print("seq_class rows:", len(rows))

    # examples of largest exact classes
    name = dict(con.execute("select aid, name from seq"))
    biggest = sorted(ce.values(), key=len, reverse=True)[:5]
    print("\nlargest exact classes:")
    for v in biggest:
        print(f"  {len(v):>4}: {v[:5]}")
        print(f"        {name[v[0]][:80]}")

    out = {
        "numeric_pairs": len(pairs),
        "sequences": len(all_ids),
        "exact_classes": len(ce),
        "exact_multi": sum(1 for v in ce.values() if len(v) > 1),
        "exact_max": max(len(v) for v in ce.values()),
        "leak_groups": len(cl),
        "leak_multi": sum(1 for v in cl.values() if len(v) > 1),
        "leak_max": max(len(v) for v in cl.values()),
        "largest_exact": [v[:10] for v in biggest],
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
