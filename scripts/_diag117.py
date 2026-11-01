import sys, json, re
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
hits = {}
for aid, r in con.execute("select aid, r from congruence2 where p=5 and m=5"):
    hits.setdefault(aid, set()).add(r)
z1 = {a for a, z in hits.items() if z == {1}}
fe = json.load(open("reports/factor_explain.json", encoding="utf-8"))
unexplained = {a for a, p, r in fe["unexplained"]}
sel = sorted(z1 & unexplained)
print("candidates:", len(sel))
ftext = {}
for aid, t in con.execute("select aid, text from formula"):
    ftext.setdefault(aid, []).append(t)
diag = 0
examples = []
for a in sel:
    blob = " ".join(ftext.get(a, []))
    if re.search(r"\[x\^n\].*\^n", blob) or "diagonal" in blob.lower():
        diag += 1
        examples.append((a, blob[:110]))
print("with diagonal-looking formula:", diag)
for a, b in examples[:8]:
    print(f"  {a}: {b}")
