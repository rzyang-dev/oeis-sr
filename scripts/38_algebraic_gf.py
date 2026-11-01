#!/usr/bin/env python3
"""Guess algebraic generating functions: does A(x) satisfy a polynomial equation?

    P_0(x) + P_1(x)A + ... + P_d(x)A^d = 0,   deg P_j <= m

Fit on the first N terms, then check the equation on the next M held-out terms.
If the residual vanishes there, the sequence is algebraic of that shape.

    python scripts/38_algebraic_gf.py
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import null_vector

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "algebraic_gf.json"
N, M = 50, 40
SHAPES = [(2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3), (2, 4), (3, 4)]


def bfile(aid, limit=400):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    v = []
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        v.append(int(q[1]))
                    except ValueError:
                        pass
                if len(v) >= limit:
                    break
    except OSError:
        return None
    return v or None


def powers(a, d, n):
    P = [[Fraction(0)] * n for _ in range(d + 1)]
    P[0][0] = Fraction(1)
    for j in range(1, d + 1):
        prev = P[j-1]
        cur = P[j]
        for k in range(n):
            s = Fraction(0)
            for t in range(k + 1):
                if prev[t] and a[k-t]:
                    s += prev[t] * a[k-t]
            cur[k] = s
    return P


def residual(coef, a, d, m, n):
    """max |coefficient of x^k| for k < n, given the equation coefficients."""
    P = powers(a, d, n)
    worst = Fraction(0)
    for k in range(n):
        s = Fraction(0)
        for j in range(d + 1):
            for i in range(m + 1):
                c = coef[j * (m + 1) + i]
                if c and k - i >= 0:
                    s += c * P[j][k - i]
        if abs(s) > worst:
            worst = abs(s)
    return worst


def guess(a, d, m, n):
    P = powers(a[:n], d, n)
    rows = []
    for k in range(n):
        row = []
        for j in range(d + 1):
            for i in range(m + 1):
                row.append(P[j][k - i] if k - i >= 0 else Fraction(0))
        rows.append(row)
    return null_vector(rows, (d + 1) * (m + 1))


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select r.aid from routed_run r join hard_solved h on h.aid=r.aid
        where r.p>=0.7 and h.method=''""").fetchall()
    aids = [r[0] for r in rows]
    print("high-confidence failures:", len(aids))

    found = []
    for aid in aids:
        v = bfile(aid)
        if not v or len(v) < N + M:
            continue
        a = [Fraction(x) for x in v[:N + M]]
        hit = None
        for d, m in SHAPES:
            coef = guess(a, d, m, N)
            if coef is None:
                continue
            if all(c == 0 for c in coef):
                continue
            r = residual(coef, a, d, m, N + M)
            if r == 0:
                hit = (d, m)
                break
        if hit:
            found.append({"aid": aid, "d": hit[0], "m": hit[1]})

    print(f"algebraic of degree<=3 found: {len(found)} / {len(aids)}")
    from collections import Counter
    print("shapes:", Counter((f["d"], f["m"]) for f in found))
    for f in found[:10]:
        print("  ", f)
    OUT.write_text(json.dumps(found, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
