#!/usr/bin/env python3
"""Second pass with long windows on high-confidence-but-unsolved targets.

Fit on 60 b-file terms, validate on the next 30, with higher-order models.

    python scripts/39_long_pass.py --shard k --of n
"""
from __future__ import annotations

import json
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
N, M = 60, 30
MODELS = [(2, 1), (2, 2), (3, 2), (4, 3), (5, 2), (5, 3), (5, 4), (3, 5), (6, 2)]


def bfile(aid, limit=200):
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


def bm_long(vals, k, maxorder=20):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0]
        if abs(s.numerator).bit_length() > 20000:
            return None
        out.append(s)
    return out[-k:]


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    pmin = float(argv[argv.index("--pmin") + 1]) if "--pmin" in argv else 0.5
    pmax = float(argv[argv.index("--pmax") + 1]) if "--pmax" in argv else 1.01
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select r.aid from routed_run r join hard_solved h on h.aid=r.aid
        where r.p>=? and r.p<? and h.method=''""", (pmin, pmax)).fetchall()
    aids = sorted(r[0] for r in rows)
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "targets", len(aids), flush=True)

    tag = f"{pmin:.2f}_{pmax:.2f}".replace(".", "")
    out = ROOT / "reports" / f"longpass_{tag}_{shard:02d}.jsonl"
    solved = 0
    t0 = time.perf_counter()
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            v = bfile(aid)
            if not v or len(v) < N + M:
                continue
            vals = [Fraction(x) for x in v[:N]]
            truth = [Fraction(x) for x in v[N:N + M]]
            method = ""
            p = bm_long(vals, M)
            if p is not None and p == truth:
                method = "bm60"
            else:
                for r, d in MODELS:
                    coef = precursive_guess(vals, r, d)
                    if coef is None:
                        continue
                    pred = precursive_predict(vals, coef, r, d, M)
                    if pred is not None and pred == truth:
                        method = f"long({r},{d})"
                        break
            if method:
                solved += 1
            fh.write(json.dumps({"aid": aid, "method": method}) + "\n")
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(aids)} solved {solved}", flush=True)
    print("done", {"targets": len(aids), "solved": solved,
                   "seconds": round(time.perf_counter() - t0, 1)}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))