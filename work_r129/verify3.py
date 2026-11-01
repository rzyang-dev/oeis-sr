
import numpy as np, sys, random
sys.stdout.reconfigure(encoding="utf-8")
N, T = 1600, 700
def simulate(N, T):
    s = np.ones(2*N+1, dtype=np.uint8); s[N-1:N+2] = 0
    rows = np.empty((T+1, 2*N+1), dtype=np.uint8); rows[1] = s
    r0 = np.zeros(2*N+1, dtype=np.uint8); r0[N] = 1; rows[0] = r0
    for t in range(1, T):
        a = s[:-2]; b = s[1:-1]; c = s[2:]
        s[1:-1] = ((a == b) & (b == c)).astype(np.uint8)
        rows[t+1] = s
    return rows
rows = simulate(N, T)
V = lambda t,j: int(rows[t, j+N])
TMAX = 320
def E(t, jlim):
    return set(j for j in range(-jlim,jlim+1) if V(t,j)!=V(t,j+1))
def R(t):
    return set(j for j in E(t, t+2) if j >= 0)
def dR(s):
    out=set()
    for j in range(0, 200):
        a = 1 if (j in s) else 0
        b = 1 if (j-1 in s) else 0
        if a!=b: out.add(j)
    return out
bad_R1 = [t for t in range(1, TMAX//2) if R(2*t+1) != set(2*r+1 for r in R(t))]
bad_R2 = [t for t in range(2, TMAX//2) if R(2*t) != set(2*r for r in dR(R(t-1)))]
print("R_{2t+1}=2R_t+1 failures:", bad_R1[:10], "count", len(bad_R1))
print("R_{2t}=2*dR_{t-1} failures:", bad_R2[:10], "count", len(bad_R2))
bad3 = [t for t in range(0,TMAX) if (V(t,0)!=V(t,1)) != ( (t+2)&(t+1) == 0 )]
print("e_t(0)=1 iff t+2 power of 2, failures:", bad3[:10])
# sanity: print E_t, R_t for small t
for t in range(0,10):
    print(f"t={t} E={sorted(E(t,t+2))} R={sorted(R(t))} dR(R)={sorted(dR(R(t)))}")
# universal identity F^2 o S = S o F
def F2(conf, lo, hi):
    cur = dict(conf); lo2, hi2 = lo, hi
    for _ in range(2):
        nxt = {j: (1 if (cur.get(j-1,1)==cur.get(j,1)==cur.get(j+1,1)) else 0) for j in range(lo2+1, hi2)}
        cur = nxt; lo2+=1; hi2-=1
    return cur
def S(conf, hi):
    out = {}
    for j in range(0, hi+1):
        v = conf.get(j,1)
        if j==0: out[-1]=out[0]=out[1]=v
        else:
            for p in (2*j, 2*j+1, -2*j, -2*j-1): out[p]=v
    return out
random.seed(1); fails=0; first=None
for trial in range(500):
    U = {j: random.randint(0,1) for j in range(0,7)}
    SU = S(U, 6)
    lhs = F2(SU, -16, 16)
    FU = {j: (1 if (U.get(j-1,1)==U.get(j,1)==U.get(j+1,1)) else 0) for j in range(0,6)}
    rhs = S(FU, 5)
    for p in range(-10, 11):
        if lhs.get(p,1)!=rhs.get(p,1):
            fails+=1; first=(U,p,lhs.get(p,1),rhs.get(p,1)); break
print("universal F^2 o S = S o F failures:", fails, "/500;", first)
