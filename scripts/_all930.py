import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\auto_all.json", encoding="utf-8"))
def auto(c):
    return c and len(c) >= 7 and c[4] == c[5] == c[6] and 1 <= c[6] <= 30
ids = [r["aid"] for r in rows if auto(r["c2"])]
print("all saturating candidates:", len(ids))
json.dump(ids, open(ROOT + r"\reports\auto_all930.json", "w"))
