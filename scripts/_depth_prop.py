import json, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
dep = {}
for x in json.load(open("reports/congruence_depth.json", encoding="utf-8")):
    a = x["aid"]
    if a not in dep or x["depth"] > dep[a]["depth"]:
        dep[a] = {"depth": x["depth"], "p": x["p"]}
print("sequences with depth>=2:", len(dep))
rels = con.execute("select aid, dst, kind from numeric_relation").fetchall()
print("numeric relations:", len(rels))
print("kinds:", Counter(k for _, _, k in rels))
pairs = [(a, b, k) for a, b, k in rels if a in dep and b in dep]
print("pairs where both have depth:", len(pairs))
print("by kind:", Counter(k for _, _, k in pairs))
byk = defaultdict(lambda: [0, 0, 0])
for a, b, k in pairs:
    da, db = dep[a]["depth"], dep[b]["depth"]
    byk[k][0] += 1
    if da == db: byk[k][1] += 1
    if abs(da - db) <= 1: byk[k][2] += 1
for k, (n, eq, close) in byk.items():
    print(f"  {k}: n={n}  depth equal {100*eq/n:.0f}%  within 1 {100*close/n:.0f}%")
# baseline: random pairs of depth>=2 sequences
import random
random.seed(0)
keys = list(dep)
eq = 0
for _ in range(5000):
    a, b = random.sample(keys, 2)
    if dep[a]["depth"] == dep[b]["depth"]: eq += 1
print(f"baseline (random pairs): depth equal {100*eq/5000:.0f}%")
