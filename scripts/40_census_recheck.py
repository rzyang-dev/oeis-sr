#!/usr/bin/env python3
"""Re-check census 'none' entries with longer windows and higher orders.

Sample sequences that the 80/80 census could not solve, then retry with
100-term fits: BM up to order 30, and P-recursive models up to (5,3).

    python scripts/40_census_recheck.py --shard k --of n
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import berlekamp_massey, precursive_guess, precursive_predict

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
T, K = 100, 100
PRE = [(3, 2), (4, 3), (5, 3)]


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


def bm_long(vals, k, maxorder=30):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0]
        if abs(s.numerator).bit_length() > 50000:
            return None
        out.append(s)
    return out[-k:]


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    per = int(argv[argv.index("--per") + 1]) if "--per" in argv else 100
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute("select aid from seq_exact where method=''")]
    random.seed(101)
    random.shuffle(aids)
    aids = aids[shard::of][:per]
    print("shard", shard, "targets", len(aids), flush=True)

    out = ROOT / "reports" / f"recheck_{shard:02d}.jsonl"
    stats = {"bm30": 0, "pre": 0, "none": 0, "skip": 0}
    t0 = time.perf_counter()
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            v = bfile(aid)
            if not v or len(v) < T + K:
                stats["skip"] += 1
                continue
            vals = [Fraction(x) for x in v[:T]]
            truth = [Fraction(x) for x in v[T:T + K]]
            method = ""
            p = bm_long(vals, K)
            if p is not None and p == truth:
                method = "bm30"
                stats["bm30"] += 1
            else:
                for r, d in PRE:
                    coef = precursive_guess(vals, r, d)
                    if coef is None:
                        continue
                    pred = precursive_predict(vals, coef, r, d, 50)
                    if pred is not None and pred == truth[:50]:
                        method = f"pre({r},{d})"
                        stats["pre"] += 1
                        break
                if not method:
                    stats["none"] += 1
            fh.write(json.dumps({"aid": aid, "method": method}) + "\n")
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{len(aids)} {stats}", flush=True)
    print("done", stats, round(time.perf_counter() - t0, 1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
