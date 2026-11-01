import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = [r["aid"] for r in per if r["period"] is None]
def terms(rec, N=100):
    tr, ov = rec["trans"], rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
seqs = {aid: terms(atlas[aid]) for aid in nonper}
binary = {aid: s for aid, s in seqs.items() if set(s) <= {0,1}}
idx = {}
for aid, s in binary.items():
    idx.setdefault(tuple(s), []).append(aid)
cand = set()
aids = list(binary)
for i in range(len(aids)):
    A = binary[aids[i]]
    for j in range(i+1, len(aids)):
        B = binary[aids[j]]
        C = tuple(1 if A[k] != B[k] else 0 for k in range(100))
        for c in idx.get(C, []):
            cand.add(tuple(sorted((aids[i], aids[j], c))))
print("candidate XOR relations:", len(cand))
def verify_xor(a, b, c, maxstates=50000):
    tra, trb, trc = atlas[a]["trans"], atlas[b]["trans"], atlas[c]["trans"]
    ova, ovb, ovc = atlas[a]["out"], atlas[b]["out"], atlas[c]["out"]
    start = (0, 0, 0); seen = {start}; fr = [start]
    while fr:
        nx = []
        for (sa, sb, sc) in fr:
            if ova[sa] != (ovb[sb] ^ ovc[sc]):
                return False
            for bit in (0, 1):
                s2 = (tra[sa][bit], trb[sb][bit], trc[sc][bit])
                if s2 not in seen:
                    seen.add(s2); nx.append(s2)
                    if len(seen) > maxstates: return None
        fr = nx
    return True
good = []; bad = []
for (a, b, c) in sorted(cand):
    r = verify_xor(a, b, c)
    (good if r else bad).append((a, b, c))
print("rigorously verified XOR:", len(good), " failed:", len(bad))
for g in good: print("  ", g)
