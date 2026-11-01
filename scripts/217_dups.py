import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = [r["aid"] for r in per if r["period"] is None]
def terms(rec, N=128):
    tr, ov = rec["trans"], rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
N = 128
seqs = {aid: tuple(terms(atlas[aid], N)) for aid in nonper}
from collections import defaultdict
groups = defaultdict(list)
for aid, s in seqs.items(): groups[s].append(aid)
dups = {s: a for s, a in groups.items() if len(a) > 1}
print("distinct sequences:", len(groups), " duplicate classes:", len(dups))
total_dup = sum(len(a) for a in dups.values())
print("sequences involved in duplicates:", total_dup)
for s, a in sorted(dups.items(), key=lambda kv: -len(kv[1]))[:12]:
    print("  ", sorted(a))
