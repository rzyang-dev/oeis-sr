import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
per = dict(con.execute("select aid, periodic from seq_fingerprint"))
names = dict(con.execute("select aid, name from seq"))
atlas = set(a["aid"] for a in json.load(open(ROOT + r"\reports\atlas.json", encoding="utf-8")))
cand3 = json.load(open(ROOT + r"\reports\auto3_cand.json", encoding="utf-8"))
both = [a for a in cand3 if a in atlas]
print("both 2- and 3-automatic:", len(both))
periodic = [a for a in both if (per.get(a) or 0) > 0]
print("of which eventually periodic (fingerprint):", len(periodic))
notper = [a for a in both if not (per.get(a) or 0) > 0]
print("NOT periodic per fingerprint:", len(notper))
for a in notper[:15]:
    print(f"  {a} periodic={per.get(a)} | {names.get(a,'')[:66]}")
