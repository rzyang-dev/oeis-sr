#!/usr/bin/env python3
"""Predict the construction category from term statistics alone.

If this works, the routing signal becomes usable for sequences that are not in
OEIS (no name, no formula) -- only their numbers.

Also measures how much routing degrades when the category is predicted rather
than looked up.

    python scripts/36_predict_construction.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "construction_prediction.json"

GROWTH = ["exponential", "polynomial", "factorial", "other", "super", "zero"]


def feats(r):
    (growth, degree, base, periodic, nterms, zeros, signs, digits) = r
    x = [1.0 if growth == g else 0.0 for g in GROWTH]
    x.append(min(max(degree or 0.0, -5.0), 20.0) / 10.0)
    x.append(min(max(base or 0.0, -5.0), 30.0) / 10.0)
    x.append(1.0 if (periodic or 0) > 0 else 0.0)
    x.append(math.log1p(nterms or 0) / 5.0)
    x.append(1.0 if (zeros or 0) > 0 else 0.0)
    x.append(1.0 if (signs or 0) > 0 else 0.0)
    x.append(math.log1p(digits or 0) / 5.0)
    return x


def softmax(z):
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select f.aid, c.category, f.growth, f.degree, f.log2_base,
        f.periodic, f.n_terms, f.zeros, f.sign_changes, f.max_digits
        from seq_fingerprint f join construction c on c.aid = f.aid""").fetchall()
    print("rows:", len(rows))
    cats = [c for c, n in Counter(r[1] for r in rows).most_common() if n >= 300]
    idx = {c: i for i, c in enumerate(cats)}
    rows = [r for r in rows if r[1] in idx]
    print("categories kept:", len(cats), " rows:", len(rows))
    X = np.array([feats(r[2:]) for r in rows], dtype=float)
    y = np.array([idx[r[1]] for r in rows])
    ids = np.array([int(r[0][1:]) for r in rows])
    tr = (ids % 10) < 7
    te = ~tr
    mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
    Xs = (X - mu) / sd
    Xtr, ytr, Xte, yte = Xs[tr], y[tr], Xs[te], y[te]
    C = len(cats)
    rng = np.random.default_rng(0)
    W = np.zeros((X.shape[1], C)); b = np.zeros(C)
    lr, l2, bs = 0.3, 1e-4, 512
    for epoch in range(60):
        perm = rng.permutation(len(Xtr))
        for s in range(0, len(perm), bs):
            j = perm[s:s+bs]
            p = softmax(Xtr[j] @ W + b)
            Y = np.zeros((len(j), C)); Y[np.arange(len(j)), ytr[j]] = 1.0
            g = (p - Y) / len(j)
            W -= lr * (Xtr[j].T @ g + l2 * W)
            b -= lr * g.sum(0)
    pte = softmax(Xte @ W + b)
    top1 = (pte.argmax(1) == yte).mean()
    top3 = np.mean([yte[i] in np.argsort(-pte[i])[:3] for i in range(len(yte))])
    maj = Counter(yte).most_common(1)[0][1] / len(yte)
    print(f"test n={len(yte)}  majority={maj:.3f}  top1={top1:.3f}  top3={top3:.3f}")

    per = Counter((cats[a], cats[p]) for a, p in zip(yte, pte.argmax(1)))
    print("\nmost confused (true -> predicted):")
    for (a, pb), n in per.most_common(10):
        if a != pb:
            print(f"  {a:18} -> {pb:18} {n}")
    print("\nper-category recall (>=300 test):")
    for c, n in Counter(yte).most_common(8):
        if n < 100: continue
        rec = np.mean([pte[i].argmax() == yte[i] for i in range(len(yte)) if yte[i] == c])
        print(f"  {cats[c]:18} n={n:<5} recall={rec:.2f}")


    # ---- routing with predicted vs true construction ----
    FIXED = ["poly","bm","pre(1,1)","pre(2,1)","pre(1,2)","pre(2,2)","pre(3,1)","pre(1,3)",
             "pre(2,3)","pre(3,2)","pre(4,1)","pre(1,4)","pre_high(5,1)","pre_high(6,1)",
             "pre_high(3,3)","pre_high(4,2)","pre_high(2,4)","pre_high(1,5)"]
    te_idx = np.where(te)[0]
    pred_cat = {}
    for j, i in enumerate(te_idx):
        pred_cat[rows[i][0]] = cats[int(pte[j].argmax())]
    hs = con.execute("""select s.aid, s.method, f.growth, c.category from hard_solved s
        left join seq_fingerprint f on f.aid=s.aid
        left join construction c on c.aid=s.aid where s.method<>''""").fetchall()
    glob = Counter(m for aid, m, g, c in hs if int(aid[1:]) % 10 < 7)
    bucket = defaultdict(Counter)
    for aid, m, g, c in hs:
        if int(aid[1:]) % 10 < 7:
            bucket[(g, c)][m] += 1
    global_order = [m for m, _ in glob.most_common()]

    def order_for(g, c):
        cnt = bucket.get((g, c))
        if cnt and sum(cnt.values()) >= 20:
            return sorted(cnt, key=lambda m: (-cnt[m], -glob[m]))
        return global_order

    res = {"global": [], "true": [], "predicted": []}
    for aid, m, g, c in hs:
        if int(aid[1:]) % 10 < 7 or m not in FIXED:
            continue
        res["global"].append(global_order.index(m) + 1)
        o = order_for(g, c)
        res["true"].append(o.index(m) + 1 if m in o else len(o))
        pc = pred_cat.get(aid)
        if pc is not None:
            o2 = order_for(g, pc)
            res["predicted"].append(o2.index(m) + 1 if m in o2 else len(o2))
    print("\nrouting on hard test targets:")
    for k, v in res.items():
        if v:
            print(f"  {k:9} n={len(v):<4} mean attempts {sum(v)/len(v):.2f}  "
                  f"top1 {100*sum(1 for x in v if x==1)/len(v):.1f}%")
    out = json.loads(OUT.read_text(encoding="utf-8"))
    out["routing"] = {k: round(sum(v)/len(v), 2) for k, v in res.items() if v}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")

    OUT.write_text(json.dumps({"test_n": int(len(yte)), "majority": round(float(maj), 3),
                               "top1": round(float(top1), 3), "top3": round(float(top3), 3),
                               "cats": cats}, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())