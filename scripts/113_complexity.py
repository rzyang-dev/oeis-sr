#!/usr/bin/env python3
"""Factor complexity of the atlas sequences, computed from b-files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
KMAX = 12
LIM = 4000


def bfile(aid, limit=LIM):
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


def complexity(v, kmax=KMAX):
    res = []
    for k in range(1, kmax + 1):
        s = set()
        for i in range(len(v) - k + 1):
            s.add(tuple(v[i:i + k]))
        res.append(len(s))
    return res


def main() -> int:
    atlas = json.load(open(ROOT / "reports" / "atlas930.json", encoding="utf-8"))
    per = {r["aid"]: r["period"] for r in json.load(open(ROOT / "reports" / "periodicity930.json", encoding="utf-8"))}
    rows = []
    for a in atlas:
        if a["val_ok"] != a["val_total"] or a["val_total"] < 1000:
            continue
        d = bfile(a["aid"])
        if not d or len(d) < 500:
            continue
        v = [d[k] for k in sorted(d)]
        c = complexity(v)
        slope = (c[-1] - c[-4]) / (KMAX - (KMAX - 3)) if len(c) >= 4 else None
        rows.append({"aid": a["aid"], "period": per.get(a["aid"]),
                     "states": a["states"], "complexity": c,
                     "slope": round(slope, 3) if slope is not None else None})
    print("computed:", len(rows))
    aper = [r for r in rows if not r["period"]]
    per_ = [r for r in rows if r["period"]]
    print("aperiodic:", len(aper), " periodic:", len(per_))
    print("\naperiodic slope distribution:")
    from collections import Counter
    print(Counter(r["slope"] for r in aper).most_common(10))
    print("\nlowest complexity aperiodic:")
    for r in sorted(aper, key=lambda x: x["complexity"][-1])[:12]:
        print(f"  {r['aid']} states={r['states']} c={r['complexity']} slope={r['slope']}")
    json.dump(rows, open(ROOT / "reports" / "complexity.json", "w"), indent=1)
    print("wrote complexity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
