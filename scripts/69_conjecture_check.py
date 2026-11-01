#!/usr/bin/env python3
"""Check conjectured formulas with the parser: 'Conjecture: a(n) = <expr>'.

    python scripts/69_conjecture_check.py [--limit N]
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


_con = None


def _db():
    global _con
    if _con is None:
        _con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    return _con


def bfile(aid, limit=80):
    if aid in _cache:
        return _cache[aid]
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        row = _db().execute("select offset1, terms from seq where aid=?", (aid,)).fetchone()
        if row and row[1]:
            off = row[0] if row[0] is not None else 0
            try:
                vals = [int(x) for x in row[1].split(",") if x.strip()]
            except ValueError:
                _cache[aid] = None
                return None
            d = {off + i: v for i, v in enumerate(vals[:limit])}
            _cache[aid] = d or None
            return _cache[aid]
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
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, text from stmt where text like '%onjectur%' and text like '%a(n) = %'").fetchall()
    import re as _re
    strict = []
    for aid, text in rows:
        t = text.strip()
        m = _re.match(r"(?:Conjecture[s]?[:.]?|Conjectured[:.]?)\s*a\(n\)\s*=\s*(.+)$", t, _re.I)
        if not m:
            m = _re.match(r"a\(n\)\s*=\s*(.+?)\s*\((?:conjectured|conjecture)\)\s*$", t, _re.I)
        if m:
            strict.append((aid, m.group(1)))
    rows = strict
    print("strict conjectures:", len(rows))
    stats = Counter()
    bad = []
    for aid, text in rows:
        rhs, lo = clean_rhs(text)
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
        # bare A-number formula: try offsets
        if ast[0] == "call" and isinstance(ast[1], str) and ast[1].startswith("A") and len(ast[1]) == 7 and len(ast[2]) == 1:
            other = bfile(ast[1])
            if other:
                best = None
                for dd in range(-3, 4):
                    common = [n for n in d if (n + dd) in other][:40]
                    if len(common) < 10:
                        continue
                    sc = sum(1 for n in common if d[n] == other[n + dd])
                    if best is None or sc > best[0]:
                        best = (sc, dd, len(common))
                if best and best[0] == best[2]:
                    stats["confirmed"] += 1
                    continue
        ns = [n for n in sorted(d) if n >= lo][:40]
        if len(ns) < 5:
            stats["short"] += 1
            continue
        best = None
        for shift in (0, 1, -1, 2, -2):
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
        if score == len(flags):
            stats["confirmed"] += 1
        else:
            j = len(flags)
            while j > 0 and flags[j - 1]:
                j -= 1
            suffix = len(flags) - j
            if suffix >= 10:
                stats["suffix"] += 1
            else:
                stats["sporadic"] += 1
                if limit and len(bad) >= limit:
                    continue
                bad.append({"aid": aid, "shift": shift, "score": score, "total": len(flags),
                            "first_bad": ns[flags.index(False)], "text": text[:160]})
    print(dict(stats))
    bad.sort(key=lambda x: x["score"] - x["total"])
    for b in bad[:20]:
        print(f"  {b['aid']} {b['score']}/{b['total']} shift={b['shift']} | {b['text'][:110]}")
    json.dump(bad, open(ROOT / "reports" / "conjecture_unconfirmed.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))