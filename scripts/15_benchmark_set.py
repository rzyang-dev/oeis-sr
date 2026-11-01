#!/usr/bin/env python3
"""Select the formula-recovery benchmark set and label its difficulty.

Candidates: sequences with a syntactic closed form (%F line of kind
'closed_form', i.e. a(n) = pure arithmetic in n), at least 15 terms, and a
b-file for held-out validation.

Labels: cleaned expression, token/operator counts, polynomial degree,
difficulty tier, leak group.

    python scripts/15_benchmark_set.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "benchmark_set.json"

ATTR = re.compile(r"\s*-\s*_[^_]+_,.*$")
CLEAN = re.compile(r"^a\(n\)\s*=\s*")


def clean(t: str) -> str:
    t = ATTR.sub("", t).strip()
    t = t.rstrip(".")
    t = CLEAN.sub("", t)
    return t.strip()


def features(expr: str) -> dict:
    ops = len(re.findall(r"[+\-*/^]", expr))
    tokens = len(re.findall(r"\d+|[a-z]+|[+\-*/^()]", expr))
    deg = 0
    for m in re.finditer(r"n\^(\d+)", expr):
        deg = max(deg, int(m.group(1)))
    return {
        "tokens": tokens,
        "ops": ops,
        "degree": deg,
        "has_div": int("/" in expr),
        "has_alt": int("(-1)" in expr),
        "tier": "easy" if ops <= 3 else ("medium" if ops <= 7 else "hard"),
    }


def main() -> int:
    con = sqlite3.connect(str(DB))
    rows = con.execute("""
        SELECT f.aid, f.idx, f.text, s.n_terms, s.offset1
        FROM formula f JOIN seq s ON s.aid = f.aid
        WHERE f.kind = 'closed_form' AND s.n_terms >= 15
          AND s.aid IN (SELECT aid FROM attachment WHERE name LIKE 'b%.txt')
    """).fetchall()
    print("raw closed-form candidates:", len(rows))

    seen, bench = set(), []
    for aid, idx, text, n_terms, off in rows:
        if aid in seen:
            continue
        expr = clean(text)
        if not expr or len(expr) > 300:
            continue
        if re.search(r"[A-Za-z]{2,}", expr):      # leftover prose
            continue
        seen.add(aid)
        f = features(expr)
        bench.append({"aid": aid, "expr": expr, "n_terms": n_terms,
                      "offset1": off, "formula_idx": idx, **f})
    print("benchmark entries:", len(bench))

    con.execute("DROP TABLE IF EXISTS bench")
    con.execute("""CREATE TABLE bench (
        aid TEXT PRIMARY KEY, expr TEXT, n_terms INTEGER, offset1 INTEGER,
        tokens INTEGER, ops INTEGER, degree INTEGER, has_div INTEGER,
        has_alt INTEGER, tier TEXT, leak_group INTEGER, split TEXT)""")
    lg = dict(con.execute("select aid, leak_group from seq_class"))
    con.executemany(
        "INSERT INTO bench VALUES (?,?,?,?,?,?,?,?,?,?,?,NULL)",
        [(b["aid"], b["expr"], b["n_terms"], b["offset1"], b["tokens"], b["ops"],
          b["degree"], b["has_div"], b["has_alt"], b["tier"], lg.get(b["aid"]))
         for b in bench])
    con.execute("CREATE INDEX idx_bench_leak ON bench(leak_group)")
    con.commit()

    print("tiers:", Counter(b["tier"] for b in bench))
    print("ops distribution:", sorted(Counter(b["ops"] for b in bench).items())[:12])
    print("degree distribution:", sorted(Counter(b["degree"] for b in bench).items()))
    print("examples:")
    for b in bench[:8]:
        print(f"  {b['aid']} [{b['tier']}] {b['expr'][:70]}")
    OUT.write_text(json.dumps({"n": len(bench),
                               "tiers": dict(Counter(b["tier"] for b in bench)),
                               "ops": dict(Counter(b["ops"] for b in bench)),
                               "examples": bench[:50]}, indent=1), encoding="utf-8")
    print("wrote", OUT)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
