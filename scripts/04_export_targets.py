#!/usr/bin/env python3
"""Export a symbolic-regression ready dataset from oeis.db.

    python scripts/04_export_targets.py --min-terms 10 --clean --limit 2000 \
        --out data/sr_pool_sample.jsonl

Each output line is one sequence:

    {"aid": "A000045", "name": "...", "keywords": [...], "n0": 0,
     "terms": [0, 1, 1, 2, ...], "formulas": [{"kind": "gf", "text": "..."}]}

"terms"[i] is a(n0 + i), i.e. the %O offset is already folded in.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
CLEAN_KW = ("cons", "base", "frac", "dead", "dupe", "recycled")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-terms", type=int, default=10)
    ap.add_argument("--max-terms", type=int, default=1000)
    ap.add_argument("--clean", action="store_true",
                    help="drop cons/base/frac/dead/dupe/recycled entries")
    ap.add_argument("--has-formula", action="store_true")
    ap.add_argument("--has-bfile", action="store_true")
    ap.add_argument("--kind", default="",
                    help="comma separated formula kinds, e.g. closed_form,gf")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--random", action="store_true")
    ap.add_argument("--out", default="data/sr_pool_sample.jsonl")
    a = ap.parse_args(argv)

    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    where = ["s.n_terms >= ?", "s.n_terms <= ?", "s.all_int64 = 1"]
    params: list = [a.min_terms, a.max_terms]
    if a.clean:
        for kw in CLEAN_KW:
            where.append("not exists (select 1 from keyword k where k.aid=s.aid and k.kw=?)")
            params.append(kw)
    if a.kind:
        kinds = [k.strip() for k in a.kind.split(",") if k.strip()]
        marks = ",".join("?" * len(kinds))
        where.append(f"exists (select 1 from formula f where f.aid=s.aid "
                     f"and f.kind in ({marks}) and f.conjectural=0)")
        params.extend(kinds)
    elif a.has_formula:
        where.append("exists (select 1 from formula f where f.aid=s.aid)")
    if a.has_bfile:
        where.append("exists (select 1 from attachment t where t.aid=s.aid "
                     "and t.name like 'b%.txt')")
    order = "random()" if a.random else "s.aid"
    sql = (f"select s.aid, s.name, s.keywords, s.offset1, s.terms from seq s "
           f"where {' and '.join(where)} order by {order} limit ?")
    params.append(a.limit)

    out_path = ROOT / a.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for aid, name, kw, n0, terms in con.execute(sql, params):
            fm = [{"kind": k, "text": t} for k, t in con.execute(
                "select kind, text from formula where aid=? order by idx", (aid,))]
            rec = {
                "aid": aid,
                "name": name,
                "keywords": kw.split(",") if kw else [],
                "n0": n0,
                "terms": [int(x) for x in terms.split(",")] if terms else [],
                "formulas": fm,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} sequences to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
