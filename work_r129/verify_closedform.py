
import numpy as np, sys
sys.stdout.reconfigure(encoding="utf-8")
N, T = 2400, 1150
def simulate(N,T):
    s=np.ones(2*N+1,dtype=np.uint8); s[N-1:N+2]=0
    rows=np.empty((T+1,2*N+1),dtype=np.uint8); rows[1]=s
    r0=np.zeros(2*N+1,dtype=np.uint8); r0[N]=1; rows[0]=r0
    for t in range(1,T):
        a=s[:-2]; b=s[1:-1]; c=s[2:]
        s[1:-1]=((a==b)&(b==c)).astype(np.uint8)
        rows[t+1]=s
    return rows
rows=simulate(N,T)
V=lambda t,j: int(rows[t,j+N])
def r_of(t): 
    return t - (1 << (t.bit_length()-1))
def closed(t,j):
    if t==0: return 1 if j==0 else 0
    if abs(j)>t: return 1
    d = t - abs(j)
    m = d//2
    return 1 - (1 if (m & r_of(t))==m else 0)
bad=[]
for t in range(1, T+1):
    for j in range(-t, t+1):
        if V(t,j)!=closed(t,j): bad.append((t,j,V(t,j),closed(t,j)))
print("closed form x(t,j)=1-[|j|<=t and floor((t-|j|)/2) submask r(t)] failures:", len(bad), bad[:5])
# depth form
bad2=[(t,d) for t in range(1,300) for d in range(0,t+1) if V(t,t-d)!=1-(1 if (((d//2)&r_of(t))==(d//2)) else 0)]
print("depth form failures:", len(bad2), bad2[:5])
# counts
print("|Z(t) cap [0,t]| = 2^popcount(t):", all(sum(1 for j in range(0,t+1) if V(t,j)==0)==2**bin(t).count('1') for t in range(1,600)))
print("|E_t| = 2^popcount(t+1):", all(sum(1 for j in range(-t-1,t+2) if V(t,j)!=V(t,j+1))==2**bin(t+1).count('1') for t in range(0,600)))
# era recursion for Z(t) cap [0,inf)
def Rz(t):
    return set(j for j in range(0,t+1) if V(t,j)==0)
bad3=[]
for K in range(1,11):
    for m in range(0,2**K):
        t=2**K+m
        if t>T: continue
        if m < 2**(K-1):
            pred = set(2**(K-1)+x for x in Rz(t-2**(K-1)))
        else:
            pred = Rz(m) | set(2**K+x for x in Rz(m))
        # mirror: the claimed recursion is for the right half only
        if Rz(t)!=pred: bad3.append((t,m))
print("era recursion (right half of Z) failures:", len(bad3), bad3[:6])
