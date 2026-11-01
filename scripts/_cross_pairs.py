import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
cat = dict(con.execute("select aid, category from construction"))
d = json.load(open("reports/long_equal.json", encoding="utf-8"))
sel = [x for x in d if not x["labelled_duplicate"] and not x["cross_referenced"]]
cross = []
for x in sel:
    ca, cb = cat.get(x["a"]), cat.get(x["b"])
    if ca and cb and ca != cb and ca != "other" and cb != "other":
        cross.append((x, ca, cb))
print("cross-category unlabelled pairs:", len(cross))
for x, ca, cb in sorted(cross, key=lambda t: -t[0]["agree"])[:12]:
    print(f"  {x['a']}[{ca}] vs {x['b']}[{cb}] agree={x['agree']} mismatch={x['first_mismatch']}")
    print(f"     {names.get(x['a'],'')[:75]}")
    print(f"     {names.get(x['b'],'')[:75]}")
