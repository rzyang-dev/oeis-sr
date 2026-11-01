#!/usr/bin/env python3
"""Cross-domain duplicate / near-duplicate search.

Group sequences by their first 8 terms (from their own start), then verify
equality on more terms and report pairs whose domain clusters differ.

    python scripts/73_cross_domain.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "cross_domain.json"


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    cluster = dict(con.execute("select aid, cluster from domain"))
    groups = defaultdict(list)
    terms_map = {}
    for aid, off, terms in con.execute("select aid, offset1, terms from seq"):
        if not terms:
            continue
        try:
            vals = [int(x) for x in terms.split(",")[:40]]
        except ValueError:
            continue
        if len(vals) < 8:
            continue
        terms_map[aid] = vals
        groups[tuple(vals[:8])].append(aid)
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    print("groups with >1 sequence:", len(multi))

    pairs = []
    for key, aids in multi.items():
        aids = aids[:12]
        for i in range(len(aids)):
            for j in range(i + 1, len(aids)):
                a, b = aids[i], aids[j]
                ta, tb = terms_map[a], terms_map[b]
                n = min(len(ta), len(tb))
                if n < 20:
                    continue
                if ta[:n] != tb[:n]:
                    continue
                ca, cb = cluster.get(a, -1), cluster.get(b, -1)
                if ca == cb:
                    continue
                pairs.append({"a": a, "b": b, "ca": ca, "cb": cb, "n": n})
    print("cross-domain identical (>=20 terms):", len(pairs))
    names = dict(con.execute("select aid, name from seq"))
    for p in pairs[:20]:
        print(f"  {p['a']}[{p['ca']}] = {p['b']}[{p['cb']}]  n={p['n']}")
        print(f"     {names.get(p['a'],'')[:70]}")
        print(f"     {names.get(p['b'],'')[:70]}")
    OUT.write_text(json.dumps(pairs, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
