import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
# states as dicts / functions on a window; use a big window to avoid boundary effects
def Phi(W, lo, hi):
    out = {}
    for j in range(lo, hi+1):
        a = W.get(j-1, 1); b = W.get(j, 1); c = W.get(j+1, 1)
        out[j] = 1 if (a == b == c) else 0
    return out
def S(W, lo, hi):
    out = {}
    for j in range(lo, hi+1):
        out[j] = W.get(abs(j)//2, 1)
    return out
def restrict(W, lo, hi):
    return {j: W.get(j, 1) for j in range(lo, hi+1)}
# (L1): Phi^2(S(S(W))) == S(Phi(S(W)))  for all W on a base window
bad1 = 0; tot1 = 0
for n in range(0, 9):  # support size
    for bits in itertools.product([0,1], repeat=n):
        W = {i: b for i, b in enumerate(bits)}
        # compute on a large window
        L = -20; H = 20
        A = Phi(Phi(S(S(W, L, H), L, H), L, H), L, H)
        B = S(Phi(S(W, L, H), L, H), L, H)
        tot1 += 1
        for j in range(-6, 7):
            if A.get(j,1) != B.get(j,1):
                bad1 += 1
                if bad1 <= 3: print("L1 fail", n, bits, j, A.get(j), B.get(j))
                break
print(f"L1: {bad1} failures / {tot1} configurations")
# (L2): W := Phi(S(X)); check Phi^2(S(W)) == S(Phi(W))
bad2 = 0; tot2 = 0
for n in range(0, 9):
    for bits in itertools.product([0,1], repeat=n):
        X = {i: b for i, b in enumerate(bits)}
        L = -20; H = 20
        W = Phi(S(X, L, H), L, H)
        A = Phi(Phi(S(W, L, H), L, H), L, H)
        B = S(Phi(W, L, H), L, H)
        tot2 += 1
        for j in range(-6, 7):
            if A.get(j,1) != B.get(j,1):
                bad2 += 1
                if bad2 <= 3: print("L2 fail", n, bits, j)
                break
print(f"L2: {bad2} failures / {tot2} configurations")
