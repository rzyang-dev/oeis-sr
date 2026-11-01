#!/usr/bin/env python3
"""Survey the freshman's-dream congruence predictor over diagonal-power sequences.

For a(n) = [x^n] S(x)^n, let R_p be the exponent set of S modulo p.
Then a(pm+r) = 0 (mod p) whenever r is not a sum of exactly r elements of R_p.

Parse simple polynomial S from the formula text, predict, and check on b-files.

    python scripts/51_freshman_survey.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "freshman_survey.json"


def parse_poly(s):
    s = s.replace(" ", "")
    if re.search(r"[a-wyz]", s):
        return None
    coeffs = {}
    for t in re.findall(r"[+-]?[^+-]+", s):
        if not t:
            continue
        sign = -1 if t.startswith("-") else 1
        t = t.lstrip("+-")
        m = re.fullmatch(r"(?:(\d+)\*)?x(?:\^(\d+))?", t)
        if m:
            c = int(m.group(1)) if m.group(1) else 1
            e = int(m.group(2)) if m.group(2) else 1
        elif t.isdigit():
            c, e = int(t), 0
        else:
            return None
        coeffs[e] = coeffs.get(e, 0) + sign * c
    return coeffs or None


def sumsets(R, p, maxr):
    reach = [set() for _ in range(maxr + 1)]
    reach[0] = {0}
    S = {e % p for e in R}
    for r in range(1, maxr + 1):
        reach[r] = {(x + y) % p for x in reach[r - 1] for y in S}
    return reach


def bfile(aid, limit=1200):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    v = {}
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
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
    except OSError:
        return None
    return v or None


def main() -> int:
    con = sqlite3.connect(f"file:{ROOT.joinpath('oeis.db').as_posix()}?mode=ro", uri=True)
    rows = con.execute("select aid, text from stmt where field='F' and kind='def' and text like '%[x^n]%'").fetchall()
    pat = re.compile(r"\[x\^n\]\s*\(([^()]*)\)\^n", re.I)
    cases = []
    for aid, t in rows:
        t2 = re.sub(r"\s*-\s*_[^_]+_\s*\w+\s*\d{4}.*$", "", t.strip())
        t2 = re.sub(r"\s*\.\s*$", "", t2)
        m = pat.search(t2)
        if not m:
            continue
        rest = t2[m.end():].lstrip()
        if rest.startswith("*"):
            continue
        poly = parse_poly(m.group(1))
        if poly:
            cases.append((aid, poly, m.group(1)))
    print("parseable diagonal-power sequences:", len(cases))

    confirmed = refuted = 0
    results = []
    for aid, poly, src in cases:
        d = bfile(aid)
        if not d or len(d) < 200:
            continue
        for p in (2, 3, 5, 7, 11):
            R = [e for e, c in poly.items() if c % p != 0]
            if not R:
                continue
            reach = sumsets(R, p, p - 1)
            for r in range(p):
                if r in reach[r]:
                    continue          # not predicted to vanish
                cls = [x for n, x in d.items() if n % p == r]
                if len(cls) < 20:
                    continue
                ok = all(x % p == 0 for x in cls)
                if ok:
                    confirmed += 1
                else:
                    refuted += 1
                results.append({"aid": aid, "p": p, "r": r, "predicted_zero": True,
                                "confirmed": ok, "poly": src[:60]})
    print(f"predictions: confirmed {confirmed}  refuted {refuted}")
    print("by prime:", Counter((x['p'], x['confirmed']) for x in results))
    for x in results[:10]:
        print("  ", x)
    OUT.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())