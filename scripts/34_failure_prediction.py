#!/usr/bin/env python3
"""Predict which hard targets are worth attempting.

Features: growth fingerprint + construction category + basic term statistics.
Label: did any exact method solve it (hard_solved.method <> '')?

Trained on 70% of the hard set (by aid hash), evaluated on the other 30%.

    python scripts/34_failure_prediction.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "failure_prediction.json"
MODEL = ROOT / "reports" / "model.json"

GROWTH = ["exponential", "polynomial", "factorial", "other", "super", "zero"]
CONSTR = ["prime", "digit", "table", "expansion", "divisor", "partition",
          "floor_round", "counting", "permutation", "graph", "set_partition",
          "continued_fraction", "cyclotomic", "words", "path", "modular", "matrix",
          "arrangement", "lexicographic", "zeolite", "recurrence", "game",
          "moonshine", "automaton", "sum_convolution", "other"]


def build_features(row):
    aid, method, growth, category, degree, base, periodic, nterms, zeros, signs, digits = row
    x = []
    for g in GROWTH:
        x.append(1.0 if growth == g else 0.0)
    for c in CONSTR:
        x.append(1.0 if category == c else 0.0)
    x.append(min(max(degree or 0.0, -5.0), 20.0) / 10.0)
    x.append(min(max(base or 0.0, -5.0), 30.0) / 10.0)
    x.append(1.0 if (periodic or 0) > 0 else 0.0)
    x.append(math.log1p(nterms or 0) / 5.0)
    x.append(1.0 if (zeros or 0) > 0 else 0.0)
    x.append(1.0 if (signs or 0) > 0 else 0.0)
    x.append(math.log1p(digits or 0) / 5.0)
    return x


def auc(y, p):
    order = np.argsort(p)
    ranks = np.empty(len(p))
    ranks[order] = np.arange(1, len(p) + 1)
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return 0.5
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""
        select s.aid, coalesce(s.method,''), f.growth, c.category, f.degree,
               f.log2_base, f.periodic, f.n_terms, f.zeros, f.sign_changes, f.max_digits
        from hard_solved s
        left join seq_fingerprint f on f.aid = s.aid
        left join construction c on c.aid = s.aid""").fetchall()
    print("rows:", len(rows))
    X = np.array([build_features(r) for r in rows], dtype=float)
    y = np.array([1.0 if r[1] else 0.0 for r in rows])
    mask = np.array([r[0][1:].isdigit() for r in rows])
    X, y, rows = X[mask], y[mask], [r for r, m in zip(rows, mask) if m]
    ids = np.array([int(r[0][1:]) for r in rows])
    tr = (ids % 10) < 7
    te = ~tr
    mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
    Xs = (X - mu) / sd
    Xtr, ytr, Xte, yte = Xs[tr], y[tr], Xs[te], y[te]
    print(f"train {tr.sum()}  test {te.sum()}  positive rate {y.mean():.3f}")

    w = np.zeros(X.shape[1]); b = 0.0
    lr = 0.05
    for it in range(3000):
        z = Xtr @ w + b
        p = 1 / (1 + np.exp(-z))
        gw = Xtr.T @ (p - ytr) / len(ytr) + 1e-4 * w
        gb = (p - ytr).mean()
        w -= lr * gw; b -= lr * gb
    pte = 1 / (1 + np.exp(-(Xte @ w + b)))
    print(f"test AUC: {auc(yte, pte):.3f}")
    print(f"test accuracy @0.5: {((pte >= 0.5) == yte).mean():.3f}")

    # coverage / recall tradeoff
    order = np.argsort(-pte)
    total_pos = int(yte.sum())
    print(f"\ntest positives: {total_pos}")
    out = {"auc": round(float(auc(yte, pte)), 3), "test_n": int(te.sum()),
           "positives": total_pos, "coverage": []}
    for frac in (0.2, 0.3, 0.5, 0.7, 0.9):
        k = int(frac * len(pte))
        caught = int(yte[order[:k]].sum())
        prec = caught / k
        print(f"  attempt top {frac*100:>3.0f}% by score: precision {prec:.3f}  "
              f"recall {caught/total_pos:.3f}  (caught {caught}/{total_pos})")
        out["coverage"].append({"frac": frac, "precision": round(prec, 3),
                                "recall": round(caught / total_pos, 3)})


    # end-to-end: how much compute does skipping low-score targets save?
    FIXED_POS = ["poly","bm","pre(1,1)","pre(2,1)","pre(1,2)","pre(2,2)","pre(3,1)","pre(1,3)",
                 "pre(2,3)","pre(3,2)","pre(4,1)","pre(1,4)","pre_high(5,1)","pre_high(6,1)",
                 "pre_high(3,3)","pre_high(4,2)","pre_high(2,4)","pre_high(1,5)"]
    rows_te = [r for r, m in zip(rows, te) if m]
    base_total = skip_total = 0
    thr = float(np.median(pte))
    for r, pr in zip(rows_te, pte):
        m = r[1]
        pos = FIXED_POS.index(m) + 1 if m in FIXED_POS else len(FIXED_POS)
        base_total += pos
        if pr >= thr:
            skip_total += pos
    print(f"\nend-to-end attempts on test set: full {base_total}  "
          f"skip-bottom-half {skip_total}  saving {100*(1-skip_total/base_total):.1f}%")
    out["attempts_full"] = base_total
    out["attempts_skip_half"] = skip_total

    names = [f"growth={g}" for g in GROWTH] + [f"constr={c}" for c in CONSTR] + \
            ["degree", "log2_base", "periodic", "log_terms", "has_zeros", "sign_changes", "log_digits"]
    MODEL.write_text(json.dumps({
        "mu": mu.tolist(), "sd": sd.tolist(), "w": w.tolist(), "b": float(b),
        "growth": GROWTH, "constr": CONSTR,
        "features": [f"growth={g}" for g in GROWTH] + [f"constr={c}" for c in CONSTR] +
                    ["degree", "log2_base", "periodic", "log_terms", "has_zeros",
                     "sign_changes", "log_digits"]}, indent=1), encoding="utf-8")
    print("wrote", MODEL)


    coefs = sorted(zip(names, w), key=lambda kv: -abs(kv[1]))[:12]
    print("\nstrongest coefficients:")
    for n, v in coefs:
        print(f"  {n:26} {v:+.2f}")
    out["top_coefs"] = [{"name": n, "w": round(float(v), 3)} for n, v in coefs]
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())