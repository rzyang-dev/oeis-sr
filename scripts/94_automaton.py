#!/usr/bin/env python3
"""Construct 2-automata for candidate automatic sequences.

States are 8-windows of subsequences a(r + 2^e n); transitions are even/odd
decimations.  A closed, finite state set is a candidate DFA.

    python scripts/94_automaton.py
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
W = 8
MAXS = 200


def bfile(aid, limit=6000):
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


def build(d):
    """BFS over (e, r); returns (n_states, closed, transitions)."""
    start = []
    for k in range(2 * W):
        if k in d:
            start.append(d[k])
        else:
            return 0, False, {}
    ids = {}
    windows = {}

    def key(win):
        return tuple(win[:W])

    q = deque()
    q.append((0, 0, start))
    ids[key(start)] = 0
    windows[0] = start
    trans = {}
    incomplete = 0
    while q:
        e, r, win = q.popleft()
        sid = ids[key(win)]
        for digit in (0, 1):
            child = [win[digit + 2 * k] for k in range(len(win) // 2)]
            if len(child) < 2 * W:
                incomplete += 1
                trans[(sid, digit)] = None
                continue
            kk = key(child)
            if kk not in ids:
                if len(ids) >= MAXS:
                    return len(ids), False, trans
                ids[kk] = len(ids)
                windows[ids[kk]] = child
                q.append((e + 1, r + digit * (2 ** e), child))
            trans[(sid, digit)] = ids[kk]
    closed = all(v is not None for v in trans.values())
    return len(ids), closed, trans


def main() -> int:
    ids = json.load(open(ROOT / "reports" / "auto_surprise.json", encoding="utf-8"))
    print("candidates:", len(ids))
    results = []
    for aid in ids:
        d = bfile(aid)
        if not d:
            continue
        for m in (0, 1):
            dd = {k - m: v for k, v in d.items()}
            n, closed, trans = build(dd)
            if n > 0:
                results.append({"aid": aid, "shift": m, "states": n, "closed": closed})
                break
        else:
            results.append({"aid": aid, "shift": None, "states": 0, "closed": False})
    closed_ok = [r for r in results if r["closed"]]
    print("built:", len(results), " closed:", len(closed_ok))
    results.sort(key=lambda x: x["states"])
    for r in results[:30]:
        print(f"  {r['aid']} states={r['states']} closed={r['closed']}")
    json.dump(results, open(ROOT / "reports" / "automata.json", "w"), indent=1)
    print("wrote automata.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())