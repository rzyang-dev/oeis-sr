import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
con = sqlite3.connect("file:" + (ROOT/"oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
ids = json.load(open(ROOT/"reports"/"auto_undoc.json", encoding="utf-8"))
print("candidates:", len(ids))
def bfile(aid, limit=600):
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
keep = []
stats = {"no_bfile":0,"sparse":0,"ok":0}
for aid in ids:
    d = bfile(aid)
    if not d: stats["no_bfile"] += 1; continue
    vals = list(d.values())
    z = sum(1 for x in vals if x == 0)/len(vals)
    if z > 0.3 or len(set(vals)) <= 3:
        stats["sparse"] += 1; continue
    stats["ok"] += 1
    keep.append(aid)
print(stats)
print("strong candidates:", len(keep))
for aid in keep[:25]:
    print(f"  {aid} | {names.get(aid,'')[:70]}")
json.dump(keep, open(ROOT/"reports"/"auto_strong.json","w"), indent=1)
