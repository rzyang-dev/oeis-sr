import json, sys
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
con = sqlite3.connect("file:" + (ROOT/"oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
res = json.load(open(ROOT/"reports"/"automata.json", encoding="utf-8"))
def bfile(aid, limit=3000):
    f = DATA/"files"/("A"+aid[1:4])/f"b{aid[1:]}.txt"
    if not f.exists(): return None
    d = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: d[int(q[0])]=int(q[1])
            except ValueError: pass
        if len(d)>=limit: break
    return d or None
ok = [r for r in res if r["closed"]]
solid = []
for r in ok:
    d = bfile(r["aid"])
    if not d: continue
    v = list(d.values())
    z = sum(1 for x in v if x == 0)/len(v)
    if z > 0.3: continue
    solid.append(r)
print("closed:", len(ok), " non-sparse:", len(solid))
print("states dist:", Counter(x["states"] for x in solid).most_common(10))
for r in sorted(solid, key=lambda x: -x["states"])[:15]:
    print(f"  {r['aid']} states={r['states']} | {names.get(r['aid'],'')[:64]}")
json.dump(solid, open(ROOT/"reports"/"automata_solid.json","w"), indent=1)
