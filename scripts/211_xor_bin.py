import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = [r["aid"] for r in per if r["period"] is None]
def terms(rec, N=120):
    tr, ov = rec["trans"], rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
N = 100
seqs = {aid: terms(atlas[aid], N) for aid in nonper}
binary = {aid: s for aid, s in seqs.items() if set(s) <= {0, 1}}
print("non-periodic:", len(seqs), " binary (0/1):", len(binary))
idx = {}
for aid, s in binary.items():
    idx.setdefault(tuple(s), []).append(aid)
rels = set()
aids = list(binary)
for i in range(len(aids)):
    a = aids[i]; A = binary[a]
    for j in range(i+1, len(aids)):
        b = aids[j]; B = binary[b]
        C = tuple(1 if A[k] != B[k] else 0 for k in range(N))
        for c in idx.get(C, []):
            rels.add(tuple(sorted((a, b, c))))
print("XOR relations (0/1 only):", len(rels))
for r in sorted(rels)[:25]:
    print("  ", r)
