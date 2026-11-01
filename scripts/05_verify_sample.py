#!/usr/bin/env python3
"""Independent spot check: compare oeis.db rows with the raw .seq text.

The comparison uses a deliberately naive parser (line prefixes + split) so a
bug in oeisdb.internal would show up as a mismatch.

    python scripts/05_verify_sample.py --n 100
"""
from __future__ import annotations

import random
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"


def naive(path: Path) -> dict:
    name, kw, off, terms = "", [], None, []
    parts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if len(line) < 11 or line[0] != "%":
            continue
        code, payload = line[1], line[11:]
        if code == "N":
            name = payload
        elif code == "K":
            kw = [k.strip() for k in payload.split(",") if k.strip()]
        elif code == "O":
            off = int(payload.split(",")[0])
        elif code in "STU":
            parts.append(payload.strip())
    if parts:
        joined = ",".join(p.strip().rstrip(",") for p in parts)
        terms = [t.strip() for t in joined.split(",") if t.strip()]
    return {"name": name, "keywords": kw, "offset1": off, "terms": terms}


def main(argv: list[str]) -> int:
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 100
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select aid from seq order by random() limit ?", (n,))]
    bad = 0
    for aid in aids:
        path = DATA / "seq" / ("A" + aid[1:4]) / f"{aid}.seq"
        exp = naive(path)
        got = con.execute(
            "select name, keywords, offset1, terms from seq where aid=?", (aid,)).fetchone()
        got_terms = got[3].split(",") if got[3] else []
        problems = []
        if exp["name"] != got[0]:
            problems.append("name")
        if set(exp["keywords"]) != set((got[1] or "").split(",")):
            problems.append("keywords")
        if exp["offset1"] != got[2]:
            problems.append("offset")
        if exp["terms"] != got_terms:
            problems.append(f"terms({len(exp['terms'])} vs {len(got_terms)})")
        if problems:
            bad += 1
            print(f"  MISMATCH {aid}: {', '.join(problems)}")
    print(f"checked {len(aids)} entries, mismatches: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
