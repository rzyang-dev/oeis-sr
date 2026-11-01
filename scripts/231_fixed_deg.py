import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from collections import Counter
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = {r["aid"] for r in per if r["period"] is None}
def terms_int(rec, N):
    tr, ov = rec["trans"], rec["out"]
    v = 0
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        if ov[s]: v |= 1 << n
    return v
def mul(a, b, N):
    r = 0; x = 0; bb = b
    while bb:
        if bb & 1: r ^= a << x
        bb >>= 1; x += 1
    return r & ((1 << N) - 1)
def guess(f, N, dxmax, dymax):
    ps = [1]
    for j in range(1, dymax+1): ps.append(mul(ps[-1], f, N))
    for dy in range(1, dymax+1):
        for dx in range(0, dxmax+1):
            cols = []; names = []
            for j in range(0, dy+1):
                for i in range(0, dx+1):
                    if i == 0 and j == 0: continue
                    v = (ps[j] << i) & ((1 << N) - 1)
                    if v: cols.append(v); names.append((i, j))
            cols.append(1); names.append((0, 0))
            basis = {}; dep = None
            for idx, v in enumerate(cols):
                w = v; expr = 1 << idx
                while w:
                    p = w.bit_length() - 1
                    if p in basis:
                        w ^= basis[p][0]; expr ^= basis[p][1]
                    else:
                        basis[p] = (w, expr); break
                if w == 0:
                    dep = expr; break
            if dep is not None:
                rel = [names[k] for k in range(len(names)) if dep >> k & 1]
                return max(j for (_, j) in rel), sorted(rel)
    return None
N = 400
dist = Counter(); detail = []; fails = []; skipped = 0
for rec in rows:
    ovs = set(rec["out"])
    if not ovs <= {0, 1}:
        skipped += 1; continue
    if rec["states"] > 9: continue
    f = terms_int(rec, N)
    if f == 0: continue
    r = guess(f, N, 10, 14)
    tag = "nonper" if rec["aid"] in nonper else "per"
    if r:
        dist[(tag, r[0])] += 1
        detail.append((rec["aid"], tag, r[0], r[1]))
    else:
        fails.append((rec["aid"], tag, rec["states"]))
print("skipped (non-binary outputs):", skipped)
print("distribution (tag, degree):", sorted(dist.items()))
print("fails:", len(fails), fails[:12])
print("\nnon-periodic degrees:")
for d in sorted([x for x in detail if x[1]=="nonper"], key=lambda x: -x[2])[:10]:
    print("  ", d)
