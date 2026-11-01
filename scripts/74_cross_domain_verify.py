import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
con = sqlite3.connect("file:" + (ROOT/"oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
pairs = json.load(open("reports/cross_domain.json", encoding="utf-8"))
print("pairs:", len(pairs))
_cache = {}
def terms(aid, limit=1200):
    if aid in _cache: return _cache[aid]
    f = DATA/"files"/("A"+aid[1:4])/f"b{aid[1:]}.txt"
    d = {}
    if f.exists():
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line=line.strip()
            if not line or line.startswith("#"): continue
            q=line.split()
            if len(q)>=2:
                try: d[int(q[0])]=int(q[1])
                except ValueError: pass
            if len(d)>=limit: break
    _cache[aid]=d or None
    return _cache[aid]
strong = []
for p in pairs:
    a,b = p["a"],p["b"]
    na, nb = names.get(a,"").lower(), names.get(b,"").lower()
    if "duplicate" in na or "duplicate" in nb or "same as" in na or "same as" in nb:
        continue
    if " mod " in na or " mod " in nb:
        continue
    ta, tb = terms(a), terms(b)
    if not ta or not tb: continue
    common = [n for n in ta if n in tb]
    if len(common) < 100: continue
    if all(ta[n] == tb[n] for n in common):
        strong.append({"a":a,"b":b,"ca":p["ca"],"cb":p["cb"],"n":len(common)})
print("strong cross-domain identities:", len(strong))
from collections import Counter
print("by cluster pair:", Counter((x["ca"],x["cb"]) for x in strong).most_common(10))
for x in sorted(strong, key=lambda y:-y["n"])[:15]:
    print(f"  {x['a']}[{x['ca']}] = {x['b']}[{x['cb']}] n={x['n']}")
    print(f"     {names.get(x['a'],'')[:62]}")
    print(f"     {names.get(x['b'],'')[:62]}")
json.dump(strong, open("reports/cross_domain_strong.json","w"), indent=1)
print("saved")
