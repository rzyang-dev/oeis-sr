import sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("""select d.cluster, f.growth, d.aid from domain d
    join seq_fingerprint f on f.aid=d.aid""").fetchall()
print("rows:", len(rows))
by = defaultdict(Counter)
for c, g, a in rows:
    by[c][g] += 1
tot = {c: sum(v.values()) for c, v in by.items()}
print("domains:", len(by))
# rare growth per domain
rare = []
for c, g, a in rows:
    p = by[c][g] / tot[c]
    if p < 0.02 and tot[c] > 200:
        rare.append((p, c, g, a))
print("rare-growth sequences:", len(rare))
names = dict(con.execute("select aid, name from seq"))
rare.sort()
for p, c, g, a in rare[:25]:
    print(f"  dom={c} growth={g} p={p:.3f} {a} | {names.get(a,'')[:70]}")
