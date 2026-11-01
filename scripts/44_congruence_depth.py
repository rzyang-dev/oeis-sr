#!/usr/bin/env python3
"""Depth of p-adic congruences, with full branching (DFS).

For a class n = r (mod p) with a(n) = 0 (mod p), explore every sub-class at
mod p^2, p^3, ... and report the deepest level where the minimum p-adic
valuation reaches the level.

Validated on A000041: level 1 -> 4, level 2 -> 24, level 3 -> 99, level 4 -> 599.

    python scripts/44_congruence_depth.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "congruence_depth.json"
MAXDEPTH = 4
MINPTS = 5


def bfile(aid, limit=6000):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    v = []
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
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


def vp(x, p):
    if x == 0:
        return -1   # zeros must not inflate the depth
    k = 0
    while x % p == 0:
        x //= p
        k += 1
        if k > 20:
            break
    return k


def deepest(pairs, p, r):
    """DFS over sub-classes; returns (depth, residue at deepest level)."""
    vals = {n: vp(x, p) for n, x in pairs if n % p == r}
    if len(vals) < MINPTS or min(vals.values()) < 1:
        return 0, r
    best = (1, r)
    frontier = [(1, r)]
    while frontier:
        k, res = frontier.pop()
        mod = p ** (k + 1)
        for t in range(p):
            sub = res + t * p ** k
            sub_vals = {n: v for n, v in vals.items() if n % mod == sub}
            if len(sub_vals) >= MINPTS and min(sub_vals.values()) >= k + 1:
                if k + 1 > best[0]:
                    best = (k + 1, sub)
                frontier.append((k + 1, sub))
    return best


def main() -> int:
    cands = []
    for line in open(ROOT / "reports" / "congruence_candidates2.txt", encoding="utf-8"):
        aid, p, r, pts = line.split()
        cands.append((aid, int(p), int(r)))
    cands += [("A000041", 5, 4), ("A000041", 7, 5), ("A000041", 11, 6)]
    print("candidates:", len(cands))

    cache = {}
    out = []
    for aid, p, r in cands:
        if aid not in cache:
            cache[aid] = bfile(aid)
        pairs = cache[aid]
        if not pairs:
            continue
        k, res = deepest(pairs, p, r)
        if k >= 2:
            out.append({"aid": aid, "p": p, "r": r, "depth": k, "deep_res": res})

    print("depth >= 2:", len(out), "seqs:", len({o['aid'] for o in out}))
    print("depth distribution:", Counter(o["depth"] for o in out))
    for o in out[:10]:
        print("  ", o)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())