import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\auto_all.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
for aid in ("A268355", "A054244", "A219201", "A010060", "A179868", "A085296"):
    r = m.get(aid)
    print(aid, "c2=", r["c2"] if r else None, " c3=", r["c3"] if r else None)
