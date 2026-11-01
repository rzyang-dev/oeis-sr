#!/usr/bin/env python3
"""Exact-algebra baseline on the formula benchmark.

Given the first 20 terms of a sequence, predict the next 30 with

  poly   finite differences -> exact polynomial of degree <= 6
  bm     Berlekamp-Massey over Q -> linear recurrence of order <= 8
  either poly first, bm as fallback

and compare against the b-file values.

    python scripts/17_baseline.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "baseline.json"
T, K = 20, 30

_cache = {}
def bfile(aid, limit=4000):
    if aid in _cache: return _cache[aid]
    p = DATA / "files" / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    q = line.split()
                    if len(q) >= 2:
                        try: d[int(q[0])] = int(q[1])
                        except ValueError: pass
                    if len(d) >= limit: break
        except OSError: d = None
    _cache[aid] = d
    return d

def poly_predict(vals, k, maxdeg=12):
    cols = [list(vals)]
    for deg in range(1, maxdeg + 1):
        prev = cols[-1]
        if len(prev) < 2: return None
        cols.append([prev[i+1]-prev[i] for i in range(len(prev)-1)])
        row = cols[-1]
        if len(row) >= 2 and len(set(row)) == 1:
            out = []
            for _ in range(k):
                cols[-1].append(cols[-1][-1])
                for j in range(len(cols)-2, -1, -1):
                    cols[j].append(cols[j][-1] + cols[j+1][-1])
                out.append(cols[0][-1])
            return out
    return None

def berlekamp_massey(s):
    C = [Fraction(1)]; B = [Fraction(1)]
    L = 0; m = 1; b = Fraction(1)
    for n in range(len(s)):
        d = sum(C[i]*s[n-i] for i in range(min(L, n)+1))
        if d == 0:
            m += 1; continue
        T = C[:]
        coef = d / b
        if len(C) < len(B) + m:
            C += [Fraction(0)] * (len(B) + m - len(C))
        for j, bj in enumerate(B):
            C[j+m] -= coef * bj
        if 2*L <= n:
            L = n + 1 - L; B = T; b = d; m = 1
        else:
            m += 1
    return C, L

def bm_predict(vals, k, maxorder=12):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L+1: return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i]*out[n-i] for i in range(1, L+1))
        s = s / C[0]
        out.append(s)
    return out[-k:]

def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("select aid, tier, split from bench").fetchall()
    res = defaultdict(Counter)
    detail = []
    n_used = 0
    for aid, tier, split in rows:
        d = bfile(aid)
        if not d: continue
        ns = sorted(d)
        # need a contiguous run of T+K values
        run = []
        best = []
        prev = None
        for n in ns:
            if prev is not None and n != prev + 1:
                if len(run) > len(best): best = run
                run = []
            run.append(n); prev = n
        if len(run) > len(best): best = run
        if len(best) < T + K: continue
        vals = [d[n] for n in best[:T]]
        truth = [d[n] for n in best[T:T+K]]
        n_used += 1
        for name, pred in (("poly", poly_predict(vals, K)),
                           ("bm", bm_predict(vals, K))):
            if pred is None:
                res[(name, "skip")][split] += 1; continue
            ok = pred == truth
            res[(name, "ok" if ok else "fail")][split] += 1
            res[(name, "ok" if ok else "fail")]["t:" + tier] += 1
        pp = poly_predict(vals, K)
        bp = bm_predict(vals, K)
        p = pp if pp is not None else bp
        ok = p == truth if p is not None else False
        res[("best", "ok" if ok else "fail")][split] += 1
        res[("best", "ok" if ok else "fail")]["t:" + tier] += 1
        detail.append((aid, int(pp is not None), int(bp is not None), int(ok)))

    con2 = sqlite3.connect(str(DB))
    con2.execute("DROP TABLE IF EXISTS bench_result")
    con2.execute("CREATE TABLE bench_result (aid TEXT PRIMARY KEY, poly_ok INTEGER, bm_ok INTEGER, solved INTEGER)")
    con2.executemany("INSERT INTO bench_result VALUES (?,?,?,?)", detail)
    con2.commit(); con2.close()

    print("sequences evaluated:", n_used)
    for name in ("poly", "bm", "best"):
        ok = sum(v for k, v in res[(name, "ok")].items() if not k.startswith("t:"))
        fa = sum(v for k, v in res[(name, "fail")].items() if not k.startswith("t:"))
        sk = sum(v for k, v in res[(name, "skip")].items() if not k.startswith("t:"))
        print(f"{name:5} ok={ok:>4} fail={fa:>4} skip={sk:>4}  success={100*ok/max(1,ok+fa):.1f}%")
    print("\nbest by split:", {s: dict(res[("best","ok")]) for s in ()})
    bysplit = {}
    for s in ("train", "val", "test"):
        ok = res[("best", "ok")][s]; fa = res[("best", "fail")][s]
        bysplit[s] = (ok, ok+fa)
    print("split accuracy:", {s: f"{100*o/max(1,t):.1f}% ({o}/{t})" for s, (o, t) in bysplit.items()})
    bytier = {}
    for s in ("easy", "medium", "hard"):
        ok = res[("best", "ok")]["t:" + s]; fa = res[("best", "fail")]["t:" + s]
        bytier[s] = (ok, ok+fa)
    print("tier accuracy:", {s: f"{100*o/max(1,t):.1f}% ({o}/{t})" for s, (o, t) in bytier.items()})
    OUT.write_text(json.dumps({"evaluated": n_used,
                               "by_split": bysplit, "by_tier": bytier}, indent=1))
    print("wrote", OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())