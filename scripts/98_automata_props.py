#!/usr/bin/env python3
"""Use the DFA atlas to decide properties: value sets and zero density."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(r"C:\Users\ginger\Documents\oeis")


def density_zero(dfa, iters=4000):
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
    atlas = json.load(open(ROOT / "reports" / "atlas.json", encoding="utf-8"))
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    names = dict(con.execute("select aid, name from seq"))
    text = {}
    for aid, t in con.execute("select aid, text from stmt"):
        text.setdefault(aid, []).append(t)
    print("atlas:", len(atlas))
    rows = []
    for a in atlas:
        if a["val_total"] < 1000 or a["val_ok"] != a["val_total"]:
            continue
        dfa = {"n": a["states"], "out": a["out"], "trans": a["trans"]}
        outs = sorted(set(a["out"]))
        dz = density_zero(dfa)
        blob = " ".join(text.get(a["aid"], [])).lower()
        rows.append({"aid": a["aid"], "states": a["states"], "values": outs,
                     "zero_density": round(dz, 4),
                     "mentions_periodic": ("periodic" in blob or "period " in blob),
                     "name": names.get(a["aid"], "")[:70]})
    print("analyzed:", len(rows))
    print(f"{'aid':10} {'states':>6} {'values':>16} {'zdens':>7} periodic?")
    for r in sorted(rows, key=lambda x: x["zero_density"])[:12]:
        print(f"{r['aid']:10} {r['states']:>6} {str(r['values'])[:16]:>16} {r['zero_density']:>7} {r['mentions_periodic']}")
    print("...")
    for r in sorted(rows, key=lambda x: -x["zero_density"])[:8]:
        print(f"{r['aid']:10} {r['states']:>6} {str(r['values'])[:16]:>16} {r['zero_density']:>7} {r['mentions_periodic']}")
    json.dump(rows, open(ROOT / "reports" / "atlas_props.json", "w"), indent=1)
    print("wrote atlas_props.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
