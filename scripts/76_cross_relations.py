import sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
dom = dict(con.execute("select aid, cluster from domain"))
rows = con.execute("select target, b, c, op, terms from pointwise_decomposition").fetchall()
print("rows:", len(rows))
dist = Counter()
tri = []
for t, b, c, op, n in rows:
    ds = {dom.get(x, -1) for x in (t, b, c)}
    dist[len(ds)] += 1
    if len(ds) == 3 and n >= 60:
        tri.append((t, b, c, op, n, dom.get(t), dom.get(b), dom.get(c)))
print("distinct-domain count distribution:", dict(dist))
print("3-domain relations (>=60 terms):", len(tri))
for t, b, c, op, n, dt, db, dc in tri[:20]:
    sym = {"sum": "+", "diff": "-", "prod": "*"}[op]
    print(f"  {t}[{dt}] = {b}[{db}] {sym} {c}[{dc}]  n={n}")
    print(f"     T: {names.get(t,'')[:64]}")
    print(f"     B: {names.get(b,'')[:64]}")
    print(f"     C: {names.get(c,'')[:64]}")
