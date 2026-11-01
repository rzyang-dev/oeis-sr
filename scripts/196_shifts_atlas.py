import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
# each record: aid, out, trans
def terms(rec, N=120):
    s = 0; out = []
    for _ in range(N):
        out.append(rec["out"][s])
        s = 0  # placeholder
    return out
def seq_terms(rec, N=120):
    # read n bits LSB first from start state 0
    out = []
    tr = rec["trans"]; ov = rec["out"]
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
seqs = {}
for rec in rows:
    seqs[rec["aid"]] = seq_terms(rec, 120)
print("loaded", len(seqs))
# index by 80-term prefix
from collections import defaultdict
idx = defaultdict(list)
for aid, s in seqs.items():
    idx[tuple(s[:80])].append(aid)
# find shift relations: a[n] = b[n+k]
found = []
aids = list(seqs)
for a in aids:
    A = seqs[a]
    for k in range(1, 25):
        # A[n] == B[n+k]  <=>  B[n] == A[n-k]
        for b in aids:
            if a == b: continue
            B = seqs[b]
            if all(A[i] == B[i+k] for i in range(80)):
                found.append((a, b, k))
print("shift relations found:", len(found))
for f in found[:30]:
    print(f)
