#!/usr/bin/env python3
"""Dirichlet square roots: if a = b * b, does b occur in OEIS?

    python scripts/81_dirichlet_sqrt.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "dirichlet_sqrt.json"
N = 40


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return ds


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    hashmap = defaultdict(list)
    seqs = {}
    for aid, terms in con.execute("select aid, terms from seq"):
        if not terms:
            continue
        try:
            v = [int(x) for x in terms.split(",")[:N]]
        except ValueError:
            continue
        if len(v) < 10:
            continue
        seqs[aid] = v
        hashmap[tuple(v[1:9])].append(aid)
    print("sequences:", len(seqs), "keys:", len(hashmap))

    hits = []
    for aid, v in seqs.items():
        a1 = v[1]
        if a1 <= 0:
            continue
        r = math.isqrt(a1)
        if r * r != a1 or r == 0:
            continue
        M = min(N, len(v) - 1)
        b = [0] * (N + 1)
        b[1] = r
        ok = True
        for n in range(2, M + 1):
            s = 0
            for d in divisors(n):
                if 1 < d < n:
                    s += b[d] * b[n // d]
            num = v[n] - s
            if num % (2 * r) != 0:
                ok = False
                break
            b[n] = num // (2 * r)
        if not ok:
            continue
        key = tuple(b[1:13]) if len(b) > 12 else tuple(b[1:9])
        for cand in hashmap.get(tuple(b[1:9]), []):
            if cand == aid:
                continue
            cb = seqs.get(cand)
            if not cb or cb[1] != r:
                continue
            good = 0
            for n in range(2, M + 1):
                if n >= len(cb):
                    break
                s2 = sum(cb[d] * cb[n // d] for d in divisors(n))
                if s2 != v[n]:
                    break
                good += 1
            if good >= 10:
                hits.append((aid, cand, good))
    print("square-root matches:", len(hits))
    names = dict(con.execute("select aid, name from seq"))
    seen = set()
    for a, b, g in hits[:25]:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        print(f"  {a} = {b} * {b}  ok={g}")
        print(f"     A: {names.get(a,'')[:62]}")
        print(f"     B: {names.get(b,'')[:62]}")
    OUT.write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())