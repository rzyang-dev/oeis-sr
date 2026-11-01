
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
def V(t,j): return int(rows[t,j+N])
def Phi(W):
    n=len(W)
    def g(k):
        if k<0: return W[-k] if -k<n else 1
        return W[k] if k<n else 1
    return [ 1 if (g(j-1)==g(j)==g(j+1)) else 0 for j in range(n) ]
def S(W):
    n=len(W)
    return [ W[j//2] if (j//2)<n else 1 for j in range(n) ]
def rec(t, jmax):
    m = jmax+1
    if t==1: return [0 if j<=1 else 1 for j in range(m)]
    if t==2: return [1 if (j==0 or j>=3) else 0 for j in range(m)]
    if t==3: return S(rec(1, m))[:m]
    if t%2==1: return S(rec((t-1)//2, m))[:m]
    return Phi(S(rec(t//2-1, m)))[:m]
bad=[]
for t in range(1, T+1):
    jm = min(t, N-t-5)
    if jm < 0: continue
    R = rec(t, jm)
    if len(R)<jm+1 or any(R[j]!=V(t,j) for j in range(0,jm+1)):
        bad.append(t)
print("end-to-end recursion failures t<=%d:"%T, bad[:10], "count", len(bad))

def g(W,k): return W.get(abs(k),1)
def P(W,hi): return {j:(1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0,hi+1)}
def St(W,hi): return {j: W.get(abs(j)//2,1) for j in range(0,hi+1)}
def build_even(X,hi):
    W={0:1}
    for j in range(1,hi//2+2): W[2*j]=1 if X.get(j-1,1)==X.get(j,1) else 0
    for j in range(0,hi//2+2): W[2*j+1]=1 if X.get(j,1)==X.get(j+1,1) else 0
    return {k:v for k,v in W.items() if k<=hi}
L=8
b1=b2=0
for bits in range(1<<(L+1)):
    X={j:(bits>>j)&1 for j in range(0,L+1)}
    SS=St(St(X, 4*L+20), 4*L+24); l=P(P(SS,4*L+24),4*L+22); r=St(P(St(X,4*L+20),4*L+22),4*L+24)
    if any(l.get(p,1)!=r.get(p,1) for p in range(0,2*L+3)): b1+=1
    W=build_even(X,4*L+24)
    l2=P(P(St(W,4*L+24),4*L+22),4*L+20); r2=St(P(W,4*L+22),4*L+24)
    if any(l2.get(p,1)!=r2.get(p,1) for p in range(0,2*L+3)): b2+=1
print("J1 failures:", b1, "/", 1<<(L+1), "  J2 failures:", b2, "/", 1<<(L+1))
