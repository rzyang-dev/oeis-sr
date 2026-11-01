#!/usr/bin/env python3
"""Explain congruences by linear factors: does (a*n+b) divide a(n)?

If a(n) is always divisible by (a*n+b), and (a*n+b) = 0 (mod p) exactly when
n = r (mod p), then the congruence is a trivial consequence of a linear factor.

    python scripts/47_factor_explain.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "factor_explain.json"
AMAX = 12
BMAX = 30


def bfile(aid, limit=800):
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
    unexplained = []
    for aid, p, r in cands:
        if aid not in cache:
            cache[aid] = bfile(aid)
        pairs = cache[aid]
        if not pairs:
            continue
        found = None
        for a in range(1, AMAX + 1):
            if a % p == 0:
                continue
            for t in range(-3, 4):
                b = -a * r + t * p
                if abs(b) > BMAX:
                    continue
                ok = True
                cnt = 0
                for n, v in pairs:
                    d = a * n + b
                    if d == 0:
                        continue
                    cnt += 1
                    if v % d != 0:
                        ok = False
                        break
                if ok and cnt >= 20:
                    found = f"{a}*n{b:+d}"
                    break
            if found:
                break
        if found:
            explained.append((aid, p, r, found))
        else:
            unexplained.append((aid, p, r))

    print(f"explained by a linear factor: {len(explained)}")
    print(f"not explained: {len(unexplained)}")
    print("most common factors:", Counter(f for _, _, _, f in explained).most_common(10))
    OUT.write_text(json.dumps({"explained": explained, "unexplained": unexplained}, indent=1),
                   encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
