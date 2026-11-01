#!/usr/bin/env python3
"""Minimal EML baseline: fit the paper's level-2 master formula to OEIS terms.

The master formula has 14 real parameters:

  F(x) = eml(a1+b1*x+g1*E1, a2+b2*x+g2*E2)
  E1   = eml(a3+b3*x, a4+b4*x)
  E2   = eml(a5+b5*x, a6+b6*x)

Fit with Adam on the first 20 terms (finite-difference gradients), snap each
(alpha, beta, gamma) triple to the nearest vertex, then check the next 30.

    python scripts/20_eml_baseline.py
"""
from __future__ import annotations

import json
import random
import sqlite3
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "eml_baseline.json"


def eml(u, v):
    u = np.clip(u.real, -50, 50) + 1j * u.imag
    v = np.where(np.abs(v) < 1e-12, 1e-12 + 0j, v)
    return np.exp(u) - np.log(v)


def master(x, p):
    a1, b1, g1, a2, b2, g2, a3, b3, a4, b4, a5, b5, a6, b6 = p
    e1 = eml(a3 + b3 * x, a4 + b4 * x)
    e2 = eml(a5 + b5 * x, a6 + b6 * x)
    return eml(a1 + b1 * x + g1 * e1, a2 + b2 * x + g2 * e2)


def loss(x, y, p):
    f = master(x, p)
    d = f - y
    if not np.all(np.isfinite(d)):
        return 1e12
    return float(np.mean(np.abs(d) ** 2))


def fit(x, y, steps=1200, lr=0.02, seed=0):
    rng = np.random.default_rng(seed)
    p = rng.normal(0, 0.3, 14)
    m = np.zeros(14); v = np.zeros(14)
    b1, b2, eps = 0.9, 0.999, 1e-8
    best_p, best_l = p.copy(), loss(x, y, p)
    for t in range(1, steps + 1):
        g = np.zeros(14)
        for i in range(14):
            pp = p.copy(); pp[i] += 1e-6
            pm = p.copy(); pm[i] -= 1e-6
            g[i] = (loss(x, y, pp) - loss(x, y, pm)) / 2e-6
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        p = p - lr * (m / (1 - b1**t)) / (np.sqrt(v / (1 - b2**t)) + eps)
        if t % 50 == 0:
            l = loss(x, y, p)
            if l < best_l:
                best_l, best_p = l, p.copy()
    return best_p, best_l


def snap(p):
    q = p.copy()
    for i in (0, 3, 6):          # (alpha,beta,gamma) triples at 0,3,... but layout differs
        pass
    # triples: (a1,b1,g1)=0,1,2 ; (a2,b2,g2)=3,4,5
    for base in (0, 3):
        trip = q[base:base+3]
        d = [abs(trip - np.array(v)).sum() for v in ((1,0,0), (0,1,0), (0,0,1))]
        q[base:base+3] = ((1,0,0), (0,1,0), (0,0,1))[int(np.argmin(d))]
    # inner nodes keep continuous values (they only need alpha+beta*x)
    return q


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""
        select b.aid, b.expr, s.offset1, s.terms from bench b join seq s on s.aid=b.aid
        where b.tier='easy' and b.ops<=4 order by b.ops limit 40""").fetchall()
    p_known = np.zeros(14); p_known[3] = 1.0
    sanity = np.allclose(master(np.arange(5.0), p_known).real, 1.0)
    print("sanity check (hand-set params give F=1):", bool(sanity))

    random.seed(1)
    picked = rows[:15]

    res = []
    for aid, expr, off, terms in picked:
        vals = [int(x) for x in terms.split(",")]
        if len(vals) < 50: continue
        if max(abs(v) for v in vals[:50]) > 10**9: continue
        n = np.arange(off, off + 20, dtype=float)
        y = np.array(vals[:20], dtype=complex)
        p, l = fit(n, y, seed=hash(aid) % 1000)
        q = snap(p)
        with np.errstate(all="ignore"):
            pred = master(np.arange(off + 20, off + 50, dtype=float), q)
        truth = np.array(vals[20:50], dtype=complex)
        ok = np.allclose(pred.real, truth.real, atol=1e-6) and np.allclose(pred.imag, 0, atol=1e-6)
        res.append({"aid": aid, "expr": expr, "train_loss": l, "snap_ok": bool(ok)})
        print(f"  {aid:9} loss={l:12.3e}  snap={'OK' if ok else 'no'}  {expr[:60]}")

    print(f"\nEML level-2 exact recoveries: {sum(r['snap_ok'] for r in res)}/{len(res)}")
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
