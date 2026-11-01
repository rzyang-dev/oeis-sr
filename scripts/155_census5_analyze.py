import json, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = []
for f in glob.glob(ROOT + r"\reports\auto5_*.jsonl"):
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))
print("records:", len(rows))
def auto(c):
    return c and len(c) >= 5 and c[2] == c[3] == c[4] and 1 <= c[4] <= 40
cand = [r for r in rows if auto(r["c5"])]
print("strict 5-automatic (e<=4, saturating):", len(cand), f"{len(cand)/len(rows):.2%}")
atlas = {a["aid"] for a in json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8")) if a["val_ok"] == a["val_total"] and a["val_total"] >= 1000}
per = {r["aid"]: r["period"] for r in json.load(open(ROOT + r"\reports\periodicity930.json", encoding="utf-8"))}
both = [r["aid"] for r in cand if r["aid"] in atlas]
print("also 2-automatic (atlas):", len(both))
periodic = [a for a in both if per.get(a)]
print("of which eventually periodic:", len(periodic))
viol = [a for a in both if not per.get(a)]
print("Cobham violations (2&5 automatic but aperiodic):", len(viol))
for a in viol[:10]:
    print("  ", a)
json.dump([r["aid"] for r in cand], open(ROOT + r"\reports\auto5_cand.json", "w"), indent=1)
