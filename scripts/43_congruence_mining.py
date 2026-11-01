#!/usr/bin/env python3
"""Congruence mining with TRUE n-based residue classes (not positions).

    python scripts/43_congruence_mining.py --shard k --of n
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
PRIMES = [2, 3, 5, 7, 11]
MODULI = [2, 3, 4, 5, 7, 11]
MIN_POINTS = 40


def bfile(aid, limit=1200):
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
                        v.append((int(q[0]), int(q[1])))
                    except ValueError:
                        pass
                if len(v) >= limit:
                    break
    except OSError:
        return None
    return v or None


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select distinct aid from attachment where name like 'b%.txt' "
        "and aid in (select aid from seq)")]
    aids.sort()
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "sequences", len(aids), flush=True)

    out = ROOT / "reports" / f"cong2_{shard:02d}.jsonl"
    nseq = 0
    nhit = 0
    t0 = time.perf_counter()
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            pairs = bfile(aid)
            if not pairs or len(pairs) < 300:
                continue
            nseq += 1
            ns = np.array([n for n, _ in pairs], dtype=np.int64)
            vals = [v for _, v in pairs]
            L = len(vals)
            for p in PRIMES:
                a = [x % p for x in vals]
                if not any(a):
                    continue
                for m in MODULI:
                    if L // m < MIN_POINTS:
                        continue
                    res = ns % m
                    groups = [[] for _ in range(m)]
                    for j in range(L):
                        groups[res[j]].append(a[j])
                    for r in range(m):
                        if len(groups[r]) >= MIN_POINTS and not any(groups[r]):
                            fh.write(json.dumps({"aid": aid, "p": p, "m": m, "r": r,
                                                 "pts": len(groups[r])}) + "\n")
                            nhit += 1
            if (i + 1) % 5000 == 0:
                print(f"  {i+1}/{len(aids)} seqs {nseq} hits {nhit}", flush=True)
    print("done", {"sequences": nseq, "hits": nhit,
                   "seconds": round(time.perf_counter() - t0, 1)}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
