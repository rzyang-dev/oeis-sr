import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
for aid in ("A267442","A043545","A285383","A035263","A284948","A096268","A217586","A036987"):
    r = m.get(aid)
    if not r:
        print(aid, "missing"); continue
    print(aid, "shift", r["shift"], "states", r["states"])
    print("  out =", r["out"])
    print("  trans =", r["trans"])
