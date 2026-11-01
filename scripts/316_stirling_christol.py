
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def A(d): return sum(1 for u in range(d+1) if (u & ((u+d)//2)) == u)

# (a) Stirling second kind mod 2, corrected offset
N=120
S=[[0]*(N+1) for _ in range(N+1)]
S[0][0]=1
for n in range(1,N+1):
    for k in range(1,n+1):
        S[n][k]=S[n-1][k-1]+k*S[n-1][k]
odd=[sum(1 for k in range(n+1) if S[n][k]%2==1) for n in range(N+1)]
print("(a) A(d) == #{k : S(d+1,k) odd} for d<=%d : %s"%(N-1, all(A(d)==odd[d+1] for d in range(N))))
print("    A(0..11)      =",[A(d) for d in range(12)])
print("    odd(1..12)    =",odd[1:13])

# (b) Christol: algebraic equation for  sum A(d) x^d  over F_p
def series(p, M):
    return [A(d)%p for d in range(M)]
def find_eq(p, M, D, K):
    # search c[i][j] with sum_{i<=D, j<=K} c[i][j] x^j f^i = 0, f = series, over F_p
    f=series(p,M)
    powf=[[0]*M for _ in range(D+1)]
    powf[0][0]=1
    for i in range(1,D+1):
        for a in range(M):
            s=0
            for b in range(a+1):
                s=(s+f[b]*powf[i-1][a-b])%p
            powf[i][a]=s
    rows=[]
    for n in range(M):
        row=[]
        for i in range(D+1):
            for j in range(K+1):
                row.append(powf[i][n-j]%p if n-j>=0 else 0)
        rows.append(row)
    ncol=(D+1)*(K+1)
    # gaussian elimination over F_p
    piv=[]; rk=0
    for c in range(ncol):
        pr=None
        for r in range(rk,len(rows)):
            if rows[r][c]%p: pr=r; break
        if pr is None: continue
        rows[rk],rows[pr]=rows[pr],rows[rk]
        inv=pow(rows[rk][c],p-2,p)
        rows[rk]=[(x*inv)%p for x in rows[rk]]
        for r in range(len(rows)):
            if r!=rk and rows[r][c]%p:
                fac=rows[r][c]
                rows[r]=[(rows[r][t]-fac*rows[rk][t])%p for t in range(ncol)]
        piv.append(c); rk+=1
        if rk==len(rows): break
    if rk==ncol: return None
    # find a free column
    free=[c for c in range(ncol) if c not in piv]
    if not free: return None
    fc=free[0]
    sol=[0]*ncol; sol[fc]=1
    for i,c in enumerate(piv):
        sol[c]=(-rows[i][fc])%p
    return sol, D, K

for p in (2,3):
    for (D,K) in ((3,6),(4,8),(5,10)):
        r=find_eq(p,140,D,K)
        if r:
            sol,D2,K2=r
            terms=[]
            for i in range(D2+1):
                for j in range(K2+1):
                    c=sol[i*(K2+1)+j]
                    if c: terms.append("%d*x^%d*f^%d"%(c,j,i))
            print("(b) p=%d  deg f<=%d, x-deg<=%d :  %s = 0  (mod %d)"%(p,D2,K2," + ".join(terms),p))
            break
