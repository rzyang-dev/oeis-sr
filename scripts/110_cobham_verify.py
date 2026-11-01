import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
a3 = {r["aid"]: r for r in json.load(open(ROOT + r"\reports\atlas3.json", encoding="utf-8"))}
per = {r["aid"]: r["period"] for r in json.load(open(ROOT + r"\reports\periodicity930.json", encoding="utf-8"))}
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
a2 = {r["aid"] for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
cand3 = set(json.load(open(ROOT + r"\reports\auto3_cand.json", encoding="utf-8")))
dual = [a for a in a2 if a in cand3]
print("dual candidates:", len(dual))
aperiodic = [a for a in dual if not per.get(a)]
periodic = [a for a in dual if per.get(a)]
print("aperiodic (Cobham-forbidden):", len(aperiodic), " periodic:", len(periodic))
def status(aid):
    r = a3.get(aid)
    if not r: return "not-built"
    return "perfect" if (r["val_total"] > 1000 and r["val_ok"] == r["val_total"]) else "failed"
from collections import Counter
print("aperiodic status:", Counter(status(a) for a in aperiodic))
print("periodic status:", Counter(status(a) for a in periodic))
