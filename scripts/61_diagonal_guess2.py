#!/usr/bin/env python3
"""Search for a(n) = [x^n] (1 + p1 x + p2 x^2)^n with small integer p1,p2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "diagonal_guess2.json"


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


def poly_pow_coeff(p1, p2, n, target):
    """coefficient of x^target in (1 + p1 x + p2 x^2)^n"""
    poly = [1]
    for _ in range(n):
        new = [0] * (len(poly) + 2)
        for i, c in enumerate(poly):
            new[i] += c
            new[i + 1] += c * p1
            new[i + 2] += c * p2
        poly = new
    return poly[target] if target < len(poly) else 0


def main() -> int:
    ver = json.load(open(ROOT / "reports" / "closed_loop_verified.json", encoding="utf-8"))
    z1 = [x["aid"] for x in ver if x["kind"] == "z1"]
    matches = []
    for aid in z1:
        v = bfile(aid)
        if not v or len(v) < 10:
            continue
        found = None
        for p1 in range(-4, 5):
            for p2 in range(-4, 5):
                if p1 == 0 and p2 == 0:
                    continue
                if all(poly_pow_coeff(p1, p2, n, n) == v[n] for n in range(0, 9)):
                    found = (p1, p2)
                    break
            if found:
                break
        if found:
            matches.append({"aid": aid, "p1": found[0], "p2": found[1]})
            print(f"{aid}: a(n) = [x^n](1 {found[0]:+d}x {found[1]:+d}x^2)^n", flush=True)
    print("matches:", len(matches))
    OUT.write_text(json.dumps(matches, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
