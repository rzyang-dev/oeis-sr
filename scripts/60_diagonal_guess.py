#!/usr/bin/env python3
"""Search for diagonal identities: a(n) = [y^(c n)] (1+y)^(a n) (2+y)^(b n).

    python scripts/60_diagonal_guess.py
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(r"C:\Users\ginger\oeisdata")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "diagonal_guess.json"


def bfile(aid, limit=200):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    v = []
    try:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
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


def coeff_diag(n, c, al, be):
    """[y^(c n)] (1+y)^(al n) (2+y)^(be n)"""
    target = c * n
    total = 0
    for j in range(0, min(al * n, target) + 1):
        k = target - j
        if 0 <= k <= be * n:
            total += comb(al * n, j) * comb(be * n, k) * (2 ** (be * n - k))
    return total


def main() -> int:
    ver = json.load(open(ROOT / "reports" / "closed_loop_verified.json", encoding="utf-8"))
    z1 = [x["aid"] for x in ver if x["kind"] == "z1"]
    matches = []
    checked = 0
    for aid in z1:
        v = bfile(aid)
        if not v or len(v) < 12:
            continue
        checked += 1
        found = None
        for c in range(1, 5):
            for al in range(0, 5):
                for be in range(0, 4):
                    if al == 0 and be == 0:
                        continue
                    if all(coeff_diag(n, c, al, be) == v[n] for n in range(0, 8)):
                        found = (c, al, be)
                        break
                if found:
                    break
            if found:
                break
        if found:
            c, al, be = found
            matches.append({"aid": aid, "c": c, "alpha": al, "beta": be})
            print(f"{aid}: a(n) = [y^{c}n](1+y)^{al}n(2+y)^{be}n", flush=True)
    print(f"checked {checked}, matches {len(matches)}")
    OUT.write_text(json.dumps(matches, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
