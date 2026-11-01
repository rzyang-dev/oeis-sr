import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
ok = {r["aid"] for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
conj = []
for aid, t in con.execute("select aid, text from stmt where lower(text) like '%conjecture%'"):
    if aid in ok:
        conj.append((aid, t[:160]))
print("atlas entries with conjectures:", len(conj))
for aid, t in conj[:25]:
    print(f"  {aid}: {t}")
