
import sys, random
sys.stdout.reconfigure(encoding="utf-8")
LO, HI = -60, 60
def F(c):
    return {j: (1 if (c.get(j-1,1)==c.get(j,1)==c.get(j+1,1)) else 0) for j in range(LO, HI)}
def S(c):
    out={}
    for j in range(0, 20):
        v=c.get(j,1)
        if j==0: out[-1]=out[0]=out[1]=v
        else:
            for p in (2*j,2*j+1,-2*j,-2*j-1): out[p]=v
    return out
def norm(c): return {j: c.get(j,1) for j in range(LO,HI)}
random.seed(7)
def test(op_left, op_right, name):
    bad=0; first=None
    for trial in range(300):
        W={j: random.randint(0,1) for j in range(0,5)}
        L=op_left(W); R=op_right(W)
        diff=[p for p in range(-6,7) if L.get(p,1)!=R.get(p,1)]
        if diff:
            bad+=1
            if first is None: first=(W,diff[:4],L.get(diff[0],1),R.get(diff[0],1))
    print(name, "failures:", bad, "/300", first)
# candidate identities
test(lambda W: F(F(S(S(W)))), lambda W: S(F(S(W))), "F^2 S S = S F S      ")
test(lambda W: F(F(S(F(S(W))))), lambda W: S(F(F(S(W)))), "F^2 S F S = S F^2 S ")
