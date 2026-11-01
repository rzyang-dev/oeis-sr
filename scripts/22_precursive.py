#!/usr/bin/env python3
"""P-recursive (holonomic) guesser: a(n) = sum_i P_i(n) a(n-i) with polynomial P_i.

This is the natural next baseline for factorial/binomial sequences, which are
P-recursive but not C-finite.  A recurrence is guessed from the first 25 terms
by exact rational linear algebra, then validated on the next 30 b-file terms.

    python scripts/22_precursive.py [--limit N]
"""
from __future__ import annotations

import json
import random
import sqlite3
import sys
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "precursive.json"
T, K = 25, 30


def null_vector(rows: list[list[Fraction]], ncols: int):
    m = [row[:] for row in rows]
    pivot_cols: list[int] = []
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(m)):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        pv = m[r][c]
        m[r] = [x / pv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r])]
        pivot_cols.append(c)
        r += 1
        if r == len(m):
            break
    free = [c for c in range(ncols) if c not in pivot_cols]
    if not free:
        return None
    fc = free[-1]
    sol = [Fraction(0)] * ncols
    sol[fc] = Fraction(1)
    for i, c in enumerate(pivot_cols):
        sol[c] = -m[i][fc]
    return sol


def guess(vals: list[int], r: int, d: int):
    """Return the coefficient list of a recurrence of order r and degree d."""
    ncols = (r + 1) * (d + 1)
    nrows = len(vals) - r
    if nrows < ncols + 3:          # demand a margin against overfitting
        return None
    rows = []
    for n in range(r, len(vals)):
        row = []
        for i in range(r + 1):
            a = Fraction(vals[n - i])
            for j in range(d + 1):
                row.append(a * (n ** j))
        rows.append(row)
    return null_vector(rows, ncols)


def predict(vals: list[int], coef, r: int, d: int, k: int):
    out = list(vals)
    for n in range(len(vals), len(vals) + k):
        s = Fraction(0)
        p0 = Fraction(0)
        for i in range(r + 1):
            p = sum(coef[i * (d + 1) + j] * (n ** j) for j in range(d + 1))
            if i == 0:
                p0 = p
            else:
                s += p * out[n - i]
        if p0 == 0:
            return None
        v = -s / p0
        if v.denominator != 1:
            out.append(v)
        else:
            out.append(v.numerator)
    return out[-k:]


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


def main(argv: list[str]) -> int:
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute("select aid from hard_bench where hard=1")]
    if limit:
        random.seed(3)
        aids = random.sample(aids, min(limit, len(aids)))
    if of > 1:
        aids = aids[shard::of]
        out_path = ROOT / "reports" / f"precursive_{shard:02d}.json"
    else:
        out_path = OUT
    print("candidates:", len(aids))

    solved = skipped = 0
    by_model = {}
    examples = []
    for aid in aids:
        d = bfile(aid)
        if not d:
            skipped += 1
            continue
        ns = sorted(d)
        run, prev, longest = [], None, []
        for n in ns:
            if prev is not None and n != prev + 1:
                if len(run) > len(longest):
                    longest = run
                run = []
            run.append(n)
            prev = n
        if len(run) > len(longest):
            longest = run
        if len(longest) < T + K:
            skipped += 1
            continue
        vals = [d[n] for n in longest[:T]]
        truth = [d[n] for n in longest[T:T+K]]
        got = None
        for r, deg in ((1, 1), (1, 2), (2, 1), (1, 3), (2, 2), (3, 1),
                       (1, 4), (2, 3), (3, 2), (4, 1)):
            coef = guess(vals, r, deg)
            if coef is None:
                continue
            pred = predict(vals, coef, r, deg, K)
            if pred is not None and pred == truth:
                got = (r, deg)
                break
        if got:
            solved += 1
            by_model[got] = by_model.get(got, 0) + 1
            if len(examples) < 12:
                examples.append({"aid": aid, "order": got[0], "degree": got[1]})

    print(f"evaluated: {len(aids) - skipped}   solved: {solved} "
          f"({100*solved/max(1,len(aids)-skipped):.1f}%)   skipped: {skipped}")
    print("by model:", by_model)
    for e in examples:
        print("  ", e)
    out_path.write_text(json.dumps({"candidates": len(aids), "solved": solved,
                               "by_model": {f"{k[0]},{k[1]}": v for k, v in by_model.items()},
                               "examples": examples}, indent=1), encoding="utf-8")
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))