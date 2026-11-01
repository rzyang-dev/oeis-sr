#!/usr/bin/env python3
"""Controlled experiment: which transforms preserve 5-adic congruence depth?

Start from A000041 (partition numbers, depth 4 at p=5) and apply transforms,
then measure the depth of the result.

    python scripts/50_transform_depth.py
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(r"C:\Users\ginger\oeisdata")


def bfile(aid, limit=3100):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    v = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        q = line.split()
        if len(q) >= 2:
            try:
                v[int(q[0])] = int(q[1])
            except ValueError:
                pass
        if len(v) >= limit:
            break
    return v


def vp(x, p):
    if x == 0:
        return -1
    k = 0
    while x % p == 0:
        x //= p
        k += 1
    return k


def depth_scan(seq, p, maxdepth=4):
    """best depth over all residues r mod p, given seq as list indexed 0..N"""
    N = len(seq)
    best = (0, None)
    for r in range(p):
        idx = list(range(r, N, p))
        if len(idx) < 20:
            continue
        vals = [vp(seq[i], p) for i in idx]
        if min(vals) < 1:
            continue
        # DFS
        cur = {r: vals}
        d = 1
        frontier = [(1, r, [seq[i] for i in idx], [i for i in idx])]
        while frontier:
            k, res, vlist, ilist = frontier.pop()
            mod = p ** (k + 1)
            for t in range(p):
                sub = res + t * p ** k
                sv = [v for v, i in zip(vlist, ilist) if i % mod == sub]
                if len(sv) >= 5 and min(sv) >= k + 1:
                    d = max(d, k + 1)
                    frontier.append((k + 1, sub, sv, [i for i in ilist if i % mod == sub]))
        if d > best[0]:
            best = (d, r)
    return best


def main() -> int:
    d = bfile("A000041")
    N = 3000
    a = [d[i] for i in range(N)]
    transforms = {
        "original": a,
        "shift a(n+1)": [d[i + 1] for i in range(N)],
        "prefix sum": [sum(a[:i + 1]) for i in range(N)],
        "difference": [a[i + 1] - a[i] for i in range(N - 1)],
        "multiply by n": [a[i] * i for i in range(N)],
        "multiply by n+1": [a[i] * (i + 1) for i in range(N)],
        "square": [a[i] * a[i] for i in range(N)],
        "2^n * a(n)": [a[i] * 2 ** i for i in range(N)],
    }
    # binomial transform
    bt = []
    row = [1]
    bt.append(a[0])
    from math import comb
    for n in range(1, min(N, 400)):
        bt.append(sum(comb(n, k) * a[k] for k in range(n + 1)))
    transforms["binomial transform"] = bt

    print(f"{'transform':22} {'depth':>6} {'class':>8}")
    for name, seq in transforms.items():
        dep, r = depth_scan(seq, 5)
        print(f"{name:22} {dep:>6} {str(r):>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())