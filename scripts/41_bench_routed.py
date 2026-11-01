#!/usr/bin/env python3
"""Apply the routed pipeline to the v0 formula benchmark.

The benchmark is easy (BM solves 96%), so the point is that routing must not
lose solutions while cutting attempts.

    python scripts/41_bench_routed.py
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.routed import predict, conditional_orders, fingerprint
from oeisdb.solvers import poly_predict, berlekamp_massey, precursive_guess, precursive_predict

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "bench_routed.json"
T, K = 20, 30
FIXED = ["poly","bm","pre(1,1)","pre(2,1)","pre(1,2)","pre(2,2)","pre(3,1)","pre(1,3)",
         "pre(2,3)","pre(3,2)","pre(4,1)","pre(1,4)","pre_high(5,1)","pre_high(6,1)",
         "pre_high(3,3)","pre_high(4,2)","pre_high(2,4)","pre_high(1,5)"]


def bfile(aid, limit=200):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    v = []
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        v.append(int(q[1]))
                    except ValueError:
                        pass
                if len(v) >= limit:
                    break
    except OSError:
        return None
    return v or None


def run(method, vals, truth):
    try:
        if method == "poly":
            return poly_predict(vals, K, maxdeg=12) == truth
        if method == "bm":
            C, L = berlekamp_massey([Fraction(x) for x in vals])
            if L == 0 or L > 20 or len(C) < L + 1:
                return False
            out = [Fraction(x) for x in vals]
            for _ in range(K):
                n = len(out)
                s = -sum(C[i]*out[n-i] for i in range(1, L+1)) / C[0]
                if abs(s.numerator).bit_length() > 5000:
                    return False
                out.append(s)
            return out[-K:] == [Fraction(x) for x in truth]
        r, d = method.split("(")[1].rstrip(")").split(",")
        r, d = int(r), int(d)
        coef = precursive_guess(vals, r, d)
        if coef is None:
            return False
        p = precursive_predict(vals, coef, r, d, K)
        return p is not None and p == [Fraction(x) for x in truth]
    except Exception:
        return False


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    order_for, _ = conditional_orders(con)
    cats = dict(con.execute("select aid, category from construction"))
    aids = [r[0] for r in con.execute("select aid from bench")]
    res = {"fixed": {"solved": 0, "attempts": 0, "time": 0.0},
           "routed": {"solved": 0, "attempts": 0, "time": 0.0, "skipped": 0}}
    n = 0
    for aid in aids:
        v = bfile(aid)
        if not v or len(v) < T + K:
            continue
        n += 1
        vals, truth = v[:T], v[T:T+K]
        t0 = time.perf_counter()
        ok = False
        for m in FIXED:
            res["fixed"]["attempts"] += 1
            if run(m, vals, truth):
                ok = True
                break
        res["fixed"]["time"] += time.perf_counter() - t0
        res["fixed"]["solved"] += int(ok)

        fp = fingerprint(v)
        p = predict(growth=fp["growth"], category=cats.get(aid, "other"),
                    degree=fp["degree"], log2_base=fp["log2_base"], periodic=fp["periodic"],
                    n_terms=len(v), zeros=fp["zeros"], signs=fp["sign_changes"], digits=fp["digits"])
        t0 = time.perf_counter()
        if p < 0.25:
            res["routed"]["skipped"] += 1
        else:
            for m in order_for(fp["growth"], cats.get(aid, "other")):
                res["routed"]["attempts"] += 1
                if run(m, vals, truth):
                    res["routed"]["solved"] += 1
                    break
        res["routed"]["time"] += time.perf_counter() - t0


    # cheap-first policy: always try poly/bm, then route the expensive models
    res["cheap_first"] = {"solved": 0, "attempts": 0, "time": 0.0, "skipped": 0}
    n2 = 0
    for aid in aids:
        v = bfile(aid)
        if not v or len(v) < T + K:
            continue
        n2 += 1
        vals, truth = v[:T], v[T:T+K]
        fp = fingerprint(v)
        p = predict(growth=fp["growth"], category=cats.get(aid, "other"),
                    degree=fp["degree"], log2_base=fp["log2_base"], periodic=fp["periodic"],
                    n_terms=len(v), zeros=fp["zeros"], signs=fp["sign_changes"], digits=fp["digits"])
        t0 = time.perf_counter()
        ok = False
        for m in ("poly", "bm"):
            res["cheap_first"]["attempts"] += 1
            if run(m, vals, truth):
                ok = True
                break
        if not ok and p >= 0.25:
            for m in order_for(fp["growth"], cats.get(aid, "other")):
                if m in ("poly", "bm"):
                    continue
                res["cheap_first"]["attempts"] += 1
                if run(m, vals, truth):
                    ok = True
                    break
        elif not ok:
            res["cheap_first"]["skipped"] += 1
        res["cheap_first"]["time"] += time.perf_counter() - t0
        res["cheap_first"]["solved"] += int(ok)

    print(json.dumps(res, indent=1))
    print(f"evaluated {n}")
    for k in ("fixed", "routed", "cheap_first"):
        r = res[k]
        print(f"{k:7} solved {r['solved']}  attempts {r['attempts']}  time {r['time']:.1f}s")
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())