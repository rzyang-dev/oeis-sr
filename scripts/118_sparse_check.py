import json, sys, csv
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
tab = {r["aid"]: r for r in csv.DictReader(open(ROOT + r"\reports\atlas_table.csv", encoding="utf-8"))}
per = {r["aid"]: r["period"] for r in json.load(open(ROOT + r"\reports\periodicity930.json", encoding="utf-8"))}
import re
KW = re.compile(r"digit|base|binary|decimal|continued fraction|morphic|word|morphism|Thue|Rudin|paper|dragon|Kronecker|Legendre|mod |valuation|cyclotomic", re.I)
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
sur = [r for r in ok if not per.get(r["aid"]) and not KW.search(names.get(r["aid"], ""))]
print("candidates:", len(sur))
solid = []
for r in sur:
    t = tab.get(r["aid"])
    z = float(t["zero_density"]) if t else None
    if z is None: continue
    if z > 0.9: continue
    solid.append((r, z))
print("non-sparse surprises:", len(solid))
for r, z in solid[:25]:
    print(f"  {r['aid']} states={r['states']} zd={z:.3f} | {names.get(r['aid'],'')[:62]}")
