
import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
# W on [0..L], value 1 outside. S(W)(p) = W(|p|//2), 1 outside [0..L].
def identity_ok(W, L, jmax=14):
    for p in range(0, jmax+1):
        # F^2(S(W))(p)
        def SW(q): return W.get(abs(q)//2, 1)
        def FSW(q):
            if q < -60 or q > 60: return 1
            return 1 if (SW(q-1)==SW(q)==SW(q+1)) else 0
        lhs = 1 if (FSW(p-1)==FSW(p)==FSW(p+1)) else 0
        rhs = FSW(abs(p)//2)
        if lhs != rhs: return False, p
    return True, None
def F(W, L):
    # one CA step of (W on [0..L], 1 outside) -> dict on [-1..L]
    out={}
    for j in range(-1, L+1):
        out[j] = 1 if (W.get(j-1,1)==W.get(j,1)==W.get(j+1,1)) else 0
    return out
def S(W, L):
    out={}
    for j in range(0, L+1):
        v = W.get(j,1)
        if j==0: out[-1]=out[0]=out[1]=v
        else:
            for p in (2*j,2*j+1,-2*j,-2*j-1): out[p]=v
    return out
L=5
passed=[]; failed=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    ok,_=identity_ok(W,L)
    (passed if ok else failed).append(bits)
print("L=5: passed", len(passed), "of", 1<<(L+1))
print("passed bitmasks:", passed)
print("failed count:", len(failed))
# characterize passing W: print sequences
for bits in passed:
    print("pass:", [ (bits>>j)&1 for j in range(0,L+1)])
