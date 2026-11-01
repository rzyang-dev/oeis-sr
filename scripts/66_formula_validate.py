#!/usr/bin/env python3
"""Parse every 'a(n) = ...' formula and validate it against the b-file.

    python scripts/66_formula_validate.py --shard k --of n
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


def bfile(aid, limit=300):
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
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, text from formula where text like 'a(n) = %'").fetchall()
    rows.sort()
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    if limit:
        rows = rows[:limit]
    if of > 1:
        rows = rows[shard::of]
    print("shard", shard, "formulas", len(rows), flush=True)

    stats = Counter()
    bad = []
    parse_fail = []
    out = ROOT / "reports" / f"formula_val_{shard:02d}.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for i, (aid, text) in enumerate(rows):
            rhs, lo = clean_rhs(text.split("=", 1)[1].strip())
            ast = None
            for cand in [rhs] + [x.strip() for x in rhs.split("=")[:3]]:
                try:
                    ast = parse(cand)
                    break
                except FormulaError:
                    continue
            try:
                if ast is None:
                    raise FormulaError("no parse")
            except FormulaError as e:
                stats["parse_fail"] += 1
                if len(parse_fail) < 50:
                    parse_fail.append({"aid": aid, "text": text[:120], "err": str(e)[:80]})
                continue
            d = bfile(aid)
            if not d:
                stats["no_bfile"] += 1
                continue
            ns = [n for n in sorted(d) if n >= lo][:40]
            env = {"n": None,
                   "__seq__": lambda a, k: Fraction(bfile(a)[k]) if bfile(a) and k in bfile(a) else (_ for _ in ()).throw(FormulaError("missing A")),
                   "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing a"))}
            ok = True
            first_bad = None
            for n in ns:
                env["n"] = Fraction(n)
                try:
                    v = ev(ast, env)
                except Unsupported:
                    ok = None
                    first_bad = n
                    stats["unsupported"] += 1
                    break
                except Exception:
                    ok = False
                    first_bad = n
                    stats["eval_err"] += 1
                    break
                if v.denominator != 1 or v.numerator != d[n]:
                    ok = False
                    first_bad = n
                    break
            if ok:
                stats["match"] += 1
            else:
                stats["mismatch"] += 1
                if len(bad) < 200:
                    bad.append({"aid": aid, "n": first_bad, "text": text[:140], "value": d.get(first_bad)})
            fh.write(json.dumps({"aid": aid, "ok": ok, "n": first_bad}) + chr(10))
            if (i + 1) % 5000 == 0:
                print("  ", i + 1, dict(stats), flush=True)
    print("done", dict(stats), flush=True)
    json.dump({"bad": bad, "parse_fail": parse_fail},
              open(ROOT / "reports" / f"formula_val_{shard:02d}_detail.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))