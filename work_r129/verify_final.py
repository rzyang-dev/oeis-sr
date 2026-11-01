
import numpy as np, sys
sys.stdout.reconfigure(encoding="utf-8")
# ---------- exhaustive check of the two operator identities ----------
def F(c):
    # c: dict over Z with 1 outside (missing = 1); returns dict over all needed indices lazily via function
    pass
def fval(c, j):
    # one CA step at j, c given as dict (missing -> 1)
    return 1 if (c.get(j-1,1)==c.get(j,1)==c.get(j+1,1)) else 0
def sval(c, p):
    return c.get(abs(p)//2, 1)
bad1 = bad2 = 0; ex1 = ex2 = None
K = 12
for bits in range(1<<(K+1)):
    W = {j:(bits>>j)&1 for j in range(0,K+1)}
    # S(W) values via sval; F(S(W)) at q = fval of sval; F^2 S(W) at p
    def SW(q): return sval(W,q)
    def FSW(q): return 1 if (SW(q-1)==SW(q)==SW(q+1)) else 0
    def F2SW(p): return 1 if (FSW(p-1)==FSW(p)==FSW(p+1)) else 0
    # S(S(W)) at q = (SW)(abs(q)//2)
    def SSW(q): return SW(abs(q)//2)
    def FSSW(p): return 1 if (SSW(p-1)==SSW(p)==SSW(p+1)) else 0
    def SFSW(p): return FSW(abs(p)//2)     # S(F(S(W)))(p)
    # F(S(F(S(W)))) : need FS(W) then F twice
    def FSW2(q): return 1 if (FSW(q-1)==FSW(q)==FSW(q+1)) else 0
    def F2SFW(p): return 1 if (FSW2(p-1)==FSW2(p)==FSW2(p+1)) else 0
    def SFFSW(p): return FSW2(abs(p)//2)   # S(F(F(S(W))))(p)
    for p in range(0, 21):
        if FSSW(p) != SFSW(p):
            bad1 += 1
            if ex1 is None: ex1 = (W,p,FSSW(p),SFSW(p))
        if F2SFW(p) != SFFSW(p):
            bad2 += 1
            if ex2 is None: ex2 = (W,p,F2SFW(p),SFFSW(p))
print("I1  F^2 S S = S F S   failures:", bad1, " example:", ex1)
print("I2  F^2 S F S = S F^2 S failures:", bad2, " example:", ex2)

# ---------- full verification of all claims ----------
N, T = 1600, 720
def simulate(N, T):
    s = np.ones(2*N+1, dtype=np.uint8); s[N-1:N+2] = 0
    rows = np.empty((T+1, 2*N+1), dtype=np.uint8); rows[1] = s
    r0 = np.zeros(2*N+1, dtype=np.uint8); r0[N] = 1; rows[0] = r0
    for t in range(1, T):
        a = s[:-2]; b = s[1:-1]; c = s[2:]
        s[1:-1] = ((a==b)&(b==c)).astype(np.uint8)
        rows[t+1] = s
    return rows
rows = simulate(N,T)
V = lambda t,j: int(rows[t,j+N])
TM = 340
Sop = lambda W,t,j: W(abs(j)//2) if abs(j)<=2*(t+2) else 1  # conceptual only

# P(t): V(2t+1,j) = V(t, |j|//2)
badP = []
for t in range(1, TM//2):
    for j in range(-(2*t+1), 2*t+2):
        if V(2*t+1,j) != V(t, abs(j)//2): badP.append((t,j))
print("P(t): V_{2t+1}(j)=V_t(|j|//2) failures:", len(badP), badP[:4])

# even formula
badE = []
for t in range(2, TM//2):
    if V(2*t,0)!=1: badE.append((t,0))
    for j in range(1,t+2):
        if V(2*t,2*j) != (1 if V(t-1,j-1)==V(t-1,j) else 0): badE.append((t,j))
    for j in range(0,t+2):
        if V(2*t,2*j+1) != (1 if V(t-1,j)==V(t-1,j+1) else 0): badE.append((t,j))
print("even-time local formula failures:", len(badE), badE[:4])

# edge quantities
def E(t):
    return set(j for j in range(-t-2,t+3) if V(t,j)!=V(t,j+1))
def R(t): return set(j for j in E(t) if j>=0)
def dR(s):
    return set(j for j in range(0,300) if ((j in s) != ((j-1) in s)))
bad = [t for t in range(1,TM//2) if R(2*t+1)!=set(2*r+1 for r in R(t))]
bad += [t for t in range(2,TM//2) if R(2*t)!=set(2*r for r in dR(R(t-1)))]
print("R recursions failures:", len(bad))
bad = [t for t in range(0,TM) if (V(t,0)!=V(t,1)) != (((t+2)&(t+1))==0)]
print("e_t(0)=1 iff t+2=2^k failures:", len(bad))
bad = [t for t in range(0,TM) if V(t,0)!= (0 if (((t+1)&t)==0 and t>0) else 1)]
print("V_t(0)=0 iff t=2^k-1 failures:", len(bad))
# full alternating states at t=2^k-2 ; E_t = {j: |j|<=t+1, parity}
def alt(t):
    return set(j for j in range(-t-1,t+2) if (j%2 == ((t+1)%2 if j<0 else t%2)))
bad=[]
for k in range(1,9):
    t=2**k-2
    if E(t)!=alt(t): bad.append(t)
print("full-alternating at t=2^k-2 failures:", bad)
# counts
bad=[]
for t in range(1,TM//2):
    if len(E(2*t)) != 2*len(E(t-1)): bad.append(("even",t))
    if len(E(2*t+1)) != 2*len(E(t)): bad.append(("odd",t))
print("|E| doubling failures:", bad[:5])
# parent's (1)
bad=[t for t in range(1,TM) if V(t,0) != 1 - (V(t-1,0)!=V(t-1,1))]
print("state_t(0)=1-e_{t-1}(0) failures:", bad[:5])
# base cases
print("V_1:", [V(1,j) for j in range(-4,5)], " V_3=S(V_1):", all(V(3,j)==V(1,abs(j)//2) for j in range(-4,5)))
print("V_2:", [V(2,j) for j in range(-4,5)], " V_5=S(V_2):", all(V(5,j)==V(2,abs(j)//2) for j in range(-6,7)))
