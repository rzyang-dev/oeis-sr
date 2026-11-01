#!/usr/bin/env python3
"""Run the routed pipeline over the whole hard set, sharded.

    python scripts/37_routed_full.py --shard k --of n
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
T, K = 25, 30


def bfile(aid, limit=600):
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


def bm_capped(vals, k, maxorder=20):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        s = -sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0]
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
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    order_for, _ = conditional_orders(con)
    cats = dict(con.execute("select aid, category from construction"))
    aids = [r[0] for r in con.execute("select aid from hard_bench where hard=1")]
    aids.sort()
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "targets", len(aids), flush=True)

    out = ROOT / "reports" / f"routed_{shard:02d}.jsonl"
    n_solved = n_skip = 0
    attempts = 0
    t0 = time.perf_counter()
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            v = bfile(aid)
            if not v or len(v) < T + K:
                continue
            vals, truth = v[:T], v[T:T + K]
            fp = fingerprint(v)
            cat = cats.get(aid, "other")
            try:
                p = predict(growth=fp["growth"], category=cat, degree=fp["degree"],
                            log2_base=fp["log2_base"], periodic=fp["periodic"],
                            n_terms=len(v), zeros=fp["zeros"], signs=fp["sign_changes"],
                            digits=fp["digits"])
            except Exception:
                p = 0.0
            rec = {"aid": aid, "p": round(float(p), 4), "skipped": 0, "attempts": 0, "method": ""}
            if p < 0.25:
                rec["skipped"] = 1
                n_skip += 1
            else:
                for m in order_for(fp["growth"], cat):
                    rec["attempts"] += 1
                    attempts += 1
                    if run(m, vals, truth):
                        rec["method"] = m
                        n_solved += 1
                        break
            fh.write(json.dumps(rec) + "\n")
            if (i + 1) % 500 == 0:
                print(f"  {i+1}/{len(aids)} solved {n_solved} skipped {n_skip}", flush=True)
    print("done", {"solved": n_solved, "skipped": n_skip, "attempts": attempts,
                   "seconds": round(time.perf_counter() - t0, 1)}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
