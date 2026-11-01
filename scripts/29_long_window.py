#!/usr/bin/env python3
"""Does long b-file data change what is solvable?

Train on the first T terms, predict the next T, require exact equality.
Methods: finite differences (poly) and Berlekamp-Massey (linear recurrence),
with a hard cap on intermediate size so factorial-like sequences do not explode.

    python scripts/29_long_window.py [--limit 150] [--train 200]
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import poly_predict, berlekamp_massey

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "long_window.json"
MAXBITS = 20000


def bfile(aid, limit=5000):
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


def bm_capped(vals, k, maxorder=20):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0]
        if abs(s.numerator).bit_length() > MAXBITS:
            return None
        out.append(s)
    return out[-k:]


def main(argv: list[str]) -> int:
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 150
    T = int(argv[argv.index("--train") + 1]) if "--train" in argv else 200
    K = T
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select h.aid, s.method from hard_bench h
                          join hard_solved s on s.aid=h.aid where h.hard=1""").fetchall()
    random.seed(41)
    random.shuffle(rows)
    rows = rows[:limit * 3]
    print(f"train={T} test={K} candidates={len(rows)}", flush=True)

    res = []
    for i, (aid, old) in enumerate(rows):
        if len(res) >= limit:
            break
        d = bfile(aid)
        if not d:
            continue
        run = longest_run(sorted(d))
        if len(run) < T + K:
            continue
        vals = [d[n] for n in run[:T]]
        truth = [d[n] for n in run[T:T + K]]
        if max(abs(v) for v in vals) > 10**200:
            continue
        got = None
        p = poly_predict(vals, K, maxdeg=12)
        if p == truth:
            got = "poly"
        else:
            p = bm_capped(vals, K)
            if p is not None and p == [Fraction(x) for x in truth]:
                got = "bm20"
        res.append({"aid": aid, "old": old or "", "new": got or ""})
        if (i + 1) % 10 == 0:
            print(f"  {i+1} processed, solved {sum(1 for r in res if r['new'])}", flush=True)

    solved_new = sum(1 for r in res if r["new"])
    solved_old = sum(1 for r in res if r["old"])
    gained = sum(1 for r in res if r["new"] and not r["old"])
    lost = sum(1 for r in res if r["old"] and not r["new"])
    print(f"\nevaluated {len(res)}")
    print(f"  solved with {T}-term window: {solved_new} ({100*solved_new/max(1,len(res)):.1f}%)")
    print(f"  solved with 25-term window:  {solved_old} ({100*solved_old/max(1,len(res)):.1f}%)")
    print(f"  gained: {gained}   lost: {lost}")
    OUT.write_text(json.dumps({"train": T, "evaluated": len(res),
                               "new": solved_new, "old": solved_old,
                               "gained": gained, "lost": lost,
                               "detail": res[:200]}, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
