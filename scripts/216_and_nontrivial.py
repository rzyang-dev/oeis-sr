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
idx = {}
for aid, s in binary.items():
    idx.setdefault(tuple(s), []).append(aid)
aids = sorted(binary)
cand = set()
for i in range(len(aids)):
    A = binary[aids[i]]
    for j in range(i+1, len(aids)):
        B = binary[aids[j]]
        C = tuple(1 if (A[k] and B[k]) else 0 for k in range(N))
        for c in idx.get(C, []):
            cand.add(tuple(sorted((aids[i], aids[j], c))))
# non-trivial: c not equal to a or b, and c not constant, and a != b
def is_const(t): return len(set(t)) == 1
def verify_and(a, b, c):
    tra, trb, trc = atlas[a]["trans"], atlas[b]["trans"], atlas[c]["trans"]
    ova, ovb, ovc = atlas[a]["out"], atlas[b]["out"], atlas[c]["out"]
    start = (0,0,0); seen = {start}; fr = [start]
    while fr:
        nx = []
        for (sa, sb, sc) in fr:
            if ova[sa] != (1 if (ovb[sb] and ovc[sc]) else 0): return False
            for bit in (0,1):
                s2 = (tra[sa][bit], trb[sb][bit], trc[sc][bit])
                if s2 not in seen: seen.add(s2); nx.append(s2)
        fr = nx
    return True
nontrivial = []
for (a, b, c) in sorted(cand):
    if c in (a, b): continue
    if is_const(binary[c]): continue
    if verify_and(a, b, c):
        nontrivial.append((a, b, c))
print("NON-TRIVIAL AND relations:", len(nontrivial))
for r in nontrivial: print("  ", r[0], "AND", r[1], "=", r[2])
