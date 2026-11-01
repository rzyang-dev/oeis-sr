import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
for aid in ("A217586", "A096268", "A036987"):
    r = m.get(aid)
    print(aid, "shift=", r["shift"], "states=", r["states"], "out=", r["out"][:8] if r else None)
