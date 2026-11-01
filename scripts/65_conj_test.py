#!/usr/bin/env python3
"""Test OEIS conjectures mechanically: equality with another sequence, divisibility.

    python scripts/65_conj_test.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "conjecture_tests.json"

_cache = {}


def bfile(aid, limit=400):
    if aid in _cache:
        return _cache[aid]
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        _cache[aid] = None
        return None
    v = {}
    try:
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
    except OSError:
        _cache[aid] = None
        return None
    _cache[aid] = v or None
    return _cache[aid]


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, text from stmt where text like '%Conjecture%'").fetchall()
    pat_eq = re.compile(r"a\(n\)\s*=\s*A(\d{6})\((n(?:[+-]\d+)?)\)\s*[,.]?\s*(?:for\s+)?(?:n\s*[<>]=?\s*\d+)?\s*\.?\s*$", re.I)
    tested = []
    for aid, t in rows:
        tl = t.lower()
        if "proved" in tl or "this is true" in tl:
            continue
        m = pat_eq.search(t.strip())
        if not m:
            continue
        other = "A" + m.group(1)
        idx = m.group(2)
        rng = re.search(r"n\s*(>=|>|<=|<)\s*(\d+)", t)
        lo = -10**9
        if rng:
            op, val = rng.group(1), int(rng.group(2))
            if op == ">":
                lo = val + 1
            elif op == ">=":
                lo = val
        off = 0
        if idx != "n":
            off = int(idx[1:])
        da = bfile(aid)
        db = bfile(other)
        if not da or not db:
            continue
        common = [n for n in da if (n + off) in db and n >= lo]
        if len(common) < 20:
            continue
        bad = [n for n in common if da[n] != db[n + off]]
        tested.append({"aid": aid, "other": other, "off": off,
                       "checked": len(common), "mismatches": len(bad),
                       "first_bad": bad[:3], "text": t[:140]})
    tested.sort(key=lambda x: x["mismatches"])
    print("tested equality conjectures:", len(tested))
    print("clean (0 mismatch):", sum(1 for x in tested if x["mismatches"] == 0))
    print("violated:", [x for x in tested if x["mismatches"] > 0][:10])
    OUT.write_text(json.dumps(tested, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())