import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\auto_all.json", encoding="utf-8"))
print("records:", len(rows))
def auto(r, key):
    c = r.get(key)
    if not c or len(c) < 6:
        return False
    if c[6] < 1 or c[6] > 30:
        return False
    # saturation: last three levels do not grow
    return c[4] == c[5] == c[6]
a2 = [r for r in rows if auto(r, "c2")]
a3 = [r for r in rows if auto(r, "c3")]
print("2-automatic (saturating):", len(a2))
print("3-automatic (saturating):", len(a3))
print("both:", sum(1 for r in rows if auto(r, "c2") and auto(r, "c3")))
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
text = {}
for aid, t in con.execute("select aid, text from stmt"):
    text.setdefault(aid, []).append(t)
undoc = []
for r in a2:
    blob = " ".join(text.get(r["aid"], [])).lower()
    if "automatic" not in blob and "2-regular" not in blob:
        undoc.append(r)
print("2-automatic without 'automatic' in entry:", len(undoc))
for r in undoc[:30]:
    print(f"  {r['aid']} c2={r['c2']} | {names.get(r['aid'],'')[:62]}")
json.dump([r["aid"] for r in undoc], open(ROOT + r"\reports\auto_undoc2.json","w"), indent=1)