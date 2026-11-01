import json, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
rows = []
for f in glob.glob("reports/consistency_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    rows += d.get("sporadic", [])
print("sporadic:", len(rows))
for x in rows[:25]:
    print(f"  {x['aid']} at n={x['at']} | {x['text'][:120]}")
