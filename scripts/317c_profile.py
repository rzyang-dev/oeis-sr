
import math
N0=1<<16
f=[0]*(N0+2); f[1]=1
for n in range(2,N0+2):
    if n%2==0: f[n]=f[n//2]
    else: f[n]=f[n//2]+f[n//2+1]
A=[f[d]+f[d+1] for d in range(N0+1)]
pref=[0]*(N0+2)
for d in range(N0+1): pref[d+1]=pref[d]+A[d]
lg=math.log(3,2)
# F profile on [0,1): F(x) = S(floor(2^x))/N^{log2 3}
print("F profile (N=2^{12.5}) :")
for i in range(0,20):
    x=i/20
    e=12+x
    N=int(2**e)
    print("   x=%.2f  S(N)/N^log2 3 = %.5f"%(x, pref[N]/N**lg))
# Stirling check count
N=200
S=[[0]*(N+1) for _ in range(N+1)]; S[0][0]=1
for n in range(1,N+1):
    for k in range(1,n+1):
        S[n][k]=S[n-1][k-1]+k*S[n-1][k]
odd=[sum(1 for k in range(n+1) if S[n][k]%2==1) for n in range(N+1)]
print("Stirling check to 199:", all((f[d]+f[d+1])==odd[d+1] for d in range(N)))

# Christol mod 3: small search
def find_eq(p,M,D,K):
    F=[A[d]%p for d in range(M)]
    pw=[[0]*M for _ in range(D+1)]; pw[0][0]=1
    for i in range(1,D+1):
        for a in range(M):
            s=0
            for b in range(min(a,M-1)+1):
                s+=F[b]*pw[i-1][a-b]
            pw[i][a]=s%p
    ncol=(D+1)*(K+1)
    rows=[[0]*ncol for _ in range(M)]
    for n in range(M):
        for i in range(D+1):
            for j in range(K+1):
                if n-j>=0: rows[n][i*(K+1)+j]=pw[i][n-j]
    rk=0; piv=[]
    for c in range(ncol):
        pr=None
        for rr in range(rk,M):
            if rows[rr][c]%p: pr=rr; break
        if pr is None: continue
        rows[rk],rows[pr]=rows[pr],rows[rk]
        inv=pow(rows[rk][c],p-2,p)
        rows[rk]=[(x*inv)%p for x in rows[rk]]
        for rr in range(M):
            if rr!=rk and rows[rr][c]%p:
                fa=rows[rr][c]
                rows[rr]=[(rows[rr][t]-fa*rows[rk][t])%p for t in range(ncol)]
        piv.append(c); rk+=1
    free=[c for c in range(ncol) if c not in piv]
    if not free: return None
    fc=free[0]; sol=[0]*ncol; sol[fc]=1
    for i,c in enumerate(piv): sol[c]=(-rows[i][fc])%p
    return sol
for (p,D,K,M) in ((3,6,10,200),(3,9,16,320),(5,6,10,200)):
    s=find_eq(p,M,D,K)
    if s is None: print("p=%d D=%d K=%d : none"%(p,D,K))
    else:
        ts=[]
        for i in range(D+1):
            for j in range(K+1):
                c=s[i*(K+1)+j]
                if c: ts.append("%d x^%d f^%d"%(c,j,i))
        print("p=%d D=%d K=%d : %s = 0"%(p,D,K," + ".join(ts)))
