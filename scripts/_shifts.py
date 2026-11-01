import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
for aid in ("A267442","A043545","A285383","A035263","A284948","A096268"):
    r = m.get(aid)
    print(aid, "shift=", r["shift"] if r else None, "states=", r["states"] if r else None)
