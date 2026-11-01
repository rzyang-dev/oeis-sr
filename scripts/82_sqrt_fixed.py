#!/usr/bin/env python3
"""Dirichlet square roots with correct offsets.

For every sequence covering n=1 with a(1) a perfect square, compute b with
a = b * b, then look b up in the corpus.

    python scripts/82_sqrt_fixed.py
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
OUT = ROOT / "reports" / "sqrt_fixed.json"
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
    seqs = {}
    for aid, off, terms in con.execute("select aid, offset1, terms from seq"):
        if not terms:
            continue
        off = off if off is not None else 0
        try:
            v = [int(x) for x in terms.split(",")[:N]]
        except ValueError:
            continue
        d = {off + i: x for i, x in enumerate(v)}
        seqs[aid] = (off, d)
    print("sequences:", len(seqs))

    keylen = 10
    hashmap = defaultdict(list)
    for aid, (off, d) in seqs.items():
        key = tuple(d.get(k) for k in range(1, keylen + 1))
        if None in key:
            continue
        hashmap[key].append(aid)
    print("keys:", len(hashmap))

    hits = []
    tested = 0
    for aid, (off, d) in seqs.items():
        if 1 not in d:
            continue
        a1 = d[1]
        if a1 <= 0:
            continue
        r = math.isqrt(a1)
        if r * r != a1 or r == 0:
            continue
        M = min(N, max(d))
        b = {1: r}
        ok = True
        for n in range(2, M + 1):
            if n not in d:
                ok = False
                break
            s = sum(b[x] * b[n // x] for x in divisors(n) if 1 < x < n)
            num = d[n] - s
            if num % (2 * r) != 0:
                ok = False
                break
            b[n] = num // (2 * r)
        if not ok or len(b) < keylen + 1:
            continue
        tested += 1
        key = tuple(b.get(k) for k in range(1, keylen + 1))
        if None in key:
            continue
        for cand in hashmap.get(key, []):
            if cand == aid:
                continue
            coff, cd = seqs[cand]
            good = 0
            for n in range(1, M + 1):
                if n not in d or n not in cd:
                    break
                if sum(cd[x] * cd[n // x] for x in divisors(n)) == d[n]:
                    good += 1
                else:
                    break
            if good >= 10:
                hits.append((aid, cand, good))
    print("tested square roots:", tested)
    print("verified matches:", len(hits))
    names = dict(con.execute("select aid, name from seq"))
    seen = set()
    for a, b, g in hits[:30]:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        print(f"  {a} = {b} * {b}  ok={g}")
        print(f"     A: {names.get(a,'')[:60]}")
        print(f"     B: {names.get(b,'')[:60]}")
    OUT.write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
