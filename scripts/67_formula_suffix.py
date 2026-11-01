#!/usr/bin/env python3
"""Classify formula-vs-bfile agreement: full / suffix / sporadic.

    python scripts/67_formula_suffix.py --shard k --of n [--limit m]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.formula import parse, ev, FormulaError, Unsupported, clean_rhs

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
_cache = {}


def bfile(aid, limit=80):
    if aid in _cache:
        return _cache[aid]
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        _cache[aid] = None
        return None
    d = {}
    try:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            q = line.split()
            if len(q) >= 2:
                try:
                    d[int(q[0])] = int(q[1])
                except ValueError:
                    pass
            if len(d) >= limit:
                break
    except OSError:
        _cache[aid] = None
        return None
    _cache[aid] = d or None
    return _cache[aid]


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, text from formula where text like 'a(n) = %'").fetchall()
    rows.sort()
    if limit:
        rows = rows[:limit]
    if of > 1:
        rows = rows[shard::of]
    print("shard", shard, "rows", len(rows), flush=True)

    stats = Counter()
    out = []
    for i, (aid, text) in enumerate(rows):
        rhs, lo = clean_rhs(text.split("=", 1)[1].strip())
        ast = None
        for cand in [rhs] + [x.strip() for x in rhs.split("=")[:3]]:
            try:
                ast = parse(cand)
                break
            except FormulaError:
                continue
        if ast is None:
            stats["parse_fail"] += 1
            continue
        d = bfile(aid)
        if not d:
            stats["no_bfile"] += 1
            continue
        ns = [n for n in sorted(d) if n >= lo][:30]
        if len(ns) < 5:
            stats["short"] += 1
            continue
        best = None
        for shift in range(-3, 4):
            flags = []
            err = None
            for n in ns:
                env = {"n": Fraction(n + shift),
                       "__seq__": lambda a, k: Fraction(bfile(a)[k]) if bfile(a) and k in bfile(a) else (_ for _ in ()).throw(FormulaError("missing A")),
                       "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing a"))}
                try:
                    v = ev(ast, env)
                except Unsupported:
                    err = "unsupported"
                    break
                except Exception:
                    err = "eval"
                    break
                flags.append(v.denominator == 1 and v.numerator == d[n])
            if err:
                break
            score = sum(flags)
            if best is None or score > best[0]:
                best = (score, shift, flags)
        if err:
            stats[err] += 1
            continue
        score, shift, flags = best
        if shift != 0 and score == len(flags):
            stats["full_shifted"] += 1
            continue
        if all(flags):
            stats["full"] += 1
        else:
            # largest suffix of matches
            k = len(flags)
            j = k
            while j > 0 and flags[j - 1]:
                j -= 1
            suffix = k - j
            if suffix >= 10:
                stats["suffix"] += 1
                out.append({"aid": aid, "kind": "suffix", "from": ns[j], "text": text[:120]})
            else:
                stats["sporadic"] += 1
                first_bad = ns[flags.index(False)]
                out.append({"aid": aid, "kind": "sporadic", "at": first_bad, "text": text[:120]})
        if (i + 1) % 2000 == 0:
            print("  ", i + 1, dict(stats), flush=True)
    print("done", dict(stats), flush=True)
    json.dump(out, open(ROOT / "reports" / f"formula_suffix_{shard:02d}.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))