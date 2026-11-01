import json, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
rows = []
for f in glob.glob("reports/consistency_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    rows += d.get("sporadic", [])
print("sporadic:", len(rows))
rows.sort(key=lambda x: x["aid"])
for x in rows[:30]:
    print(f"  {x['aid']} n={x['at']} | {x['text'][:110]}")
