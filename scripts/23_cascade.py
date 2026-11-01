#!/usr/bin/env python3
"""Sequence-operator cascade: solve a hard target via a parent sequence.

If a(n) is a prefix sum / difference / affine function of another sequence b,
and b itself can be solved from its own terms, then a is solved too.

    python scripts/23_cascade.py [--limit N]
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

from oeisdb.solvers import solve, solve_validated

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "cascade.json"
T, K = 20, 30

_cache = {}
def bfile(aid, limit=4000):
    if aid in _cache:
        return _cache[aid]
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
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
            d = None
    _cache[aid] = d
    return d


def longest_run(ns):
    run, prev, best = [], None, []
    for n in ns:
        if prev is not None and n != prev + 1:
            if len(run) > len(best):
                best = run
            run = []
        run.append(n)
        prev = n
    return run if len(run) > len(best) else best


def parent_values(aid, cutoff, need_to):
    """Known parent values <= cutoff plus predictions up to need_to."""
    d = bfile(aid)
    if not d:
        return None
    known = sorted(n for n in d if n <= cutoff)
    if len(known) < 20:
        return None
    last = known[-25:]
    vals = [d[n] for n in last]
    need = need_to - last[-1]
    if need <= 0:
        return {n: d[n] for n in d if n <= need_to}
    pred, how = solve_validated(vals, need)
    if pred is None:
        return None
    out = {n: d[n] for n in d if n <= cutoff}
    for i, v in enumerate(pred):
        n = last[-1] + 1 + i
        out[n] = v.numerator if isinstance(v, Fraction) and v.denominator == 1 else v
    return out


def main(argv: list[str]) -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("select aid from hard_bench where hard=1").fetchall()
    aids = [r[0] for r in rows]
    if "--limit" in argv:
        import random
        random.seed(5)
        aids = random.sample(aids, int(argv[argv.index("--limit") + 1]))
    print("hard targets:", len(aids))

    # candidate derivations
    deriv = {}
    for a, b, kind in con.execute("select aid, dst, kind from numeric_relation"):
        deriv.setdefault(a, []).append((b, kind))
        if kind != "prefix":            # prefix is directional
            deriv.setdefault(b, []).append((a, kind))
    for aid, dst, text in con.execute(
            "select aid, dst, text from definition"):
        low = text.lower()
        if "partial sum" in low:
            deriv.setdefault(aid, []).append((dst, "prefix"))
        elif "first difference" in low or "differences of" in low:
            deriv.setdefault(aid, []).append((dst, "diff"))

    solved = 0
    by_op = {}
    examples = []
    tried = 0
    for aid in aids:
        if aid not in deriv:
            continue
        d = bfile(aid)
        if not d:
            continue
        run = longest_run(sorted(d))
        if len(run) < T + K:
            continue
        n0 = run[0]
        train = [d[n] for n in run[:T]]
        truth = [d[n] for n in run[T:T + K]]
        cutoff = run[T - 1]
        need_to = run[T + K - 1]
        tried += 1
        ok = False
        for b, kind in deriv[aid][:4]:
            pv = parent_values(b, cutoff, need_to)
            if pv is None:
                continue
            try:
                if kind == "equal":
                    pred = [pv[n] for n in range(cutoff + 1, cutoff + K + 1)]
                elif kind == "affine":
                    pairs = [(d[n], pv[n]) for n in run[:T] if n in pv]
                    if len(pairs) < 10:
                        continue
                    (a1, b1), (a2, b2) = pairs[0], pairs[-1]
                    if b1 == b2:
                        continue
                    an, ad = a1 - a2, b1 - b2
                    bn = a1 * ad - an * b1
                    if any(x * ad != an * y + bn for x, y in pairs):
                        continue
                    pred = [(an * pv[n] + bn) / ad for n in range(cutoff + 1, cutoff + K + 1)]
                elif kind == "prefix":
                    pred = []
                    cur = train[-1]
                    for n in range(cutoff + 1, cutoff + K + 1):
                        cur = cur + pv[n]
                        pred.append(cur)
                else:   # diff
                    pred = [pv[n] - pv[n - 1] for n in range(cutoff + 1, cutoff + K + 1)]
            except KeyError:
                continue
            if pred == truth:
                ok = True
                by_op[kind] = by_op.get(kind, 0) + 1
                if len(examples) < 12:
                    examples.append({"aid": aid, "parent": b, "op": kind})
                break
        if ok:
            solved += 1

    print(f"targets with derivations: {tried}   solved via cascade: {solved} "
          f"({100*solved/max(1,tried):.1f}%)")
    print("by operator:", by_op)
    for e in examples:
        print("  ", e)
    OUT.write_text(json.dumps({"hard": len(aids), "with_derivation": tried,
                               "solved": solved, "by_op": by_op,
                               "examples": examples}, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
