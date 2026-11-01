import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
rows = json.load(open(ROOT + r"\reports\periodicity930.json", encoding="utf-8"))
aper = [r for r in rows if not r["period"]]
print("analyzed:", len(rows), " periodic:", len(rows)-len(aper), " aperiodic:", len(aper))
from collections import Counter
print("periods:", Counter(r["period"] for r in rows if r["period"]).most_common(12))
print("\naperiodic examples:")
for r in aper[:25]:
    print(f"  {r['aid']} states={r['states']} | {names.get(r['aid'],'')[:64]}")
