#!/usr/bin/env python3
"""Kernel growth test: automatic sequences have a saturating p-kernel.

For each level e, count distinct windows of a(p^e n + r) mod p.
Automatic  -> the count saturates (few new windows at each level).
Non-automatic -> the count keeps growing ~ p^e.

    python scripts/46_kernel_growth.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "kernel_growth.json"
W = 10
MAXE = 4


def bfile(aid, limit=6000):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists():
        return None
    v = {}
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        v[int(q[0])] = int(q[1])
                    except ValueError:
                        pass
                if len(v) >= limit:
                    break
    except OSError:
        return None
    return v or None


def windows_at(d, p, e):
    mod = p ** e
    seen = set()
    for r in range(mod):
        w = []
        for k in range(W):
            x = d.get(r + k * mod)
            if x is None:
                w = None
                break
            w.append(x % p)
        if w is not None:
            seen.add(tuple(w))
    return len(seen)


def main() -> int:
    depth = {}
    for x in json.load(open(ROOT / "reports" / "congruence_depth.json", encoding="utf-8")):
        if x["depth"] >= 3:
            if x["aid"] not in depth or x["depth"] > depth[x["aid"]]["depth"]:
                depth[x["aid"]] = x
    print("depth>=3 sequences:", len(depth))

    out = []
    for aid, x in depth.items():
        d = bfile(aid)
        if not d:
            continue
        p = x["p"]
        L = max(d)
        emax = 0
        for e in range(1, MAXE + 1):
            if W * (p ** e) <= L + 1:
                emax = e
        if emax < 2:
            continue
        sizes = [windows_at(d, p, e) for e in range(emax + 1)]
        out.append({"aid": aid, "p": p, "depth": x["depth"], "sizes": sizes,
                    "emax": emax})

    # classify: saturating if the last level adds < 1.5x the previous
    sat = 0
    grow = 0
    for o in out:
        s_prev = o["sizes"][-2]
        s_last = o["sizes"][-1]
        o["growth"] = s_last / max(1, s_prev)
        if o["growth"] < 1.5:
            sat += 1
        else:
            grow += 1
    print("tested:", len(out), " saturating:", sat, " growing:", grow)
    print("median growth ratio:", sorted(o["growth"] for o in out)[len(out)//2])
    print("\nsaturating examples (automatic-like):")
    for o in [x for x in out if x["growth"] < 1.2][:8]:
        print("  ", o["aid"], o["p"], o["sizes"])
    print("\ngrowing examples (non-automatic):")
    for o in sorted([x for x in out if x["growth"] > 3], key=lambda x: -x["growth"])[:8]:
        print("  ", o["aid"], o["p"], o["sizes"])
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())