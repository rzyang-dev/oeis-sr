#!/usr/bin/env python3
"""Dirichlet square-root search with long-window (b-file) verification."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "sqrt_long.json"
L = 40
VER = 100


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


_c = {}
def bfile(aid, limit=250):
    if aid in _c:
        return _c[aid]
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = {}
    if f.exists():
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        d[int(q[0])] = int(q[1])
                    except ValueError:
                        pass
                if len(d) >= limit:
                    break
        except OSError:
            pass
    _c[aid] = d or None
    return _c[aid]


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    seqs = {}
    for aid, off, terms in con.execute("select aid, offset1, terms from seq"):
        if not terms:
            continue
        off = off if off is not None else 0
        try:
            v = [int(x) for x in terms.split(",")[:L]]
        except ValueError:
            continue
        d = {off + i: x for i, x in enumerate(v)}
        if all(k in d for k in range(1, L + 1)):
            seqs[aid] = d
    print("sequences with n=1..40:", len(seqs))
    hashmap = defaultdict(list)
    for aid, d in seqs.items():
        hashmap[tuple(d[k] for k in range(1, L + 1))].append(aid)
    print("keys:", len(hashmap))

    cands = []
    for aid, d in seqs.items():
        a1 = d[1]
        if a1 <= 0:
            continue
        r = math.isqrt(a1)
        if r * r != a1 or r == 0:
            continue
        b = {1: r}
        ok = True
        for n in range(2, L + 1):
            s = sum(b[x] * b[n // x] for x in divisors(n) if 1 < x < n)
            num = d[n] - s
            if num % (2 * r) != 0:
                ok = False
                break
            b[n] = num // (2 * r)
        if ok:
            cands.append((aid, b))
    print("with square root defined to 40:", len(cands))

    hits = []
    for aid, b in cands:
        key = tuple(b[k] for k in range(1, L + 1))
        for cand in hashmap.get(key, []):
            if cand == aid:
                continue
            ha, hb = bfile(aid), bfile(cand)
            if not ha or not hb:
                continue
            ns = [n for n in range(1, VER + 1) if n in ha and n in hb]
            if len(ns) < VER:
                continue
            good = 0
            for n in ns:
                if sum(hb[x] * hb[n // x] for x in divisors(n) if x in hb and (n // x) in hb) == ha[n]:
                    good += 1
                else:
                    break
            if good >= VER:
                hits.append((aid, cand, good))
    print("verified long-window matches:", len(hits))
    names = dict(con.execute("select aid, name from seq"))
    seen = set()
    for a, b_, g in hits[:30]:
        if (a, b_) in seen:
            continue
        seen.add((a, b_))
        print(f"  {a} = {b_} * {b_}  ok={g}")
        print(f"     A: {names.get(a,'')[:60]}")
        print(f"     B: {names.get(b_,'')[:60]}")
    OUT.write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
