
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
def E(t):
    return set(j for j in range(-t-2,t+3) if V(t,j)!=V(t,j+1))
bad=0
for t in range(1, 575):
    for j in range(-(2*t+1), 2*t+2):
        if V(2*t+1,j)!=V(t,abs(j)//2): bad+=1
print("3. C(t): V_{2t+1}(j)=V_t(|j|//2) failures (t<=574):", bad)
bad=0
for t in range(2,576):
    if V(2*t,0)!=1: bad+=1
    for j in range(1,t+2):
        if V(2*t,2*j)!=(1 if V(t-1,j-1)==V(t-1,j) else 0): bad+=1
    for j in range(0,t+2):
        if V(2*t,2*j+1)!=(1 if V(t-1,j)==V(t-1,j+1) else 0): bad+=1
print("4. even-row formula failures (t<=575):", bad)
R=lambda t: set(j for j in E(t) if j>=0)
def dR(s): return set(j for j in range(0,2000) if ((j in s)!=((j-1) in s)))
bad=0
for t in range(1,575):
    if R(2*t+1)!=set(2*r+1 for r in R(t)): bad+=1
for t in range(2,575):
    if R(2*t)!=set(2*r for r in dR(R(t-1))): bad+=1
print("5. R recursions failures:", bad)
print("6a. V_t(0)=0 iff t=2^k-1, t<=1100:", all((V(t,0)==0)==(((t+1)&t)==0 and t>0) for t in range(0,1101)))
print("6b. e_t(0)=1 iff t+2=2^k, t<=1100:", all(((V(t,0)!=V(t,1)))==(((t+2)&(t+1))==0) for t in range(0,1101)))
bad=0
for t in range(1,575):
    if len(E(2*t))!=2*len(E(t-1)): bad+=1
    if len(E(2*t+1))!=len(E(t)): bad+=1
print("7. counts failures:", bad, " |E_t| t=0..16:", [len(E(t)) for t in range(17)])
bad=[]
for k in range(1,11):
    t=2**k-2
    alt=set(j for j in range(-t-1,t+2) if (j%2 == ((t+1)%2 if j<0 else t%2)))
    if E(t)!=alt or R(t)!=set(range(0,t+1,2)): bad.append(t)
print("8. full alternating at t=2^k-2, k<=10, failures:", bad)
for k in (3,4,5):
    ok=[m for m in range(1,13) if all(V(2**k+m-1,j)==V(m-1,j) for j in range(-m,m+1))]
    print(f"9. naive identity state(2^{k}+m-1)=state(m-1) on |j|<=m holds for m in {ok}")
print("10. rows V_1..V_6 on j=-6..6:")
for t in range(1,7):
    print("   t=%d: "%t + "".join(str(V(t,j)) for j in range(-6,7)))
