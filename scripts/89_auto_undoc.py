import json, sys, re
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
rows = json.load(open(ROOT + r"\reports\auto_all.json", encoding="utf-8"))
fp = {}
for aid, g, per in con.execute("select aid, growth, periodic from seq_fingerprint"):
    fp[aid] = (g, per)
names = dict(con.execute("select aid, name from seq"))
print("k2<=40 total:", sum(1 for r in rows if r["k2"] <= 40))
c = Counter()
nonper = []
for r in rows:
    if r["k2"] > 40: continue
    g, per = fp.get(r["aid"], (None, None))
    if per and per > 0:
        c["periodic"] += 1
    elif g == "polynomial":
        c["polynomial"] += 1
    else:
        c["other"] += 1
        nonper.append(r)
print(dict(c))
print("\nnon-periodic, non-polynomial 2-automatic candidates:", len(nonper))
# check mentions
text = {}
for aid, t in con.execute("select aid, text from stmt"):
    text.setdefault(aid, []).append(t)
doc = 0
undoc = []
for r in nonper:
    blob = " ".join(text.get(r["aid"], [])).lower()
    if "automatic" in blob or "2-regular" in blob or "regular sequence" in blob:
        doc += 1
    else:
        undoc.append(r)
print("entry mentions automatic:", doc, " not mentioned:", len(undoc))
for r in undoc[:20]:
    print(f"  {r['aid']} k2={r['k2']} k3={r['k3']} | {names.get(r['aid'],'')[:66]}")
json.dump([r['aid'] for r in undoc], open(ROOT + r"\reports\auto_undoc.json","w"), indent=1)
