import sys, json, itertools
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
hits = {}
for aid, r in con.execute("select aid, r from congruence2 where p=5 and m=5"):
    hits.setdefault(aid, set()).add(r)
z1 = {a for a, z in hits.items() if z == {1}}
print("sequences with Z={1}:", len(z1))
fe = json.load(open("reports/factor_explain.json", encoding="utf-8"))
unexplained = {a for a, p, r in fe["unexplained"]}
print("of which unexplained by linear factors:", len(z1 & unexplained))
# how many of the unexplained set are in z1
print("unexplained total:", len(unexplained))
names = dict(con.execute("select aid, name from seq"))
fame = dict(con.execute("select aid, count(*) from formula group by 1"))
top = sorted(z1 & unexplained, key=lambda a: -fame.get(a, 0))[:15]
for a in top:
    print(f"  {a} f={fame.get(a,0)} | {names.get(a,'')[:66]}")
