
import math
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def A(d): return sum(1 for u in range(d+1) if (u & ((u+d)//2)) == u)

# (b') p=3 algebraic equation, wider search
def find_eq(p, M, D, K):
    f=[A(d)%p for d in range(M)]
    powf=[[0]*M for _ in range(D+1)]
    powf[0][0]=1
    for i in range(1,D+1):
        pi=powf[i]; pm=powf[i-1]
        for a in range(M):
            s=0
            for b in range(min(a,len(f)-1)+1):
                s+=f[b]*pm[a-b]
            pi[a]=s%p
    ncol=(D+1)*(K+1)
    rows=[[0]*ncol for _ in range(M)]
    for n in range(M):
        for i in range(D+1):
            for j in range(K+1):
                if n-j>=0: rows[n][i*(K+1)+j]=powf[i][n-j]
    rk=0; piv=[]
    for c in range(ncol):
        pr=None
        for r in range(rk,M):
            if rows[r][c]%p: pr=r; break
        if pr is None: continue
        rows[rk],rows[pr]=rows[pr],rows[rk]
        inv=pow(rows[rk][c],p-2,p)
        rows[rk]=[(x*inv)%p for x in rows[rk]]
        for r in range(M):
            if r!=rk and rows[r][c]%p:
                fac=rows[r][c]
                rows[r]=[(rows[r][t]-fac*rows[rk][t])%p for t in range(ncol)]
        piv.append(c); rk+=1
    free=[c for c in range(ncol) if c not in piv]
    if not free: return None
    fc=free[0]; sol=[0]*ncol; sol[fc]=1
    for i,c in enumerate(piv): sol[c]=(-rows[i][fc])%p
    return sol,D,K
for p,D,K,M in ((3,8,14,400),(3,12,20,600),(5,8,14,400)):
    r=find_eq(p,M,D,K)
    if r is None:
        print("(b') p=%d D=%d K=%d : no relation found"%(p,D,K))
    else:
        sol,D2,K2=r; terms=[]
        for i in range(D2+1):
            for j in range(K2+1):
                c=sol[i*(K2+1)+j]
                if c: terms.append("%d x^%d f^%d"%(c,j,i))
        print("(b') p=%d : %s = 0"%(p," + ".join(terms)))

# (c) Delange / fractal: S(N)/N^{log2 3}
lg=math.log(3,2)
print("(c) S(N)/N^{log2 3} for N=2^k .. : (rows are k, cols are N=2^k + j*2^k/8)")
for k in range(6,15):
    vals=[]
    for j in range(9):
        N=(1<<k)+j*((1<<k)//8)
        S=sum(A(d) for d in range(N))
        vals.append(S/ (N**lg))
    print("  k=%2d "%k + " ".join("%.4f"%v for v in vals))

# (d) box-counting dimension of the dead set inside a block
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def subm(rr):
    out=[]; m=rr
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&rr
    return out
def shell(t):
    out=set()
    for m in subm(r(t)): out.add(t-2*m); out.add(t-2*m-1)
    return out
print("(d) counts of dead cells with d < 2^j inside block k=14  vs  2*3^j")
Sset=set()
for t in range(1<<14,1<<15):
    for d in shell(t): Sset.add((t,d))
for j in range(4,15):
    c=sum(1 for (t,d) in Sset if d < (1<<j))
    print("   j=%2d  count=%8d   3^j=%8d  ratio=%.4f"%(j,c,3**j,c/3**j))
