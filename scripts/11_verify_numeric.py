#!/usr/bin/env python3
"""Spot-check mined numeric relations against b-files (longer than %S terms).

    python scripts/11_verify_numeric.py [--per-kind 120]
"""
from __future__ import annotations

import random
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"


def bfile(aid: str):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    d = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        q = line.split()
        if len(q) >= 2:
            try:
                d[int(q[0])] = int(q[1])
            except ValueError:
                pass
    return d or None


def main(argv: list[str]) -> int:
    per_kind = int(argv[argv.index("--per-kind") + 1]) if "--per-kind" in argv else 120
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    nterms = dict(con.execute("select aid, n_terms from seq"))
    pairs = con.execute("select aid, dst, kind from numeric_relation").fetchall()
    doc = set()
    for q in ("select aid, dst from definition", "select aid, dst from identity",
              "select src, dst from xref"):
        for a, b in con.execute(q):
            doc.add((a, b) if a < b else (b, a))
    undoc = [(a, b, k) for a, b, k in pairs if ((a, b) if a < b else (b, a)) not in doc]

    random.seed(9)
    res = Counter()
    for kind in ("equal", "affine", "prefix"):
        pool = [(a, b) for a, b, k in undoc
                if k == kind and nterms.get(a, 0) >= 25 and nterms.get(b, 0) >= 25]
        for a, b in random.sample(pool, min(per_kind, len(pool))):
            da, db = bfile(a), bfile(b)
            if not da or not db:
                res[(kind, "no_bfile")] += 1
                continue
            common = sorted(set(da) & set(db))
            best, cur = [], []
            for n in common:
                if cur and n != cur[-1] + 1:
                    if len(cur) > len(best):
                        best = cur
                    cur = []
                cur.append(n)
            if len(cur) > len(best):
                best = cur
            if len(best) < 50:
                res[(kind, "too_short")] += 1
                continue
            x = [da[n] for n in best]
            y = [db[n] for n in best]
            if kind == "equal":
                ok = x == y
            elif kind == "prefix":
                ok = all(x[i] - x[i - 1] == y[i] for i in range(1, len(x)))
            else:
                i = next((k for k in range(len(y) - 1) if y[k] != y[k + 1]), None)
                if i is None:
                    ok = False
                else:
                    an, ad = x[i] - x[i + 1], y[i] - y[i + 1]
                    bn = x[i] * ad - an * y[i]
                    ok = all(x[k] * ad == an * y[k] + bn for k in range(len(x)))
            res[(kind, "ok" if ok else "FAIL")] += 1

    print("b-file verification (>=50 consecutive terms, both with >=25 %S terms):")
    for kind in ("equal", "affine", "prefix"):
        ok, bad = res[(kind, "ok")], res[(kind, "FAIL")]
        if ok + bad:
            print(f"  {kind:7} pass {100*ok/(ok+bad):5.1f}%  ({ok}/{ok+bad})"
                  f"   no b-file {res[(kind,'no_bfile')]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
