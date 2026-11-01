#!/usr/bin/env python3
"""Find sequences that are exactly b op c for two core atoms (op in +,-,*).

    python scripts/13_pointwise_decompositions.py

Writes reports/pointwise_hits.json and the table pointwise_decomposition.
Only combinations of the 525 most-used atoms are tried, so this is a lower bound.
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
OUT = ROOT / "reports" / "pointwise_hits.json"
L = 14


def main() -> int:
    con = sqlite3.connect(str(DB))
    rows = con.execute(
        "select aid, offset1, terms from seq where n_terms>=? and offset1 in (0,1)",
        (L,)).fetchall()
    full, off = {}, {}
    for aid, o, t in rows:
        v = [int(x) for x in t.split(",")]
        if len(v) < L:
            continue
        full[aid] = v
        off[aid] = o
    print("sequences:", len(full))

    lookup = defaultdict(list)
    for aid, v in full.items():
        lookup[(off[aid], tuple(v[:L]))].append(aid)

    atoms = [r[0] for r in con.execute(
        "select dst, count(*) n from definition group by dst order by n desc limit 525")]
    atoms = [a for a in atoms if a in full]
    by_off = {0: [a for a in atoms if off[a] == 0], 1: [a for a in atoms if off[a] == 1]}

    hits = []
    for o, group in by_off.items():
        for i in range(len(group)):
            a = group[i]
            va = full[a][:L]
            for j in range(i + 1, len(group)):
                b = group[j]
                vb = full[b][:L]
                for op, w in (("sum", [x + y for x, y in zip(va, vb)]),
                              ("prod", [x * y for x, y in zip(va, vb)]),
                              ("diff", [x - y for x, y in zip(va, vb)])):
                    for tgt in lookup.get((o, tuple(w)), ()):
                        if tgt not in (a, b):
                            hits.append((op, tgt, a, b))

    def verify(a, b, c, op):
        lo = max(off[a], off[b], off[c])
        hi = min(off[a] + len(full[a]), off[b] + len(full[b]), off[c] + len(full[c]))
        if hi - lo < 10:
            return 0
        ok = 0
        for n in range(lo, hi):
            x, y, z = full[a][n-off[a]], full[b][n-off[b]], full[c][n-off[c]]
            if x != {"sum": y + z, "prod": y * z, "diff": y - z}[op]:
                break
            ok += 1
        return ok

    verified = []
    for op, t, a, b in hits:
        k = verify(t, a, b, op)
        if k >= 10:
            verified.append((k, op, t, a, b))
    verified.sort(reverse=True)

    con.execute("DROP TABLE IF EXISTS pointwise_decomposition")
    con.execute("CREATE TABLE pointwise_decomposition "
                "(target TEXT, b TEXT, c TEXT, op TEXT, terms INTEGER)")
    con.executemany("INSERT INTO pointwise_decomposition VALUES (?,?,?,?,?)",
                    [(t, a, b, op, k) for k, op, t, a, b in verified])
    con.execute("CREATE INDEX idx_pwd_target ON pointwise_decomposition(target)")
    con.commit()

    JSON = [{"terms": k, "op": op, "target": t, "b": a, "c": b} for k, op, t, a, b in verified]
    OUT.write_text(json.dumps(JSON, indent=1), encoding="utf-8")
    print(f"verified decompositions: {len(verified)}")
    print("by op:", {op: sum(1 for v in verified if v[1] == op) for op in ("sum", "prod", "diff")})
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
