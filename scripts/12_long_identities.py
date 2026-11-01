#!/usr/bin/env python3
"""For every 'equal prefix' pair, measure how far the agreement extends on b-files.

    python scripts/12_long_identities.py

Writes reports/long_equal.json with, for each pair: agreement length, whether the
pair is cross-referenced, and whether either name is labelled as a duplicate.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "long_equal.json"

_cache: dict[str, dict | None] = {}


def bfile(aid: str, limit: int = 20000):
    if aid in _cache:
        return _cache[aid]
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    q = line.split()
                    if len(q) >= 2:
                        try:
                            d[int(q[0])] = int(q[1])
                        except ValueError:
                            pass
                    if len(d) > limit:
                        break
        except OSError:
            d = None
    _cache[aid] = d
    return d


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    pairs = con.execute("select aid, dst from numeric_relation where kind='equal'").fetchall()
    name = dict(con.execute("select aid, name from seq"))
    doc = set()
    for q in ("select aid, dst from definition", "select aid, dst from identity",
              "select src, dst from xref"):
        for a, b in con.execute(q):
            doc.add((a, b) if a < b else (b, a))

    def labelled(aid: str) -> bool:
        low = name[aid].lower()
        return any(m in low for m in ("duplicate of", "same as a", "erroneous version",
                                      "identical to a", "is a duplicate"))

    out = []
    for a, b in pairs:
        da, db = bfile(a), bfile(b)
        if not da or not db:
            continue
        common = sorted(set(da) & set(db))
        agree = 0
        for n in common:
            if da[n] == db[n]:
                agree += 1
            else:
                break
        out.append({
            "a": a, "b": b, "agree": agree, "common": len(common),
            "first_mismatch": common[agree] if agree < len(common) else None,
            "cross_referenced": (a, b) in doc or (b, a) in doc,
            "labelled_duplicate": labelled(a) or labelled(b),
        })
    out.sort(key=lambda r: -r["agree"])
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"pairs with both b-files: {len(out)}")
    for lo in (25, 50, 100, 500, 1000):
        print(f"  agree >= {lo}: {sum(1 for r in out if r['agree'] >= lo)}")
    print(f"  unlabelled AND not cross-referenced AND agree >= 1000: "
          f"{sum(1 for r in out if not r['labelled_duplicate'] and not r['cross_referenced'] and r['agree'] >= 1000)}")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
