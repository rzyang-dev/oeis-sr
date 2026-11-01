#!/usr/bin/env python3
"""Census of p-automatic sequences in OEIS.

A sequence is p-automatic iff its p-kernel is finite. We approximate the kernel
by hashing windows of a(p^e n + r) for e=0..6.

    python scripts/87_automatic_census.py --shard k --of n
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
W = 8
MAXE = 6


def bfile(aid, limit=1200):
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


def kernel_size(d, p):
    """number of distinct windows of a(p^e n + r) for e<=MAXE"""
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
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select distinct aid from attachment where name like 'b%.txt' and aid in (select aid from seq)")]
    aids.sort()
    if limit:
        aids = aids[:limit]
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "sequences", len(aids), flush=True)
    out = ROOT / "reports" / f"auto_{shard:02d}.jsonl"
    n = 0
    small = 0
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            d = bfile(aid)
            if not d or len(d) < 300:
                continue
            n += 1
            rec = {"aid": aid}
            for p in (2, 3):
                k, counts = kernel_size(d, p)
                rec[f"k{p}"] = k
                rec[f"c{p}"] = counts
                if k <= 40:
                    small += 1
            fh.write(json.dumps(rec) + chr(10))
            if (i + 1) % 5000 == 0:
                print("  ", i + 1, "processed", n, "small", small, flush=True)
    print("done", {"tested": n, "small_kernel": small}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
