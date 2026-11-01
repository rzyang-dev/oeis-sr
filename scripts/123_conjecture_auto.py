#!/usr/bin/env python3
"""Decide equality of two automatic sequences via the product automaton."""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")


def load():
    rows = json.load(open(ROOT / "reports" / "atlas930.json", encoding="utf-8"))
    return {r["aid"]: r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}


def product_mismatch(A, B, start_digits=0):
    """Look for n whose output differs.  start_digits=1 skips n=0."""
    seen = set()
    q = deque()
    # states are (sa, sb); the digit string read so far is the LSB-first binary of n
    init = (0, 0)
    q.append((init, 0))  # (state pair, number of digits read)
    seen.add((init, 0))
    while q:
        (sa, sb), depth = q.popleft()
        if depth >= start_digits and A["out"][sa] != B["out"][sb]:
            # reconstruct n
            return True, depth
        for d in (0, 1):
            ta, tb = A["trans"][sa][d], B["trans"][sb][d]
            if ta < 0 or tb < 0:
                continue
            st = ((ta, tb), depth + 1)
            if st not in seen:
                seen.add(st)
                q.append(st)
    return False, None


def main() -> int:
    m = load()
    pairs = [("A267442", "A043545", 1)]
    for a, b, sd in pairs:
        if a not in m or b not in m:
            print(f"{a} or {b} not in atlas")
            continue
        bad, depth = product_mismatch(m[a], m[b], sd)
        print(f"{a} = {b} (n>={sd})? mismatch={bad} depth={depth}")
        print("  states:", m[a]["states"], m[b]["states"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
