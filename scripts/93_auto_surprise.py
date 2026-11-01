import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
per = dict(con.execute("select aid, periodic from seq_fingerprint"))
rows = json.load(open(ROOT + r"\reports\auto_all.json", encoding="utf-8"))
def auto(c):
    return c and len(c) >= 7 and c[4] == c[5] == c[6] and 1 <= c[6] <= 30
cand = [r for r in rows if auto(r["c2"])]
print("strict 2-automatic:", len(cand))
periodic = [r for r in cand if (per.get(r["aid"]) or 0) > 0]
print("of which eventually periodic:", len(periodic))
rest = [r for r in cand if not (per.get(r["aid"]) or 0) > 0]
print("non-periodic:", len(rest))
KW = re.compile(r"digit|base|binary|decimal|cyclotomic|continued fraction|legendre|mod ", re.I)
surprise = [r for r in rest if not KW.search(names.get(r["aid"], ""))]
print("non-periodic, non-digit-name:", len(surprise))
for r in surprise[:40]:
    print(f"  {r['aid']} c2={r['c2']} | {names.get(r['aid'],'')[:66]}")
json.dump([r["aid"] for r in surprise], open(ROOT + r"\reports\auto_surprise.json","w"), indent=1)
