import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
res = json.load(open(ROOT + r"\reports\automata.json", encoding="utf-8"))
ok = [r for r in res if r["closed"]]
print("closed:", len(ok))
print("state distribution:", Counter(r["states"] for r in ok).most_common(12))
print("\nlargest automata:")
for r in sorted(ok, key=lambda x: -x["states"])[:20]:
    print(f"  {r['aid']} states={r['states']} | {names.get(r['aid'],'')[:66]}")
