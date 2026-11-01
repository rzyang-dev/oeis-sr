#!/usr/bin/env python3
"""Proper hold-out: build the DFA on the first half, predict the second half."""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
W = 16
EMAX = 9
MAXS = 400


def bfile(aid, limit=20000):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    d = {}
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
        return None
    return d or None


def key_of(d, e, r):
    step = 1 << e
    vals = []
    for n in range(W):
        v = d.get(r + step * n)
        if v is None:
            return None
        vals.append(v)
    return tuple(vals)


def build(d):
    k0 = key_of(d, 0, 0)
    if k0 is None:
        return None
    ids = {k0: 0}
    out = {0: d.get(0)}
    q = deque([(0, 0)])
    trans = {}
    while q:
        e, r = q.popleft()
        s = ids[key_of(d, e, r)]
        for digit in (0, 1):
            if e >= EMAX:
                trans[(s, digit)] = None
                continue
            rr = r + digit * (1 << e)
            kk = key_of(d, e + 1, rr)
            if kk is None:
                trans[(s, digit)] = None
                continue
            if kk not in ids:
                if len(ids) >= MAXS:
                    return None
                ids[kk] = len(ids)
                q.append((e + 1, rr))
            trans[(s, digit)] = ids[kk]
    return {"n": len(ids),
            "out": [out.get(i) for i in range(len(ids))],
            "trans": [[trans.get((i, d)) if trans.get((i, d)) is not None else -1
                       for d in (0, 1)] for i in range(len(ids))]}


def predict(dfa, n):
    s = 0
    for ch in reversed(bin(n)[2:]):
        s = dfa["trans"][s][int(ch)]
        if s < 0:
            return None
    return dfa["out"][s]


def main() -> int:
    ids = json.load(open(ROOT / "reports" / "auto_all930.json", encoding="utf-8"))
    print("candidates:", len(ids))
    rows = []
    for aid in ids:
        d = bfile(aid)
        if not d or len(d) < 400:
            continue
        ks = sorted(d)
        half = ks[len(ks) // 2]
        dtrain = {n: v for n, v in d.items() if n <= half}
        dfa = None
        for m in (0, 1, 2):
            dd = {k - m: v for k, v in dtrain.items()}
            cand = build(dd)
            if cand:
                dfa = (m, cand)
                break
        if not dfa:
            continue
        m, df = dfa
        defined = correct = 0
        for n in ks:
            nn = n - m
            if nn < 0 or n <= half:
                continue
            v = predict(df, nn)
            if v is None:
                continue
            defined += 1
            if v == d[n]:
                correct += 1
        rows.append({"aid": aid, "shift": m, "states": df["n"],
                     "defined": defined, "correct": correct})
        print(f"  {aid} states={df['n']} defined={defined} correct={correct}", flush=True)
    good = [r for r in rows if r["defined"] >= 100 and r["correct"] == r["defined"]]
    print(f"hold-out entries: {len(rows)}, perfect-on-defined: {len(good)}")
    tot_def = sum(r["defined"] for r in rows)
    tot_ok = sum(r["correct"] for r in rows)
    print(f"aggregate: {tot_ok}/{tot_def} = {tot_ok/max(tot_def,1):.4%}")
    json.dump(rows, open(ROOT / "reports" / "holdout.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
