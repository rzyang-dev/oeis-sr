#!/usr/bin/env python3
"""Combinatorial template library: Bell / Catalan / Motzkin style recurrences.

Each template is verified on the observed terms and, if it holds, used to predict
the held-out ones.  These recurrences are common in combinatorics and are neither
C-finite nor P-recursive in the usual sense.

    python scripts/25_templates.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "templates.json"
T, K = 20, 30
_c = {}


def bfile(aid, limit=4000):
    if aid in _c:
        return _c[aid]
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
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
            d = None
    _c[aid] = d
    return d


def check_bell(a):
    for n in range(1, len(a) - 1):
        s = sum(math.comb(n, k) * a[k] for k in range(n + 1))
        if a[n + 1] != s:
            return False
    return True


def pred_bell(a, k):
    out = list(a)
    for _ in range(k):
        n = len(out) - 1
        out.append(sum(math.comb(n, j) * out[j] for j in range(n + 1)))
    return out[-k:]


def check_catalan_conv(a):
    for n in range(0, len(a) - 1):
        s = sum(a[i] * a[n - i] for i in range(n + 1))
        if a[n + 1] != s:
            return False
    return True


def pred_catalan_conv(a, k):
    out = list(a)
    for _ in range(k):
        n = len(out) - 1
        out.append(sum(out[i] * out[n - i] for i in range(n + 1)))
    return out[-k:]


def check_motzkin(a):
    for n in range(1, len(a) - 1):
        s = a[n] + sum(a[i] * a[n - 1 - i] for i in range(n))
        if a[n + 1] != s:
            return False
    return True


def pred_motzkin(a, k):
    out = list(a)
    for _ in range(k):
        n = len(out) - 1
        out.append(out[n] + sum(out[i] * out[n - 1 - i] for i in range(n)))
    return out[-k:]


def check_catalan_div(a):
    for n in range(1, len(a)):
        s = sum(a[i] * a[n - i] for i in range(n + 1))
        if s % (n + 1) or a[n] != s // (n + 1):
            return False
    return True


def pred_catalan_div(a, k):
    out = list(a)
    for _ in range(k):
        n = len(out)
        s = sum(out[i] * out[n - i] for i in range(n + 1))
        if s % (n + 1):
            return None
        out.append(s // (n + 1))
    return out[-k:]


TEMPLATES = [
    ("bell", check_bell, pred_bell),
    ("catalan_conv", check_catalan_conv, pred_catalan_conv),
    ("motzkin", check_motzkin, pred_motzkin),
]


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select aid from hard_bench where hard=1")]
    print("hard targets:", len(aids))

    hits = {}
    evaluated = 0
    for aid in aids:
        d = bfile(aid)
        if not d or 0 not in d:
            continue
        ns = sorted(n for n in d if n >= 0)
        # longest consecutive run starting at 0
        run = [0]
        for n in ns:
            if n == run[-1] + 1:
                run.append(n)
            elif n > run[-1] + 1:
                break
        if len(run) < T + K:
            continue
        a = [d[n] for n in run[:T]]
        truth = [d[n] for n in run[T:T + K]]
        evaluated += 1
        for name, check, pred in TEMPLATES:
            try:
                if not check(a):
                    continue
                p = pred(a, K)
            except (ValueError, ZeroDivisionError):
                continue
            if p == truth:
                hits.setdefault(name, []).append(aid)

    print("evaluated (offset 0, >=50 terms):", evaluated)
    total = sum(len(v) for v in hits.values())
    for name in ("bell", "catalan_conv", "motzkin", "catalan_div"):
        v = hits.get(name, [])
        print(f"  {name:14} {len(v):>4}  {v[:6]}")
    print("template hits:", total)
    json.dump({k: v for k, v in hits.items()}, open(OUT, "w"), indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
