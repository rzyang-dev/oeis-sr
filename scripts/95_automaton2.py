#!/usr/bin/env python3
"""Build 2-automata via (e, r) states, reading values on demand."""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
W = 10
EMAX = 12
MAXS = 300


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


def build(d, m=0):
    d2 = {k - m: v for k, v in d.items()} if m else d
    k0 = key_of(d2, 0, 0)
    if k0 is None:
        return 0, False
    ids = {k0: 0}
    q = deque([(0, 0)])
    trans = {}
    while q:
        e, r = q.popleft()
        sid = ids[key_of(d2, e, r)]
        if e >= EMAX:
            trans[(sid, 0)] = None
            trans[(sid, 1)] = None
            continue
        for digit in (0, 1):
            rr = r + digit * (1 << e)
            kk = key_of(d2, e + 1, rr)
            if kk is None:
                trans[(sid, digit)] = None
                continue
            if kk not in ids:
                if len(ids) >= MAXS:
                    return len(ids), False
                ids[kk] = len(ids)
                q.append((e + 1, rr))
            trans[(sid, digit)] = ids[kk]
    closed = all(v is not None for v in trans.values())
    return len(ids), closed


def main() -> int:
    ids = json.load(open(ROOT / "reports" / "auto_surprise.json", encoding="utf-8"))
    print("candidates:", len(ids))
    results = []
    for aid in ids:
        d = bfile(aid)
        if not d:
            continue
        best = None
        for m in (0, 1, 2):
            n, closed = build(d, m)
            if n > 0:
                best = (m, n, closed)
                break
        results.append({"aid": aid, "shift": best[0] if best else None,
                        "states": best[1] if best else 0,
                        "closed": best[2] if best else False})
    ok = [r for r in results if r["closed"]]
    print("built:", len(results), " closed:", len(ok))
    results.sort(key=lambda x: x["states"])
    for r in results[:30]:
        print(f"  {r['aid']} shift={r['shift']} states={r['states']} closed={r['closed']}")
    json.dump(results, open(ROOT / "reports" / "automata.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
