#!/usr/bin/env python3
"""Export the benchmark as JSONL (one sequence per line).

    python scripts/19_export_benchmark.py [--out data/benchmark.jsonl]
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"


def main(argv: list[str]) -> int:
    out_path = ROOT / (argv[argv.index("--out") + 1] if "--out" in argv else "data/benchmark.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""
        SELECT b.aid, s.name, b.expr, s.offset1, s.terms, s.keywords,
               b.tier, b.ops, b.degree, b.split, b.cf_class, b.leak_group
        FROM bench b JOIN seq s ON s.aid = b.aid
        ORDER BY b.split, b.aid""").fetchall()
    n = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for aid, name, expr, off, terms, kw, tier, ops, deg, split, cf, lg in rows:
            rec = {
                "aid": aid, "name": name, "expr": expr, "n0": off,
                "terms": [int(x) for x in terms.split(",")] if terms else [],
                "keywords": kw.split(",") if kw else [],
                "tier": tier, "ops": ops, "degree": deg,
                "split": split, "class": cf, "leak_group": lg,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} records to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
