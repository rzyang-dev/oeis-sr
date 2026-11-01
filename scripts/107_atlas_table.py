#!/usr/bin/env python3
"""Full property table for the verified atlas + Cobham cross-check."""
from __future__ import annotations

import csv
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(r"C:\Users\ginger\Documents\oeis")


def density_zero(dfa, iters=3000):
    n = dfa["n"]
    v = [0.0] * n
    v[0] = 1.0
    for _ in range(iters):
        nv = [0.0] * n
        for s in range(n):
            if v[s] == 0.0:
                continue
            for d in (0, 1):
                t = dfa["trans"][s][d]
                if t >= 0:
                    nv[t] += v[s] * 0.5
        v = nv
    return sum(v[s] for s in range(n) if dfa["out"][s] == 0)


def main() -> int:
    atlas = json.load(open(ROOT / "reports" / "atlas930.json", encoding="utf-8"))
    per = {r["aid"]: r["period"] for r in json.load(open(ROOT / "reports" / "periodicity930.json", encoding="utf-8"))}
    cand3 = set(json.load(open(ROOT / "reports" / "auto3_cand.json", encoding="utf-8")))
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    names = dict(con.execute("select aid, name from seq"))
    rows = []
    for a in atlas:
        if a["val_ok"] != a["val_total"] or a["val_total"] < 1000:
            continue
        dfa = {"n": a["states"], "out": a["out"], "trans": a["trans"]}
        dz = density_zero(dfa)
        rows.append({
            "aid": a["aid"],
            "states": a["states"],
            "values": " ".join(map(str, sorted(set(a["out"])))),
            "zero_density": round(dz, 6),
            "zero_frac": str(Fraction(dz).limit_denominator(1000)),
            "period": per.get(a["aid"]),
            "in_3census": a["aid"] in cand3,
            "name": names.get(a["aid"], ""),
        })
    print("rows:", len(rows))
    both = [r for r in rows if r["in_3census"]]
    print("also in 3-census:", len(both))
    # Cobham: dual-automatic must be eventually periodic
    bad = [r for r in both if not r["period"]]
    print("Cobham violations (aperiodic but dual candidates):", len(bad))
    for r in bad[:10]:
        print(f"  {r['aid']} period={r['period']} | {r['name'][:60]}")
    with open(ROOT / "reports" / "atlas_table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote atlas_table.csv")
    from collections import Counter
    print("period distribution:", Counter(r["period"] for r in rows).most_common(10))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
