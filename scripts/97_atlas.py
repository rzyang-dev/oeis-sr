#!/usr/bin/env python3
"""Build full DFAs (states, transitions, outputs) with hold-out validation."""
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
OUT = ROOT / "reports" / "atlas930.json"


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
    out = {0: d[0]}
    q = deque([(0, 0)])
    trans = {}
    conflict = False
    while q:
        e, r = q.popleft()
        sid = ids[key_of(d, e, r)]
        for digit in (0, 1):
            if e >= EMAX:
                trans[(sid, digit)] = None
                continue
            rr = r + digit * (1 << e)
            kk = key_of(d, e + 1, rr)
            if kk is None:
                trans[(sid, digit)] = None
                continue
            if kk not in ids:
                if len(ids) >= MAXS:
                    return None
                ids[kk] = len(ids)
                out[ids[kk]] = d.get(rr)
                q.append((e + 1, rr))
            trans[(sid, digit)] = ids[kk]
            if out.get(ids[kk]) != d.get(rr):
                conflict = True
    n = len(ids)
    dfa = {
        "n": n,
        "out": [out[i] for i in range(n)],
        "trans": [[trans.get((i, 0)) if trans.get((i, 0)) is not None else -1,
                   trans.get((i, 1)) if trans.get((i, 1)) is not None else -1]
                  for i in range(n)],
        "complete": all(v is not None for v in trans.values()),
        "conflict": conflict,
    }
    return dfa


def predict(dfa, n):
    s = 0
    for ch in reversed(bin(n)[2:]):
        b = 1 if ch == "1" else 0
        s = dfa["trans"][s][b]
        if s < 0:
            return None
    return dfa["out"][s]


def main() -> int:
    ids = json.load(open(ROOT / "reports" / "auto_all930.json", encoding="utf-8"))
    print("candidates:", len(ids))
    atlas = []
    for aid in ids:
        d = bfile(aid)
        if not d:
            continue
        ks = sorted(d)
        best = None
        for m in (0, 1, 2):
            dd = {k - m: v for k, v in d.items()}
            dfa = build(dd)
            if dfa and dfa["complete"] and not dfa["conflict"]:
                best = (m, dfa)
                break
        if not best:
            continue
        m, dfa = best
        total = ok = 0
        for n in ks:
            nn = n - m
            if nn < 0:
                continue
            v = predict(dfa, nn)
            total += 1
            if v == d[n]:
                ok += 1
        atlas.append({"aid": aid, "shift": m, "states": dfa["n"],
                      "val_total": total, "val_ok": ok,
                      "trans": dfa["trans"], "out": dfa["out"]})
        print(f"  {aid} states={dfa['n']} val={ok}/{total}", flush=True)
    good = [a for a in atlas if a["val_total"] > 100 and a["val_ok"] == a["val_total"]]
    print(f"atlas entries: {len(atlas)}, perfect hold-out: {len(good)}")
    json.dump(atlas, open(OUT, "w"))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())