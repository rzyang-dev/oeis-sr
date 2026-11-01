
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

# 1. evenness of V_t ; 2. parity invariant of edges
bad_even = [(t,j) for t in range(1,TMAX) for j in range(1,t+1) if V(t,j)!=V(t,-j)]
def E(t, jlim):
    return set(j for j in range(-jlim,jlim+1) if V(t,j)!=V(t,j+1))
bad_par = []
for t in range(0,TMAX):
    for j in E(t, t+2):
        want = (t+1) % 2 if j < 0 else t % 2
        if j % 2 != want: bad_par.append((t,j))
print("evenness failures:", len(bad_even), " parity-invariant failures:", len(bad_par), bad_par[:5])

# 3. odd doubling: V(2t+1,2j)=V(2t+1,2j+1)=V(t,j) for j>=0
bad_odd = []
for t in range(1, TMAX//2):
    for j in range(0, t+1):
        if V(2*t+1,2*j)!=V(t,j) or V(2*t+1,2*j+1)!=V(t,j): bad_odd.append((t,j))
print("odd doubling failures:", len(bad_odd), bad_odd[:5])

# 4. even formulas: V(2t,0)=1 ; V(2t,2j)=[V(t-1,j-1)=V(t-1,j)] (j>=1) ; V(2t,2j+1)=[V(t-1,j)=V(t-1,j+1)] (j>=0)
bad_even2 = []
for t in range(2, TMAX//2):
    if V(2*t,0)!=1: bad_even2.append((t,0))
    for j in range(1, t+2):
        if V(2*t,2*j) != (1 if V(t-1,j-1)==V(t-1,j) else 0): bad_even2.append((t,j,"even"))
        if V(2*t,2*j+1) != (1 if V(t-1,j)==V(t-1,j+1) else 0): bad_even2.append((t,j,"odd"))
    for j in range(0, t+2):
        if V(2*t,2*j+1) != (1 if V(t-1,j)==V(t-1,j+1) else 0): bad_even2.append((t,j,"odd2"))
print("even formula failures:", len(bad_even2), bad_even2[:5])

# 5. R recursions
def R(t):
    return set(j for j in E(t, t+2) if j >= 0)
def dR(s):
    out=set()
    for j in range(0, s+4):
        a = 1 if (j in s) else 0
        b = 1 if (j-1 in s) else 0
        if a!=b: out.add(j)
    return out
bad_R1 = []; bad_R2 = []
for t in range(1, TMAX//2):
    if R(2*t+1) != set(2*r+1 for r in R(t)): bad_R1.append(t)
for t in range(2, TMAX//2):
    if R(2*t) != set(2*r for r in dR(R(t-1))): bad_R2.append(t)
print("R_{2t+1}=2R_t+1 failures:", bad_R1[:10])
print("R_{2t}=2 dR_{t-1} failures:", bad_R2[:10])

# 6. parent's (3)
bad3 = [t for t in range(0,TMAX) if (V(t,0)!=V(t,1)) != ( (t+2)&(t+1) == 0 )]
print("e_t(0)=1 iff t+2 power of 2, failures:", bad3[:10])

# 7. universal identity F^2 o S = S o F  for arbitrary U on right half (U even extension, 1 outside)
def F2(conf, lo, hi):
    lo2, hi2 = lo, hi
    cur = dict(conf)
    for _ in range(2):
        nxt = {}
        for j in range(lo2+1, hi2):
            nxt[j] = 1 if (cur.get(j-1,1)==cur.get(j,1)==cur.get(j+1,1)) else 0
        cur = nxt; lo2+=1; hi2-=1
    return cur
def S(conf, lo, hi):
    # conf given on j>=0; build SU on [-hi2..hi2]
    out = {}
    hi2 = 2*hi+1
    for j in range(lo, hi+1):
        v = conf.get(j,1)
        if j==0:
            for p in (-1,0,1): out[p]=v
        else:
            for p in (2*j, 2*j+1, -2*j, -2*j-1): out[p]=v
    for p in range(-hi2-6, hi2+7):
        out.setdefault(p,1)
    return out
random.seed(1)
fails = 0; first=None
for trial in range(400):
    U = {j: random.randint(0,1) for j in range(0,7)}
    SU = S(U, 0, 6)
    lhs = F2(SU, -14, 14)
    FU = {j: (1 if (U.get(j-1,1)==U.get(j,1)==U.get(j+1,1)) else 0) for j in range(0,6)}
    rhs = S(FU, 0, 5)
    for p in range(-10, 11):
        a = lhs.get(p,1); b = rhs.get(p,1)
        if a!=b:
            fails += 1
            if first is None: first=(U,p,a,b)
            break
print("universal F^2 o S = S o F : failures", fails, "of 400;", first)
