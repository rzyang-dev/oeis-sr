#!/usr/bin/env python3
"""3-automatic census on long b-files (>=6000 terms)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
W = 8
MAXE = 6


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


def kernel(d, p=3):
    seen = set()
    counts = []
    for e in range(MAXE + 1):
        mod = p ** e
        sub = set()
        for r in range(mod):
            w = []
            for k in range(W):
                idx = r + k * mod
                if idx not in d:
                    w = None
                    break
                w.append(d[idx])
            if w is not None:
                sub.add(tuple(w))
        counts.append(len(sub))
        seen |= sub
    return len(seen), counts


def main(argv):
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    aids = sorted({r[0] for r in con.execute(
        "select distinct aid from attachment where name like 'b%.txt'") if r[0]})
    aids = aids[shard::of]
    print("shard", shard, "candidates", len(aids), flush=True)
    out = ROOT / "reports" / f"auto3_{shard:02d}.jsonl"
    tested = small = 0
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            d = bfile(aid)
            if not d or len(d) < 6000 or max(d) < W * 3 ** MAXE:
                continue
            tested += 1
            k, counts = kernel(d)
            fh.write(json.dumps({"aid": aid, "k3": k, "c3": counts}) + chr(10))
            if counts[-1] <= 30 and counts[-1] == counts[-2]:
                small += 1
            if (i + 1) % 3000 == 0:
                print("  ", i + 1, "tested", tested, "small", small, flush=True)
    print("done", {"tested": tested, "small": small}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))