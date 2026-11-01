#!/usr/bin/env python3
"""Minimize the atlas DFAs and group sequences with isomorphic automata."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(r"C:\Users\ginger\Documents\oeis")


def minimize(dfa):
    n = dfa["n"]
    out = dfa["out"]
    tr = dfa["trans"]
    part = [0] * n
    groups = defaultdict(list)
    for s in range(n):
        groups[out[s]].append(s)
    label = {}
    for i, (k, ss) in enumerate(sorted(groups.items(), key=lambda x: str(x[0]))):
        for s in ss:
            part[s] = i
    ncls = len(groups)
    while True:
        sig = {}
        for s in range(n):
            sig[s] = (part[s], part[tr[s][0]] if tr[s][0] >= 0 else -1,
                      part[tr[s][1]] if tr[s][1] >= 0 else -1)
        ids = {}
        newpart = [0] * n
        for s in range(n):
            k = sig[s]
            if k not in ids:
                ids[k] = len(ids)
            newpart[s] = ids[k]
        if len(ids) == ncls:
            part = newpart
            break
        part = newpart
        ncls = len(ids)
    # rebuild
    reps = {}
    for s in range(n):
        reps.setdefault(part[s], s)
    m = len(reps)
    start = part[0]
    # BFS canonical order
    order = [start]
    idx = {start: 0}
    q = 0
    new_tr = []
    new_out = []
    while q < len(order):
        c = order[q]
        q += 1
        s = reps[c]
        new_out.append(out[s])
        row = []
        for d in (0, 1):
            t = tr[s][d]
            if t < 0:
                row.append(-1)
                continue
            ct = part[t]
            if ct not in idx:
                idx[ct] = len(order)
                order.append(ct)
            row.append(idx[ct])
        new_tr.append(row)
    return {"n": m, "out": new_out, "trans": new_tr}


def canon(dfa):
    return json.dumps(dfa, sort_keys=True)


def main() -> int:
    atlas = json.load(open(ROOT / "reports" / "atlas930.json", encoding="utf-8"))
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    names = dict(con.execute("select aid, name from seq"))
    groups = defaultdict(list)
    sizes = []
    for a in atlas:
        if a["val_ok"] != a["val_total"] or a["val_total"] < 1000:
            continue
        dfa = {"n": a["states"], "out": a["out"], "trans": [list(x) for x in a["trans"]]}
        m = minimize(dfa)
        sizes.append((a["aid"], a["states"], m["n"]))
        groups[canon(m)].append(a["aid"])
    print("entries:", len(sizes))
    red = sum(1 for _, s, m in sizes if m < s)
    print("minimized strictly:", red)
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    print("isomorphism classes with >1 sequence:", len(multi))
    tot = sum(len(v) for v in multi.values())
    print("sequences in non-singleton classes:", tot)
    for k, v in sorted(multi.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  class size {len(v)}: {v[:6]}")
        for aid in v[:3]:
            print(f"     {aid}: {names.get(aid,'')[:60]}")
    json.dump({"classes": {k: v for k, v in multi.items()}, "sizes": sizes},
              open(ROOT / "reports" / "automata_classes.json", "w"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
