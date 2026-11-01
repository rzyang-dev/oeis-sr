import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
pat = re.compile(r"base[- ]?([3-9]|1[0-6])|decimal|digits? of", re.I)
hits = [(r, names.get(r["aid"], "")) for r in ok if pat.search(names.get(r["aid"], ""))]
print("verified sequences whose name mentions another base:", len(hits))
for r, n in hits[:30]:
    print(f"  {r['aid']} states={r['states']} | {n[:72]}")
