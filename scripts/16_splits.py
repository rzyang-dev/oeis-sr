#!/usr/bin/env python3
"""Group-wise, tier-stratified train/val/test split for the benchmark.

Groups are the leak_group ids from seq_class: two sequences that are exact
affine/prefix relatives must never end up in different splits.

    python scripts/16_splits.py
"""
from __future__ import annotations

import json
import random
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "splits.json"


def main() -> int:
    con = sqlite3.connect(str(DB))
    rows = con.execute("select aid, tier, leak_group from bench").fetchall()
    groups: dict[int, list[str]] = defaultdict(list)
    tier_of: dict[int, Counter] = defaultdict(Counter)
    for aid, tier, g in rows:
        groups[g].append(aid)
        tier_of[g][tier] += 1
    print("bench entries:", len(rows), " leak groups:", len(groups))

    order = list(groups)
    random.seed(7)
    random.shuffle(order)
    order.sort(key=lambda g: -len(groups[g]))     # big groups first

    target = {"train": 0.70, "val": 0.15, "test": 0.15}
    counts = {k: 0 for k in target}
    split_of: dict[str, str] = {}
    n_total = len(rows)
    for g in order:
        k = max(target, key=lambda s: target[s] * n_total - counts[s])
        for aid in groups[g]:
            split_of[aid] = k
        counts[k] += len(groups[g])

    con.executemany("UPDATE bench SET split=? WHERE aid=?",
                    [(s, a) for a, s in split_of.items()])
    con.commit()

    print("split sizes:", counts)
    print("group count per split:", Counter(split_of.values()) and
          Counter(s for s in split_of.values()))
    # tier distribution per split
    dist = defaultdict(Counter)
    for aid, tier, g in rows:
        dist[split_of[aid]][tier] += 1
    for s in ("train", "val", "test"):
        print(f"  {s:5} {dict(dist[s])}")

    # sanity: no leak group spans splits
    span = defaultdict(set)
    for aid, tier, g in rows:
        span[g].add(split_of[aid])
    bad = [g for g, s in span.items() if len(s) > 1]
    print("groups spanning splits:", len(bad))

    OUT.write_text(json.dumps({
        "sizes": counts,
        "groups": len(groups),
        "tier_dist": {s: dict(dist[s]) for s in dist},
        "groups_spanning": len(bad),
    }, indent=1), encoding="utf-8")
    print("wrote", OUT)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
