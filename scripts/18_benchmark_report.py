#!/usr/bin/env python3
"""Finalize the benchmark: mark C-finite vs residual, summarise.

    python scripts/18_benchmark_report.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "benchmark_summary.json"


def main() -> int:
    con = sqlite3.connect(str(DB))
    cols = [r[1] for r in con.execute("PRAGMA table_info(bench)")]
    if "cf_class" not in cols:
        con.execute("ALTER TABLE bench ADD COLUMN cf_class TEXT")
    con.execute("""
        UPDATE bench SET cf_class = CASE
            WHEN aid IN (SELECT aid FROM bench_result WHERE solved = 1) THEN 'C_finite'
            WHEN aid IN (SELECT aid FROM bench_result) THEN 'residual'
            ELSE 'unscored' END
    """)
    con.commit()

    rows = con.execute("select tier, split, cf_class from bench").fetchall()
    by_class = Counter(r[2] for r in rows)
    by_tier_class = defaultdict(Counter)
    for tier, split, c in rows:
        by_tier_class[tier][c] += 1
    print("bench:", len(rows), dict(by_class))
    for tier in ("easy", "medium", "hard"):
        print(f"  {tier:6}: {dict(by_tier_class[tier])}")

    resid = con.execute("""
        select b.aid, b.expr, b.tier, b.ops from bench b
        where b.cf_class='residual' order by b.ops desc limit 30""").fetchall()
    print("\nresidual examples:")
    for aid, expr, tier, ops in resid[:20]:
        print(f"  {aid} [{tier}, {ops} ops] {expr[:85]}")

    # how many of the residual are rational (division by n-containing expr)
    n_div = sum(1 for r in con.execute(
        "select expr from bench where cf_class='residual'") if "/" in r[0])
    print(f"\nresidual with division: {n_div}")
    print("residual total:", by_class.get("residual", 0))

    out = {
        "bench_total": len(rows),
        "by_class": dict(by_class),
        "by_tier_class": {k: dict(v) for k, v in by_tier_class.items()},
        "residual_with_division": n_div,
        "split_sizes": dict(con.execute(
            "select split, count(*) from bench group by 1")),
        "baseline": json.load(open(ROOT / "reports" / "baseline.json")),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
