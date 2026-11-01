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
seqs = {aid: terms(atlas[aid], N) for aid in nonper}
binary = {aid: s for aid, s in seqs.items() if set(s) <= {0,1}}
aids = sorted(binary)
# GF(2) rank via bitset elimination
vecs = {}
for aid in aids:
    v = 0
    for k in range(N):
        if binary[aid][k]: v |= 1 << k
    vecs[aid] = v
basis = {}   # pivot -> (aid, vector)
for aid in aids:
    v = vecs[aid]
    for p in sorted(basis, reverse=True):
        if v >> p & 1:
            v ^= basis[p][1]
    if v:
        p = v.bit_length() - 1
        basis[p] = (aid, v)
print(f"sequences (binary, non-periodic): {len(aids)}")
print(f"GF(2) rank (first {N} terms): {len(basis)}")
print("independent set (basis):")
for p in sorted(basis, reverse=True):
    print("   ", basis[p][0])
dep = [a for a in aids if a not in {b[0] for b in basis.values()}]
print(f"\ndependent (expressible as XOR of basis): {len(dep)}")
print("   ", dep[:40])
