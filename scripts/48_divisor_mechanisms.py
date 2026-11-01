#!/usr/bin/env python3
"""Broader divisor mechanisms: is a(n) always divisible by (n+c)/d ?

Covers odd-part factors (d = 2^k) that a linear-factor test misses.
If (n+c)/d hits 0 mod p exactly on the congruence class, the pattern is trivial.

    python scripts/48_divisor_mechanisms.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "divisor_mechanisms.json"


def bfile(aid, limit=600):
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


def main() -> int:
    cands = []
    for line in open(ROOT / "reports" / "congruence_candidates2.txt", encoding="utf-8"):
        aid, p, r, pts = line.split()
        cands.append((aid, int(p), int(r)))
    print("candidates:", len(cands))

    cache = {}
    explained = []
    for aid, p, r in cands:
        if aid not in cache:
            cache[aid] = bfile(aid)
        pairs = cache[aid]
        if not pairs:
            continue
        found = None
        for c in range(-8, 9):
            for d in (1, 2, 3, 4, 5, 6, 8, 9, 10, 12):
                # cheap residue test: (n+c)/d == 0 mod p exactly on n = r mod p
                hit = all(((n + c) % (d * p) == 0) == (n % p == r) for n in range(r, r + 3 * p, 1))
                if not hit:
                    continue
                ok = True
                cnt = 0
                for n, v in pairs:
                    num = n + c
                    if num == 0 or num % d != 0:
                        continue
                    x = num // d
                    if x == 0:
                        continue
                    cnt += 1
                    if v % x != 0:
                        ok = False
                        break
                if ok and cnt >= 20:
                    found = f"(n{c:+d})/{d}"
                    break
            if found:
                break
        if found:
            explained.append((aid, p, r, found))

    print("explained by divisor mechanism:", len(explained), "/", len(cands))
    print("most common:", Counter(f for _, _, _, f in explained).most_common(12))
    OUT.write_text(json.dumps(explained, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
