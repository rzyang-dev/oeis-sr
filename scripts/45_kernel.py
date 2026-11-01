#!/usr/bin/env python3
"""p-kernel test: is a(n) mod p a p-automatic sequence?

Christol's theorem: a(n) mod p is p-automatic iff the generating function is
algebraic over F_p(x).  Automatic sequences have Lucas-type congruences, so a
small p-kernel means the congruence is explained by finite-automaton structure.

    python scripts/45_kernel.py --validate
    python scripts/45_kernel.py --full
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "kernel.json"
W = 8
MAXE = 3


def bfile(aid, limit=2500):
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


def kernel_size(d, p):
    windows = set()
    for e in range(MAXE + 1):
        mod = p ** e
        for r in range(mod):
            w = []
            for k in range(W):
                x = d.get(r + k * mod)
                if x is None:
                    w = None
                    break
                w.append(x % p)
            if w is not None:
                windows.add(tuple(w))
    return len(windows)


def main(argv):
    if "--validate" in argv:
        tests = [("A010060", 2, "Thue-Morse, should be automatic"),
                 ("A000120", 2, "binary weight, should be automatic"),
                 ("A000041", 5, "partition numbers, should NOT be automatic"),
                 ("A000594", 5, "Ramanujan tau, should NOT be automatic")]
        for aid, p, note in tests:
            d = bfile(aid)
            print(f"{aid} p={p}: kernel={kernel_size(d, p)}  ({note})")
        return 0

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
        k = kernel_size(d, x["p"])
        out.append({"aid": aid, "p": x["p"], "depth": x["depth"], "kernel": k,
                    "automatic": k <= 20})
    print("tested:", len(out))
    print("automatic (kernel<=20):", sum(1 for o in out if o["automatic"]))
    print("kernel size distribution:", Counter(min(o["kernel"] // 10 * 10, 150) for o in out).most_common(8))
    out.sort(key=lambda o: (o["automatic"], -o["depth"]))
    print("\nnon-automatic, deepest:")
    for o in out[:20]:
        if not o["automatic"]:
            print("  ", o)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
