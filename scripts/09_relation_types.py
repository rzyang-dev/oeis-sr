#!/usr/bin/env python3
"""Classify definition edges by the kind of relation they encode.

Writes reports/relation_types.json. The categories matter because a pointwise
EML tree can only express "pointwise" relations; the others need sequence-level
operators (shift, prefix sum, row extraction, inverse/positions, transforms).

    python scripts/09_relation_types.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "relation_types.json"


def classify(text: str, dst: str) -> str:
    low = text.lower()
    if "partial sum" in low:
        return "partial_sums"
    if "row sum" in low:
        return "row_sums"
    if "first difference" in low or "differences of" in low:
        return "differences"
    if "positions of" in low or "indices of" in low:
        return "positions"
    if "transform" in low:
        return "transform"
    if "bisection" in low:
        return "bisection"
    if "permutation" in low or "conjugate" in low:
        return "permutation"
    if "record" in low:
        return "records"
    if re.search(re.escape(dst) + r"\(\s*n\s*\)", text):
        return "pointwise"
    if re.search(re.escape(dst) + r"\(\s*n\s*[-+]\s*\d", text):
        return "shift"
    return "other"


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("select aid, dst, text from definition").fetchall()
    cnt = Counter(classify(t, d) for _, d, t in rows)
    n = len(rows)
    out = {
        "edges": n,
        "by_kind": {k: {"n": v, "pct": round(100 * v / n, 1)} for k, v in cnt.most_common()},
        "pointwise_call_Axxx_n": sum(1 for _, _, t in rows if re.search(r"A\d{6}\(n\)", t)),
        "any_call_Axxx_paren": sum(1 for _, _, t in rows if re.search(r"A\d{6}\(", t)),
        "shifted_call": sum(1 for _, _, t in rows if re.search(r"A\d{6}\(\s*n\s*[-+]\s*\d", t)),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out["by_kind"], indent=1, ensure_ascii=False))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
