#!/usr/bin/env python3
"""Conditional method routing: P(method | growth, construction), measured out of sample.

    python scripts/33_conditional_routing.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "routing.json"

FIXED = ["poly","bm","pre(1,1)","pre(2,1)","pre(1,2)","pre(2,2)","pre(3,1)","pre(1,3)",
         "pre(2,3)","pre(3,2)","pre(4,1)","pre(1,4)","pre_high(5,1)","pre_high(6,1)",
         "pre_high(3,3)","pre_high(4,2)","pre_high(2,4)","pre_high(1,5)"]
COST = {m: (1 if m in ("poly", "bm") else 10) for m in FIXED}


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("""select s.aid, s.method, f.growth, c.category
        from hard_solved s
        left join seq_fingerprint f on f.aid = s.aid
        left join construction c on c.aid = s.aid
        where s.method <> ''""").fetchall()
    print("solved hard targets:", len(rows))

    train = [r for r in rows if int(r[0][1:]) % 10 < 7]
    test = [r for r in rows if int(r[0][1:]) % 10 >= 7]
    glob = Counter(m for _, m, _, _ in train)
    bucket = defaultdict(Counter)
    for _, m, g, c in train:
        bucket[(g, c)][m] += 1

    def order_for(g, c):
        cnt = bucket.get((g, c))
        if cnt and sum(cnt.values()) >= 20:
            return sorted(cnt, key=lambda m: (-cnt[m], -glob[m]))
        return [m for m, _ in glob.most_common()]

    global_order = [m for m, _ in glob.most_common()]
    res = {"fixed": [], "global": [], "conditional": []}
    costs = {"fixed": [], "global": [], "conditional": []}
    covered = 0
    for _, m, g, c in test:
        if m not in FIXED:
            continue
        res["fixed"].append(FIXED.index(m) + 1)
        pos = global_order.index(m) + 1
        res["global"].append(pos)
        o = order_for(g, c)
        if (g, c) in bucket and sum(bucket[(g, c)].values()) >= 20:
            covered += 1
        res["conditional"].append(o.index(m) + 1 if m in o else len(o))
        for name, order in (("fixed", FIXED), ("global", global_order), ("conditional", o)):
            k = order.index(m) + 1 if m in order else len(order)
            costs[name].append(sum(COST[x] for x in order[:k]))

    n = len(res["fixed"])
    print(f"test targets: {n}   with a well-populated bucket: {covered}")
    out = {}
    for name in ("fixed", "global", "conditional"):
        mean_att = sum(res[name]) / n
        mean_cost = sum(costs[name]) / n
        top1 = 100 * sum(1 for x in res[name] if x == 1) / n
        top3 = 100 * sum(1 for x in res[name] if x <= 3) / n
        print(f"  {name:11} mean attempts {mean_att:5.2f}  cost {mean_cost:6.1f}  "
              f"first {top1:4.1f}%  top3 {top3:5.1f}%")
        out[name] = {"mean_attempts": round(mean_att, 2), "mean_cost": round(mean_cost, 1),
                     "top1": round(top1, 1), "top3": round(top3, 1)}
    out["test_n"] = n
    out["covered"] = covered
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
