import json, glob, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
rows = []
for f in glob.glob(ROOT + r"\reports\auto_*.jsonl"):
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))
print("records:", len(rows))
k2 = [r["k2"] for r in rows]
k3 = [r["k3"] for r in rows]
print("k2<=40:", sum(1 for x in k2 if x <= 40), " k3<=40:", sum(1 for x in k3 if x <= 40))
print("both:", sum(1 for r in rows if r["k2"] <= 40 and r["k3"] <= 40))
print("k2<=10:", sum(1 for x in k2 if x <= 10))
# validation: known automatic sequences
known = {"A010060": "Thue-Morse", "A000120": "binary weight", "A005811": "runs", "A001511": "ruler",
         "A000035": "parity", "A003849": "Fibonacci word", "A007877": "period 4"}
m = {r["aid"]: r for r in rows}
for aid, label in known.items():
    r = m.get(aid)
    print(f"  {aid} ({label}): k2={r['k2'] if r else None} k3={r['k3'] if r else None}")
json.dump(rows, open(ROOT + r"\reports\auto_all.json", "w"))
print("saved auto_all.json")
