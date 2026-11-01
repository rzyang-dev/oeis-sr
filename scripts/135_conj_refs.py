import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
atlas = {r["aid"] for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
names = dict(con.execute("select aid, name from seq"))
import collections
conj = collections.defaultdict(list)
for aid, t in con.execute("select aid, text from stmt where lower(text) like '%conjecture%'"):
    conj[aid].append(t)
print("entries with conjectures (all):", len(conj))
mine = {a: ts for a, ts in conj.items() if a in atlas}
print("in atlas:", len(mine))
for aid, ts in sorted(mine.items()):
    refs = set(re.findall(r"A\d{6}", " ".join(ts)))
    others = sorted(r for r in refs if r != aid)
    inA = [r for r in others if r in atlas]
    print(f"  {aid}: refs={others}  in-atlas={inA}")
