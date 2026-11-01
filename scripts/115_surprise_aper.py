import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
per = {r["aid"]: r["period"] for r in json.load(open(ROOT + r"\reports\periodicity930.json", encoding="utf-8"))}
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
aper = [r for r in ok if not per.get(r["aid"])]
print("aperiodic verified:", len(aper))
KW = re.compile(r"digit|base|binary|decimal|continued fraction|morphic|word|morphism|Thue|Rudin|paper|dragon|Kronecker|Legendre|mod |valuation|cyclotomic", re.I)
surprise = [r for r in aper if not KW.search(names.get(r["aid"], ""))]
print("non-obvious aperiodic:", len(surprise))
for r in surprise[:30]:
    print(f"  {r['aid']} states={r['states']} | {names.get(r['aid'],'')[:72]}")
