#!/usr/bin/env python3
"""Full-corpus formula consistency check (shift 0 only, fast).

    python scripts/70_consistency.py --shard k --of n
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

from oeisdb.formula import parse, parse_full, ev, FormulaError, Unsupported, clean_rhs

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
_cache = {}
_con = None


def db():
    global _con
    if _con is None:
        _con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    return _con


def terms(aid, limit=60):
    if aid in _cache:
        return _cache[aid]
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = {}
    if f.exists():
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
            d = {}
    if not d:
        row = db().execute("select offset1, terms from seq where aid=?", (aid,)).fetchone()
        if row and row[1]:
            off = row[0] if row[0] is not None else 0
            try:
                vals = [int(x) for x in row[1].split(",") if x.strip()]
                d = {off + i: v for i, v in enumerate(vals[:limit])}
            except ValueError:
                d = {}
    _cache[aid] = d or None
    return _cache[aid]


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = db()
    rows = con.execute("select aid, text from formula where text like 'a(n) = %'").fetchall()
    rows.sort()
    lim = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    if lim:
        rows = rows[:lim]
    if of > 1:
        rows = rows[shard::of]
    print("shard", shard, "rows", len(rows), flush=True)
    stats = Counter()
    sporadic = []
    suffix = []
    for i, (aid, text) in enumerate(rows):
        rhs, lo = clean_rhs(text.split("=", 1)[1].strip())
        ast = None
        cands = [rhs] + [x.strip() for x in rhs.split("=")[:3]] + [rhs.split(";")[0]]
        for cand in cands:
            try:
                ast = parse_full(cand)
                break
            except FormulaError:
                continue
        if ast is None:
            stats["parse_fail"] += 1
            continue
        d = terms(aid)
        if not d:
            stats["no_data"] += 1
            continue
        ns = [n for n in sorted(d) if n >= lo][:30]
        if len(ns) < 5:
            stats["short"] += 1
            continue
        flags = []
        checked = []
        err = None
        for n in ns:
            env = {"n": Fraction(n),
                   "__seq__": lambda a, k: Fraction(terms(a)[k]) if terms(a) and k in terms(a) else (_ for _ in ()).throw(FormulaError("missing_A")),
                   "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing_a"))}
            try:
                v = ev(ast, env)
            except Unsupported:
                err = "unsupported"; break
            except FormulaError as e:
                if "missing_" in str(e):
                    continue
                err = "eval"; break
            except Exception:
                err = "eval"; break
            flags.append(v.denominator == 1 and v.numerator == d[n])
            checked.append(n)
        if err:
            stats[err] += 1
            continue
        if len(flags) < 5:
            stats["short"] += 1
            continue
        ns = checked
        if all(flags):
            stats["full"] += 1
        else:
            j = len(flags)
            while j > 0 and flags[j - 1]:
                j -= 1
            if len(flags) - j >= 10:
                stats["suffix"] += 1
                if len(suffix) < 300:
                    suffix.append({"aid": aid, "from": ns[j], "text": text[:150]})
            else:
                stats["sporadic"] += 1
                if len(sporadic) < 300:
                    sporadic.append({"aid": aid, "at": ns[flags.index(False)], "text": text[:150]})
        if (i + 1) % 5000 == 0:
            print("  ", i + 1, dict(stats), flush=True)
    print("done", dict(stats), flush=True)
    json.dump({"sporadic": sporadic, "suffix": suffix},
              open(ROOT / "reports" / f"consistency_{shard:02d}.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))