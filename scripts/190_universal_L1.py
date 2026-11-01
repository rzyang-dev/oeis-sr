import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
def phi(rule, W, lo, hi):
    out = {}
    for j in range(lo, hi+1):
        l = W.get(j-1, 1); c = W.get(j, 1); r = W.get(j+1, 1)
        out[j] = (rule >> (4*l+2*c+r)) & 1
    return out
def S(W, lo, hi):
    return {j: W.get(abs(j)//2, 1) for j in range(lo, hi+1)}
# universal (L1): Phi^2(S(S W)) = S(Phi(S W)) for ALL W
# enumerate W on a window; check on a smaller inner window
L, H = -12, 12
pats = []
for n in range(9):
    for bits in itertools.product([0,1], repeat=range if False else n):
        pats.append({i: b for i, b in enumerate(bits)})
good_L1 = []
for rule in range(256):
    ok = True
    for W in pats:
        A = phi(rule, phi(rule, S(S(W, L, H), L, H), L, H), L, H)
        B = S(phi(rule, S(W, L, H), L, H), L, H)
        for j in range(-5, 6):
            if A.get(j,1) != B.get(j,1): ok = False; break
        if not ok: break
    if ok: good_L1.append(rule)
print("rules satisfying the UNIVERSAL (L1):", len(good_L1))
print(good_L1)
