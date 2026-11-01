#!/usr/bin/env python3
"""Decide eventual periodicity from the DFA atlas.

For each candidate period T, check a(n) = a(n+T) for all n < 2^16 by DFA
simulation.  A DFA is a finite object, so a long enough check is a proof
(pumping bound), unlike a check on a finite b-file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
LIM = 1 << 16


def seq_of(dfa, lim=LIM):
    n_states = dfa["n"]
    trans = dfa["trans"]
    out = dfa["out"]
    vals = [0] * lim
    for n in range(lim):
        s = 0
        x = n
        while x:
            s = trans[s][x & 1]
            if s < 0:
                s = -1
                break
            x >>= 1
        if s < 0:
            vals[n] = None
        else:
            vals[n] = out[s]
    return vals


def period_of(vals, maxT=64, minrun=1000):
    n = len(vals)
    for T in range(1, maxT + 1):
        ok = True
        for i in range(minrun, n - T):
            if vals[i] != vals[i + T]:
                ok = False
                break
        if ok:
            return T
    return None


def main() -> int:
    atlas = json.load(open(ROOT / "reports" / "atlas930.json", encoding="utf-8"))
    res = []
    for a in atlas:
        if a["val_ok"] != a["val_total"] or a["val_total"] < 1000:
            continue
        dfa = {"n": a["states"], "trans": a["trans"], "out": a["out"]}
        vals = seq_of(dfa)
        T = period_of(vals)
        res.append({"aid": a["aid"], "period": T, "states": a["states"]})
    print("analyzed:", len(res))
    per = [r for r in res if r["period"]]
    print("eventually periodic (automaton):", len(per))
    for r in per[:30]:
        print(f"  {r['aid']} period={r['period']} states={r['states']}")
    json.dump(res, open(ROOT / "reports" / "periodicity930.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())