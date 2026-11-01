#!/usr/bin/env python3
"""Pointwise-decomposition cascade: a = b op c with both operands solvable.

    python scripts/24_pointwise_cascade.py
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import solve, solve_validated

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "pointwise_cascade.json"
T, K = 20, 30
_c = {}
def bfile(aid, limit=4000):
    if aid in _c: return _c[aid]
    p = DATA / "files" / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    q = line.split()
                    if len(q) >= 2:
                        try: d[int(q[0])] = int(q[1])
                        except ValueError: pass
                    if len(d) >= limit: break
        except OSError: d = None
    _c[aid] = d
    return d

def longest_run(ns):
    run, prev, best = [], None, []
    for n in ns:
        if prev is not None and n != prev + 1:
            if len(run) > len(best): best = run
            run = []
        run.append(n); prev = n
    return run if len(run) > len(best) else best

def solve_upto(aid, cutoff, need_to):
    d = bfile(aid)
    if not d: return None
    known = sorted(n for n in d if n <= cutoff)
    if len(known) < 20: return None
    last = known[-25:]
    vals = [d[n] for n in last]
    need = need_to - last[-1]
    out = {n: d[n] for n in d if n <= cutoff}
    if need <= 0: return out
    pred, how = solve_validated(vals, need)
    if pred is None: return None
    for i, v in enumerate(pred):
        out[last[-1]+1+i] = v.numerator if isinstance(v, Fraction) and v.denominator == 1 else v
    return out

def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select p.target, p.b, p.c, p.op from pointwise_decomposition p
        join hard_bench h on h.aid=p.target where h.hard=1""").fetchall()
    print("hard targets with pointwise decomposition:", len(rows))
    solved = 0
    tried = 0
    for t, b, c, op in rows:
        d = bfile(t)
        if not d: continue
        run = longest_run(sorted(d))
        if len(run) < T + K: continue
        train = [d[n] for n in run[:T]]
        truth = [d[n] for n in run[T:T+K]]
        cutoff, need_to = run[T-1], run[T+K-1]
        pb = solve_upto(b, cutoff, need_to)
        pc = solve_upto(c, cutoff, need_to)
        if pb is None or pc is None: continue
        tried += 1
        try:
            if op == "sum": pred = [pb[n] + pc[n] for n in range(cutoff+1, cutoff+K+1)]
            elif op == "prod": pred = [pb[n] * pc[n] for n in range(cutoff+1, cutoff+K+1)]
            else: pred = [pb[n] - pc[n] for n in range(cutoff+1, cutoff+K+1)]
        except KeyError:
            continue
        if pred == truth:
            solved += 1
    print(f"both operands solvable: {tried}   cascade solved: {solved}")
    json.dump({"hard_pointwise": len(rows), "both_solvable": tried, "solved": solved},
              open(OUT, "w"), indent=1)
    print("wrote", OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
