import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
pairs = json.load(open("reports/cross_domain_strong.json", encoding="utf-8"))
xref = set()
for a, b in con.execute("select src, dst from xref"):
    xref.add((a, b)); xref.add((b, a))
unlinked = [p for p in pairs if (p["a"], p["b"]) not in xref]
print("strong pairs:", len(pairs), " without xref:", len(unlinked))
for p in unlinked:
    print(f"  {p['a']}[{p['ca']}] = {p['b']}[{p['cb']}] n={p['n']}")
    print(f"     A: {names.get(p['a'],'')[:78]}")
    print(f"     B: {names.get(p['b'],'')[:78]}")
json.dump(unlinked, open("reports/cross_domain_unlinked.json", "w"), indent=1)
