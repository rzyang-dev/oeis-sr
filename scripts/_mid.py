import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas_props.json", encoding="utf-8"))
mid = [r for r in rows if 0.05 < r["zero_density"] < 0.95]
print("nontrivial zero density:", len(mid))
for r in sorted(mid, key=lambda x: x["zero_density"]):
    print(f"  {r['aid']} states={r['states']} zd={r['zero_density']} values={r['values']} | {r['name'][:58]}")
