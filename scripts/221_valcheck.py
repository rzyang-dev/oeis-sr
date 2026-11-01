import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
for aid in ("A209229", "A255738", "A268411", "A295890", "A392736", "A267442", "A267579"):
    r = atlas.get(aid)
    if r: print(aid, "states", r["states"], "val_ok/total", r["val_ok"], "/", r["val_total"], "verified:", r["val_ok"] == r["val_total"])
    else: print(aid, "not in atlas")
print()
good = [r for r in rows if r["val_ok"] == r["val_total"]]
print("verified DFAs:", len(good), "of", len(rows))
