import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
dom = dict(con.execute("select aid, cluster from domain"))
d = json.load(open("reports/dirichlet.json", encoding="utf-8"))
allv = d["all"]
print("verified convolutions:", len(allv))
c = Counter()
for v in allv:
    ds = (dom.get(v["target"], -1), dom.get(v["b"], -1), dom.get(v["c"], -1))
    c[len(set(ds))] += 1
print("distinct-domain count:", dict(c))
cross = [v for v in allv if len({dom.get(x,-1) for x in (v["target"],v["b"],v["c"])}) == 3]
print("3-domain convolutions:", len(cross))
for v in cross[:12]:
    print(f"  {v['target']} = {v['b']} * {v['c']} n={v['n']}")
    print(f"     {names.get(v['target'],'')[:58]}")
    print(f"     {names.get(v['b'],'')[:58]}")
    print(f"     {names.get(v['c'],'')[:58]}")
