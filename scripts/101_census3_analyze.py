import json, glob, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
rows = []
for f in glob.glob(ROOT + r"\reports\auto3_*.jsonl"):
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))
print("records:", len(rows))
def auto(c):
    return c and len(c) >= 7 and c[4] == c[5] == c[6] and 1 <= c[6] <= 40
cand = [r for r in rows if auto(r["c3"])]
print("strict 3-automatic (saturating):", len(cand), f"{len(cand)/len(rows):.2%}")
print("per-level counts of a few:")
for r in cand[:6]:
    print("  ", r["aid"], r["c3"], names.get(r["aid"], "")[:50])
# overlap with 2-automatic atlas
atlas = set(a["aid"] for a in json.load(open(ROOT + r"\reports\atlas.json", encoding="utf-8")))
both = [r for r in cand if r["aid"] in atlas]
print("also 2-automatic (atlas):", len(both))
json.dump([r["aid"] for r in cand], open(ROOT + r"\reports\auto3_cand.json", "w"), indent=1)
