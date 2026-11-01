#!/usr/bin/env python3
"""Subsequence relations: a(n) = b(2n) or b(2n+1), found by hashing."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "subsequence.json"
K = 10


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    seqs = {}
    for aid, terms in con.execute("select aid, terms from seq"):
        if not terms:
            continue
        try:
            v = [int(x) for x in terms.split(",")[:80]]
        except ValueError:
            continue
        if len(v) >= K:
            seqs[aid] = v
    print("sequences:", len(seqs))
    head = defaultdict(list)
    for aid, v in seqs.items():
        head[tuple(v[:K])].append(aid)
    print("head keys:", len(head))

    hits = []
    for aid, v in seqs.items():
        if len(v) < 2 * K + 4:
            continue
        for off in (0, 1):
            sub = tuple(v[off + 2 * i] for i in range(K) if off + 2 * i < len(v))
            if len(sub) < K:
                continue
            for cand in head.get(sub, []):
                if cand == aid:
                    continue
                w = seqs[cand]
                m = min(len(v) // 2, len(w))
                good = 0
                for i in range(m):
                    if v[off + 2 * i] == w[i]:
                        good += 1
                    else:
                        break
                if good >= 2 * K:
                    hits.append((aid, cand, off, good))
    print("hits:", len(hits))
    names = dict(con.execute("select aid, name from seq"))
    seen = set()
    for a, b, off, g in hits[:30]:
        if (a, b, off) in seen:
            continue
        seen.add((a, b, off))
        print(f"  {a}(n) = {b}(2n{'+1' if off else ''})  ok={g}")
        print(f"     A: {names.get(a,'')[:58]}")
        print(f"     B: {names.get(b,'')[:58]}")
    OUT.write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
