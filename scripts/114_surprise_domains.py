import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
dom = dict(con.execute("select aid, cluster from domain"))
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
print("verified:", len(ok))
c = Counter(dom.get(r["aid"], -1) for r in ok)
print("domain distribution:", c.most_common(15))
# non-digit domains: exclude names with digit/base/binary and clusters 29,13 etc
import re
KW = re.compile(r"digit|base|binary|decimal|bits|binary expansion", re.I)
other = [r for r in ok if not KW.search(names.get(r["aid"], ""))]
print("\nnon-digit-name verified:", len(other))
for r in other[:30]:
    print(f"  {r['aid']} dom={dom.get(r['aid'])} states={r['states']} | {names.get(r['aid'],'')[:64]}")
