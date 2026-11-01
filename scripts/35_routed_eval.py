#!/usr/bin/env python3
"""End-to-end comparison: fixed solver order vs predicted+routed order.

Runs the real solvers (not a simulation) on held-out hard targets and measures
wall-clock time, attempts and solved counts.

    python scripts/35_routed_eval.py [--limit 100]
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.routed import predict, conditional_orders
from oeisdb.solvers import poly_predict, berlekamp_massey, precursive_guess, precursive_predict

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "routed_eval.json"
T, K = 25, 30

FIXED = ["poly","bm","pre(1,1)","pre(2,1)","pre(1,2)","pre(2,2)","pre(3,1)","pre(1,3)",
         "pre(2,3)","pre(3,2)","pre(4,1)","pre(1,4)","pre_high(5,1)","pre_high(6,1)",
         "pre_high(3,3)","pre_high(4,2)","pre_high(2,4)","pre_high(1,5)"]
SKIP_COST = len(FIXED)

_cache = {}
def bfile(aid, limit=600):
    if aid in _cache:
        return _cache[aid]
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    v = None
    if p.exists():
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
            v = None
    _cache[aid] = v
    return v


def fingerprint(v):
    n = len(v)
    if n < 10:
        return None
    nz = [(i, abs(x)) for i, x in enumerate(v) if x != 0]
    zeros = n - len(nz)
    signs = sum(1 for i in range(1, n) if (v[i] > 0) != (v[i-1] > 0) and v[i] and v[i-1])
    digits = max(len(str(abs(x))) for x in v)
    if len(nz) < 8:
        return {"growth": "zero", "degree": 0.0, "log2_base": 0.0, "periodic": 0,
                "zeros": zeros, "sign_changes": signs, "digits": digits}
    tail = nz[-60:]
    xs = [math.log(i + 2) for i, _ in tail]
    ys = [math.log(a) for _, a in tail]
    mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
    den = sum((x-mx)**2 for x in xs) or 1.0
    slope = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / den
    lr = [math.log2(tail[k+1][1]) - math.log2(tail[k][1]) for k in range(len(tail)-20, len(tail)-1)
          if 0 <= k < len(tail)-1]
    lr_mean = sum(lr)/len(lr) if lr else 0.0
    lr_last = lr[-1] if lr else 0.0
    growth = "other"
    if lr and abs(lr_last) < 0.05 and abs(slope) < 20:
        growth = "polynomial"
    elif lr and 0.05 <= lr_mean < 20 and abs(lr_last - lr_mean) < 0.5:
        growth = "exponential"
    elif lr and lr_last > math.log2(max(2, n)) * 0.5:
        growth = "factorial"
    elif lr and lr_mean >= 20:
        growth = "super"
    per = 0
    m = min(120, n)
    seg = v[-m:]
    for p in range(1, 13):
        if all(seg[i] == seg[i-p] for i in range(p, len(seg))):
            per = p
            break
    return {"growth": growth, "degree": round(slope, 2), "log2_base": round(lr_mean, 3),
            "periodic": per, "zeros": zeros, "sign_changes": signs, "digits": digits}


def bm_capped(vals, k, maxorder=20):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i]*out[n-i] for i in range(1, L+1)) / C[0]
        if abs(s.numerator).bit_length() > 5000:
            return None
        out.append(s)
    return out[-k:]


def run(method, vals, truth):
    try:
        if method == "poly":
            return poly_predict(vals, K, maxdeg=12) == truth
        if method == "bm":
            p = bm_capped(vals, K)
            return p is not None and [Fraction(x) for x in truth] == p
        r, d = method.split("(")[1].rstrip(")").split(",")
        r, d = int(r), int(d)
        coef = precursive_guess(vals, r, d)
        if coef is None:
            return False
        p = precursive_predict(vals, coef, r, d, K)
        return p is not None and [Fraction(x) for x in truth] == p
    except Exception:
        return False


def main(argv):
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 100
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    order_for, global_order = conditional_orders(con)
    cats = dict(con.execute("select aid, category from construction"))
    aids = [r[0] for r in con.execute("select aid from hard_bench where hard=1")]
    random.seed(77)
    random.shuffle(aids)
    picked = []
    for aid in aids:
        if int(aid[1:]) % 10 < 7:
            continue
        v = bfile(aid)
        if not v or len(v) < T + K:
            continue
        picked.append(aid)
        if len(picked) >= limit:
            break
    print("targets:", len(picked), flush=True)

    res = {"fixed": {"solved": 0, "attempts": 0, "time": 0.0},
           "routed": {"solved": 0, "attempts": 0, "time": 0.0, "skipped": 0}}
    for aid in picked:
        v = bfile(aid)
        vals, truth = v[:T], v[T:T+K]
        # fixed order, run every method until success
        t0 = time.perf_counter()
        ok = False
        for i, m in enumerate(FIXED):
            res["fixed"]["attempts"] += 1
            if run(m, vals, truth):
                ok = True
                break
        res["fixed"]["time"] += time.perf_counter() - t0
        res["fixed"]["solved"] += int(ok)

        # routed: predict, skip low score, conditional order
        fp = fingerprint(v)
        p = predict(growth=fp["growth"], category=cats.get(aid, "other"),
                    degree=fp["degree"], log2_base=fp["log2_base"],
                    periodic=fp["periodic"], n_terms=len(v), zeros=fp["zeros"],
                    signs=fp["sign_changes"], digits=fp["digits"])
        t0 = time.perf_counter()
        if p < 0.25:
            res["routed"]["skipped"] += 1
            res["routed"]["attempts"] += 0
        else:
            order = order_for(fp["growth"], cats.get(aid, "other"))
            for m in order:
                res["routed"]["attempts"] += 1
                if run(m, vals, truth):
                    res["routed"]["solved"] += 1
                    break
        res["routed"]["time"] += time.perf_counter() - t0

    print(json.dumps(res, indent=1))
    for k in ("fixed", "routed"):
        r = res[k]
        print(f"{k:7} solved {r['solved']}  attempts {r['attempts']}  time {r['time']:.1f}s")
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
