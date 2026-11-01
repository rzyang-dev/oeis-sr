import json, sys, re
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
ver = json.load(open("reports/closed_loop_verified.json", encoding="utf-8"))
z1 = [x["aid"] for x in ver if x["kind"] == "z1"]
# exclude the 9 periodic ones
periodic = {"A019566","A056545","A095740","A108189","A144500","A182386","A288268","A331725","A332562"}
z1 = [a for a in z1 if a not in periodic]
print("non-periodic Z={1}:", len(z1))
ftext = defaultdict(list)
for aid, t in con.execute("select aid, text from formula"):
    ftext[aid].append(t)
names = dict(con.execute("select aid, name from seq"))
groups = defaultdict(list)
for a in z1:
    blob = " ".join(ftext.get(a, []))[:400]
    if "Sum_{" in blob and "binomial" in blob.lower(): k = "binomial-sum"
    elif "Series_Reversion" in blob or "g.f." in blob.lower() or "G.f." in blob: k = "gfun"
    elif "E.g.f." in blob: k = "egf"
    elif "a(n) = a(n-" in blob: k = "recurrence"
    else: k = "other"
    groups[k].append(a)
print({k: len(v) for k, v in groups.items()})
print("\nbinomial-sum examples:")
for a in groups["binomial-sum"][:12]:
    print(f"  {a}: {names.get(a,'')[:60]}")
    print(f"     {ftext.get(a,[''])[0][:120]}")
