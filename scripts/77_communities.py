#!/usr/bin/env python3
"""Community detection on the OEIS cross-reference + definition graph.

    python scripts/77_communities.py
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "communities.json"


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    adj = defaultdict(set)
    n_edges = 0
    for a, b in con.execute("select src, dst from xref"):
        adj[a].add(b); adj[b].add(a); n_edges += 1
    for a, b in con.execute("select aid, dst from definition"):
        adj[a].add(b); adj[b].add(a); n_edges += 1
    print("nodes:", len(adj), "edges:", n_edges)

    labels = {u: u for u in adj}
    rng = random.Random(0)
    nodes = list(adj)
    for it in range(6):
        rng.shuffle(nodes)
        changed = 0
        for u in nodes:
            if not adj[u]:
                continue
            c = Counter(labels[v] for v in adj[u])
            best = c.most_common(1)[0][0]
            if labels[u] != best:
                labels[u] = best
                changed += 1
        print("iter", it, "changed", changed, flush=True)
        if changed < len(nodes) * 0.001:
            break
    sizes = Counter(labels.values())
    print("communities:", len(sizes), "largest:", sizes.most_common(5))
    con2 = sqlite3.connect(str(ROOT / "oeis.db"))
    con2.execute("DROP TABLE IF EXISTS community")
    con2.execute("CREATE TABLE community (aid TEXT PRIMARY KEY, comm TEXT)")
    con2.executemany("INSERT INTO community VALUES (?,?)", list(labels.items()))
    con2.commit()
    json.dump({"sizes": {k: v for k, v in sizes.most_common(50)}},
              open(OUT, "w"), indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
