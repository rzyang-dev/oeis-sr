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
                return max(j for (_, j) in rel), dx
    return None
dist = Counter(); fails = []
detail = []
for rec in rows:
    if rec["aid"] not in nonper: continue
    if rec["states"] > 9: continue
    N = 400
    f = terms_int(rec, N)
    if f == 0: continue
    r = guess(f, N, dxmax=10, dymax=14)
    if r:
        dist[r[0]] += 1
        detail.append((rec["aid"], r[0], r[1], rec["states"]))
    else:
        fails.append((rec["aid"], rec["states"]))
print("non-periodic tested:", sum(dist.values()) + len(fails))
print("degree distribution:", sorted(dist.items()))
print("fails:", len(fails), fails[:15])
print("\nhighest degrees:")
for d in sorted(detail, key=lambda x: -x[1])[:12]:
    print("  ", d)
