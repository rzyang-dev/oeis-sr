#!/usr/bin/env python3
"""Extended P-recursive sweep with per-target persistence.

Records, for every hard target, which exact method (if any) reproduces the next
30 b-file terms: poly, bm, pre(base), pre(extended).

    python scripts/26_precursive_high.py --shard 0 --of 8
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import poly_predict, bm_predict, precursive_guess, precursive_predict

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
T, K = 25, 30

BASE = ((1, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3), (2, 3), (3, 2), (4, 1), (1, 4))
EXT = ((5, 1), (6, 1), (3, 3), (4, 2), (2, 4), (1, 5))


def bfile(aid, limit=4000):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    d = {}
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        d[int(q[0])] = int(q[1])
                    except ValueError:
                        pass
                if len(d) >= limit:
                    break
    except OSError:
        return None
    return d or None


def longest_run(ns):
    run, prev, best = [], None, []
    for n in ns:
        if prev is not None and n != prev + 1:
            if len(run) > len(best):
                best = run
            run = []
        run.append(n)
        prev = n
    return run if len(run) > len(best) else best


def solve_ext(vals, truth):
    p = poly_predict(vals, K)
    if p == truth:
        return "poly"
    p = bm_predict(vals, K)
    if p == truth:
        return "bm"
    for group, models in (("pre", BASE), ("pre_high", EXT)):
        for r, d in models:
            coef = precursive_guess(vals, r, d)
            if coef is None:
                continue
            pred = precursive_predict(vals, coef, r, d, K)
            if pred == truth:
                return f"{group}({r},{d})"
    return None


def main(argv: list[str]) -> int:
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute("select aid from hard_bench where hard=1")]
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "targets:", len(aids), flush=True)

    rows = []
    counts = {}
    for i, aid in enumerate(aids):
        d = bfile(aid)
        if not d:
            continue
        run = longest_run(sorted(d))
        if len(run) < T + K:
            continue
        vals = [d[n] for n in run[:T]]
        truth = [d[n] for n in run[T:T + K]]
        method = solve_ext(vals, truth)
        rows.append({"aid": aid, "method": method})
        counts[method] = counts.get(method, 0) + 1
        if i % 500 == 0:
            print(f"  {i}/{len(aids)}", flush=True)

    out = ROOT / "reports" / f"solved_{shard:02d}.json"
    out.write_text(json.dumps(rows), encoding="utf-8")
    print("done, counts:", counts, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
