import json, sys, re
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
con = sqlite3.connect("file:" + (ROOT/"oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
text = {}
for aid, t in con.execute("select aid, text from stmt"):
    text.setdefault(aid, []).append(t)
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
per = {r["aid"]: r["period"] for r in json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))}
conc = {a: (d, c) for a, d, c in json.load(open(ROOT/"reports"/"value_concentration.json", encoding="utf-8"))}
KW = re.compile(r"digit|base|binary|decimal|continued fraction|morphic|word|morphism|Thue|Rudin|paper|dragon|Kronecker|Legendre|mod |valuation|cyclotomic|expansion", re.I)
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
cands = []
for r in ok:
    aid = r["aid"]
    if per.get(aid): continue
    d, c = conc.get(aid, (1.0, 1))
    if d > 0.85: continue
    nm = names.get(aid, "")
    if KW.search(nm): continue
    blob = " ".join(text.get(aid, [])).lower()
    if "automatic" in blob: continue
    cands.append((c, d, r["states"], aid, nm))
cands.sort(reverse=True)
print("ranked surprises:", len(cands))
for c, d, s, aid, nm in cands[:15]:
    print(f"  {aid} states={s} values={c} dom={d:.2f} | {nm[:66]}")
