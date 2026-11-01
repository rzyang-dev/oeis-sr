#!/usr/bin/env python3
"""Literature check via the DeepSeek web-search API.

    python scripts/53_literature_search.py
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
OUT = ROOT / "reports" / "literature_search.json"

QUERIES = [
    "congruences for diagonal coefficients of powers of a power series",
    "Rowland Yassawi automatic congruences diagonals rational functions",
    "supercongruences diagonal binomial sums mod p",
    "coefficient of x^n in f(x)^n divisible by p congruence",
    "Gauss congruence diagonal coefficients algebraic functions",
    "vanishing mod p of diagonal coefficients generating function",
    "congruences Apéry-like numbers mod p zero residue class",
    "Ramanujan type congruences theta functions coefficients",
    "congruences for coefficients of powers of theta functions mod p",
    "Ramanujan congruences partition function modulo 5 7 11",
]


def search(query, count=8):
    body = json.dumps({"query": query, "count": count, "need_content": False}).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/tools/search",
        data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main() -> int:
    allres = {}
    for q in QUERIES:
        try:
            res = search(q)
        except Exception as e:
            print("ERR", q, type(e).__name__, e)
            continue
        items = res.get("results", [])
        allres[q] = items
        print("=" * 78)
        print("Q:", q)
        for x in items[:6]:
            print("  -", (x.get("title") or "")[:90])
            print("    ", (x.get("url") or "")[:110])
            s = (x.get("summary") or "").replace("\n", " ")
            print("    ", s[:200])
    OUT.write_text(json.dumps(allres, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())