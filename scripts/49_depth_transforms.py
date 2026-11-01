#!/usr/bin/env python3
"""Do numeric relations preserve congruence depth?

Take every depth>=2 sequence, follow its numeric_relation edges, compute depth
for the partners, and compare.

    python scripts/49_depth_transforms.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "depth_transforms.json"
PRIMES = (5, 7, 11)


def bfile(aid, limit=1200):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    v = []
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        v.append((int(q[0]), int(q[1])))
                    except ValueError:
                        pass
                if len(v) >= limit:
                    break
    except OSError:
        return None
    return v or None


def vp(x, p):
    if x == 0:
        return -1
    k = 0
    while x % p == 0:
        x //= p
        k += 1
    return k


def depth_at(pairs, p, r, maxdepth=4):
    vals = {n: vp(x, p) for n, x in pairs if n % p == r}
    if len(vals) < 20 or min(vals.values()) < 1:
        return 0
    best = 1
    frontier = [(1, r)]
    while frontier:
        k, res = frontier.pop()
        mod = p ** (k + 1)
        for t in range(p):
            sub = res + t * p ** k
            sv = {n: v for n, v in vals.items() if n % mod == sub}
            if len(sv) >= 5 and min(sv.values()) >= k + 1:
                best = max(best, k + 1)
                frontier.append((k + 1, sub))
    return best


def best_depth(aid):
    pairs = bfile(aid)
    if not pairs:
        return 0
    best = 0
    for p in PRIMES:
        for r in range(p):
            cls = [(n, x) for n, x in pairs if n % p == r]
            if len(cls) < 20:
                continue
            if all(x % p == 0 for n, x in cls):
                best = max(best, depth_at(pairs, p, r))
    return best


def main() -> int:
    con = sqlite3.connect(f"file:{ROOT.joinpath('oeis.db').as_posix()}?mode=ro", uri=True)
    dep = {}
    for x in json.load(open(ROOT / "reports" / "congruence_depth.json", encoding="utf-8")):
        a = x["aid"]
        dep[a] = max(dep.get(a, 0), x["depth"])
    src = {a for a, d in dep.items() if d >= 2}
    print("deep sequences:", len(src))
    rel = defaultdict(set)
    for a, b, k in con.execute("select aid, dst, kind from numeric_relation"):
        if a in src and b not in dep:
            rel[a].add((b, k))
    partners = {}
    for a, s in rel.items():
        for b, k in s:
            partners.setdefault(b, k)
    print("partner sequences to test:", len(partners))
    res = {}
    for i, (b, k) in enumerate(partners.items()):
        res[b] = (best_depth(b), k)
        if (i + 1) % 500 == 0:
            print("  tested", i + 1, flush=True)
    byk = defaultdict(list)
    for b, (d, k) in res.items():
        byk[k].append(d)
    print("\npartner depth distribution by relation kind:")
    for k, ds in sorted(byk.items()):
        c = Counter(ds)
        print(f"  {k}: n={len(ds)} depth>=1 {sum(1 for d in ds if d>=1)} "
              f"depth>=2 {sum(1 for d in ds if d>=2)}  dist={dict(sorted(c.items()))}")
    out = {b: {"depth": d, "kind": k} for b, (d, k) in res.items()}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
