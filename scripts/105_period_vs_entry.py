import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
text = {}
for aid, t in con.execute("select aid, text from stmt"):
    text.setdefault(aid, []).append(t)
per = {r["aid"]: r["period"] for r in json.load(open(ROOT + r"\reports\periodicity.json", encoding="utf-8"))}
print("analyzed:", len(per))
claim = 0
disagree = []
for aid, T in per.items():
    blob = " ".join([names.get(aid, "")] + text.get(aid, [])).lower()
    says = bool(re.search(r"\bperiodic\b", blob))
    if says: claim += 1
    if says and not T:
        disagree.append((aid, T, "claims periodic but automaton says no"))
    if T and not says:
        pass
print("entries mentioning 'periodic':", claim)
print("disagreements:", len(disagree))
for d in disagree[:20]:
    print("  ", d[0], names.get(d[0], "")[:70])
