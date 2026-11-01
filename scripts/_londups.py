import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
d = json.load(open("reports/long_equal.json", encoding="utf-8"))
sel = [x for x in d if not x["labelled_duplicate"] and not x["cross_referenced"]]
print("unlabelled + uncrossed:", len(sel))
for x in sorted(sel, key=lambda y: -y["agree"])[:20]:
    print(f"  {x['a']} vs {x['b']}  agree={x['agree']}  mismatch={x['first_mismatch']}")
    print(f"     A: {names.get(x['a'],'')[:80]}")
    print(f"     B: {names.get(x['b'],'')[:80]}")
