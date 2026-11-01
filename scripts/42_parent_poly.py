#!/usr/bin/env python3
"""Parent-polynomial model: a(n) = P(b(n)) for a documented parent b.

For each unsolved hard target with a definition edge a -> b, fit a low-degree
polynomial P exactly on the training terms and verify on held-out terms.

    python scripts/42_parent_poly.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "parent_poly.json"
T, K = 20, 30

_c = {}
def bfile(aid, limit=300):
    if aid in _c:
        return _c[aid]
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
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
            d = None
    _c[aid] = d
    return d


def solve_linear(A, bvec):
    """Exact Gaussian elimination for a square system; None if singular."""
    n = len(A)
    M = [list(row) + [bvec[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [x - f * y for x, y in zip(M[r], M[col])]
    return [M[i][n] for i in range(n)]


def fit_poly(xs, ys, deg):
    idx = []
    for i, x in enumerate(xs):
        if x not in [xs[j] for j in idx]:
            idx.append(i)
        if len(idx) == deg + 1:
            break
    if len(idx) < deg + 1:
        return None
    A = [[Fraction(xs[i]) ** k for k in range(deg + 1)] for i in idx]
    bvec = [Fraction(ys[i]) for i in idx]
    coef = solve_linear(A, bvec)
    if coef is None:
        return None
    return coef


def eval_poly(coef, x):
    s = Fraction(0)
    for c in reversed(coef):
        s = s * x + c
    return s


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    unsolved = {r[0] for r in con.execute("select aid from hard_solved where method=''")}
    edges = defaultdict(list)
    for a, b in con.execute("select aid, dst from definition"):
        if a in unsolved:
            edges[a].append(b)
    print("unsolved with parents:", len(edges))

    hits = []
    tried = 0
    for aid, parents in edges.items():
        da = bfile(aid)
        if not da:
            continue
        ns = sorted(da)
        run = []
        for n in ns:
            if run and n != run[-1] + 1:
                if len(run) >= T + K:
                    break
                run = []
            run.append(n)
        if len(run) < T + K:
            continue
        tried += 1
        for b in parents[:4]:
            db = bfile(b)
            if not db:
                continue
            common = [n for n in run[:T + K] if n in db]
            if len(common) < T + K:
                continue
            xs = [Fraction(db[n]) for n in common]
            ys = [Fraction(da[n]) for n in common]
            for deg in (1, 2, 3):
                coef = fit_poly(xs[:T], ys[:T], deg)
                if coef is None:
                    continue
                if all(eval_poly(coef, x) == y for x, y in zip(xs[T:], ys[T:])):
                    hits.append({"aid": aid, "parent": b, "deg": deg})
                    break
            else:
                continue
            break
    print(f"tried {tried}  parent-polynomial solved: {len(hits)}")
    from collections import Counter
    print("by degree:", Counter(h["deg"] for h in hits))
    for h in hits[:12]:
        print("  ", h)
    OUT.write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
