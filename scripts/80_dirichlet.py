#!/usr/bin/env python3
"""Mine Dirichlet convolutions: a = b * c, verified against b-files.

    python scripts/80_dirichlet.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "dirichlet.json"


def terms(aid, limit=400):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    d = {}
    if f.exists():
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
            d = {}
    return d or None


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return ds


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, text from formula").fetchall()
    pat = re.compile(r"A(\d{6})\(d\)\s*\*\s*A\((\d{6})\)\(n/d\)|A(\d{6})\(n/d\)\s*\*\s*A(\d{6})\(d\)")
    cands = []
    for aid, t in rows:
        if "d|n" not in t and "d divides n" not in t:
            continue
        for m in pat.finditer(t):
            g = m.groups()
            if g[0]:
                cands.append((aid, "A" + g[0], "A" + g[1]))
            else:
                cands.append((aid, "A" + g[3], "A" + g[2]))
    uniq = sorted(set(cands))
    print("candidate convolutions:", len(uniq))
    verified = []
    for t, b, c in uniq:
        dt, db, dc = terms(t), terms(b), terms(c)
        if not dt or not db or not dc:
            continue
        ok = 0
        tot = 0
        for n in range(1, 120):
            if n not in dt or not all(d in db and (n // d) in dc for d in divisors(n)):
                continue
            tot += 1
            if sum(db[d] * dc[n // d] for d in divisors(n)) == dt[n]:
                ok += 1
        if tot >= 30 and ok == tot:
            verified.append({"target": t, "b": b, "c": c, "n": tot})
    print("verified a = b * c:", len(verified))
    names = dict(con.execute("select aid, name from seq"))
    dom = dict(con.execute("select aid, cluster from domain"))
    text = defaultdict(list)
    for aid, tt in con.execute("select aid, text from stmt"):
        text[aid].append(tt)
    cross = []
    for v in verified:
        ds = {dom.get(x, -1) for x in (v["target"], v["b"], v["c"])}
        blob = " ".join(text.get(v["target"], []))
        documented = v["b"] in blob and v["c"] in blob
        if len(ds) >= 2 and not documented:
            cross.append(v)
    print("cross-domain & undocumented:", len(cross))
    for v in cross[:20]:
        print(f"  {v['target']} = {v['b']} * {v['c']}  n={v['n']}")
        print(f"     {names.get(v['target'],'')[:60]}")
        print(f"     {names.get(v['b'],'')[:60]}")
        print(f"     {names.get(v['c'],'')[:60]}")
    OUT.write_text(json.dumps({"all": verified, "cross": cross}, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
