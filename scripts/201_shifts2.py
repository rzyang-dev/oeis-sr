import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = {r["aid"] for r in per if r["period"] is None}
print("non-periodic:", len(nonper))
def seq_terms(rec, N=100):
    tr = rec["trans"]; ov = rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
seqs = {}
for rec in atlas:
    if rec["aid"] in nonper:
        seqs[rec["aid"]] = seq_terms(rec, 100)
print("loaded:", len(seqs))
aids = list(seqs)
found = set()
for a in aids:
    A = seqs[a]
    for b in aids:
        if a == b: continue
        B = seqs[b]
        for k in range(1, 20):
            if all(A[i] == B[i+k] for i in range(70)):
                found.add((a, b, k))
print("shift relations among NON-PERIODIC:", len(found))
for f in sorted(found)[:30]:
    print(f)
