#!/usr/bin/env python3
"""Exact-structure census over every sequence with a b-file.

For each sequence: take a consecutive run of >= 180 terms, fit on the first 80,
predict the next 80, require exact equality.

    poly    finite differences, degree <= 12
    cf      linear recurrence of order <= 20 (Berlekamp-Massey over Q)

A fast modular Berlekamp-Massey prefilter finds the order; only low-order
candidates are verified with exact rational arithmetic.

    python scripts/31_exact_census.py --shard k --of n
"""
from __future__ import annotations

import json
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
T, K = 80, 80
P = (1 << 61) - 1
MAXORDER = 20


def read_bfile(aid, limit=300):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    vals = []
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        vals.append(int(q[1]))
                    except ValueError:
                        pass
                if len(vals) >= limit:
                    break
    except OSError:
        return None
    return vals or None


def bm_order_mod(s):
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
    for n in range(len(s)):
        d = 0
        for i in range(min(L, n) + 1):
            d = (d + C[i] * s[n - i]) % P
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d * pow(b, P - 2, P) % P
        if len(C) < len(B) + m:
            C += [0] * (len(B) + m - len(C))
        for j, bj in enumerate(B):
            C[j + m] = (C[j + m] - coef * bj) % P
        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1
        if L > MAXORDER:
            return L
    return L


def bm_exact(vals, k, maxorder=MAXORDER):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None, L
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0]
        if abs(s.numerator).bit_length() > 5000:
            return None, L
        out.append(s)
    return out[-k:], L


def main(argv: list[str]) -> int:
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select distinct aid from attachment where name like 'b%.txt' "
        "and aid in (select aid from seq)")]
    aids.sort()
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "sequences:", len(aids), flush=True)

    out = ROOT / "reports" / f"exact_{shard:02d}.jsonl"
    stats = {"poly": 0, "cf": 0, "poly_mod": 0, "none": 0, "skip": 0}
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            v = read_bfile(aid)
            if not v or len(v) < T + K:
                stats["skip"] += 1
                continue
            v = v[:T + K]
            train = v[:T]
            truth = v[T:]
            rec = {"aid": aid, "method": "", "order": 0, "n_terms": len(v)}
            p = poly_predict(train, K, maxdeg=12)
            if p == truth:
                rec["method"] = "poly"
                stats["poly"] += 1
            else:
                s = [x % P for x in train]
                L = bm_order_mod(s)
                if L <= MAXORDER:
                    pred, L2 = bm_exact(train, K)
                    if pred is not None and [int(x) if x.denominator == 1 else x for x in pred] == truth:
                        rec["method"] = "cf"
                        rec["order"] = L2
                        stats["cf"] += 1
                    else:
                        stats["none"] += 1
                else:
                    stats["none"] += 1
            fh.write(json.dumps(rec) + "\n")
            if (i + 1) % 3000 == 0:
                print(f"  {i+1}/{len(aids)} {stats}", flush=True)
    print("done", stats, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
