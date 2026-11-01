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
binary = {aid: s for aid, s in seqs.items() if set(s) <= {0,1}}
idx = {}
for aid, s in binary.items(): idx.setdefault(s, []).append(aid)
aids = sorted(binary)
cand = []
for i in range(len(aids)):
    A = binary[aids[i]]
    for j in range(i+1, len(aids)):
        B = binary[aids[j]]
        if A == B: continue
        C = tuple(1 if (A[k] and B[k]) else 0 for k in range(N))
        for c in idx.get(C, []):
            if binary[c] in (A, B): continue
            cand.append((aids[i], aids[j], c))   # a AND b = c, roles preserved
print("genuine AND candidates (roles preserved):", len(cand))
def verify_and(a, b, c):
    tra, trb, trc = atlas[a]["trans"], atlas[b]["trans"], atlas[c]["trans"]
    ova, ovb, ovc = atlas[a]["out"], atlas[b]["out"], atlas[c]["out"]
    start = (0,0,0); seen = {start}; fr = [start]
    while fr:
        nx = []
        for (sa, sb, sc) in fr:
            if (1 if (ova[sa] and ovb[sb]) else 0) != ovc[sc]: return False
            for bit in (0,1):
                s2 = (tra[sa][bit], trb[sb][bit], trc[sc][bit])
                if s2 not in seen: seen.add(s2); nx.append(s2)
        fr = nx
    return True
good = [t for t in cand if verify_and(*t)]
print("verified genuine AND (a AND b = c):", len(good))
for g in good: print(f"  {g[0]} AND {g[1]} = {g[2]}")
