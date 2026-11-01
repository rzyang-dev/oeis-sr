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
vecs = {aid: sum((1 << k) for k in range(N) if binary[aid][k]) for aid in aids}
# elimination with tracking: basis[p] = (vector, {aid: parity})
basis = {}
for aid in aids:
    v = vecs[aid]; expr = {aid: 1}
    while v:
        p = v.bit_length() - 1
        if p in basis:
            bv, bexpr = basis[p]
            v ^= bv
            for k in bexpr: expr[k] = expr.get(k, 0) ^ bexpr[k]
        else:
            basis[p] = (v, expr); expr = None; break
    # if expr is not None: v became 0 => dependent, expr is the relation
print("rank:", len(basis))
# now reduce each dependent aid against the final basis to get expression
piv = sorted(basis, reverse=True)
def reduce_with_expr(aid):
    v = vecs[aid]; used = {aid: 1}
    for p in piv:
        if v >> p & 1:
            bv, bexpr = basis[p]
            v ^= bv
            for k in bexpr: used[k] = used.get(k, 0) ^ bexpr[k]
    return v, used
dep = []
for aid in aids:
    v, used = reduce_with_expr(aid)
    if v == 0 and sum(used.values()) > 1:
        terms_used = {k: e for k, e in used.items() if e and k != aid}
        if terms_used:
            dep.append((aid, terms_used))
print("dependent with explicit expression:", len(dep))
for aid, ex in dep[:35]:
    rhs = " XOR ".join(sorted(ex))
    print(f"  {aid} = {rhs}")
