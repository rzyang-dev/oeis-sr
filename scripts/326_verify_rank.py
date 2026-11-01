
from fractions import Fraction as F
from math import comb
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def subm(rr):
    out=[]; m=rr
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&rr
    return out
def shell(t):
    s=set()
    for m in subm(r(t)): s.add(t-2*m); s.add(t-2*m-1)
    return s
def rank(rows, ncol):
    rows=[row[:ncol] for row in rows]; m=len(rows); rk=0
    for col in range(ncol):
        piv=None
        for i in range(rk,m):
            if rows[i][col]!=0: piv=i; break
        if piv is None: continue
        rows[rk],rows[piv]=rows[piv],rows[rk]
        pv=F(rows[rk][col])
        for i in range(rk+1,m):
            if rows[i][col]!=0:
                f=F(rows[i][col])/pv
                for j in range(col,ncol): rows[i][j]=F(rows[i][j])-f*F(rows[rk][j])
        rk+=1
        if rk==m: break
    return rk
def krank(a,K=6,M=30):
    need=(1<<K)*(M+2)+4
    vals=[a(t) for t in range(need+1)]
    out=[]
    for kk in (4,5,6):
        rows=[]
        for k in range(kk+1):
            for j in range(1<<k):
                rows.append([vals[(1<<k)*n+j] for n in range(1,M+1)])
        out.append(rank(rows,M))
    return out
def polyval(coef,x):
    v=0
    for c in reversed(coef): v=v*x+c
    return v
def Zc(coef): return lambda t: sum(polyval(coef,d) for d in shell(t))
def pcoef(coef):
    # p(x)=c(x)+c(x-1); compute coefficients
    n=len(coef)
    p=[0]*(n+1)
    for i,c in enumerate(coef):
        p[i]+=c            # c(x)
        # c(x-1) = sum c_i (x-1)^i ; expand (x-1)^i = sum_j C(i,j) x^j (-1)^(i-j)
        for j in range(i+1):
            p[j]+=c*comb(i,j)*((-1)**(i-j))
    while len(p)>1 and p[-1]==0: p.pop()
    return p
def dclose(p):
    S=set(i for i,c in enumerate(p) if c!=0)
    D=set()
    for i in S:
        for l in range(i%2, i+1, 2): D.add(l)
    return len(D)

# (A) rank(Phi_D) = floor(D/2)+1
print("(A) rank of a single pure moment Phi_D:")
for D in range(0,8):
    coef=[0]*(D+1); coef[D]=1
    print("   D=%d  measured=%s   floor(D/2)+1=%d"%(D,krank(Zc(coef))[2],D//2+1))

# (B) DClose formula on all small polynomials
print("(B) rank == #DClose(supp p) ?")
bad=[]; cnt=0
for a0 in range(-2,3):
  for a1 in range(-2,3):
    for a2 in range(-2,3):
      for a3 in range(-2,3):
        coef=[a0,a1,a2,a3]
        while len(coef)>1 and coef[-1]==0: coef.pop()
        p=pcoef(coef); pred=dclose(p)
        got=krank(Zc(coef))[2]; cnt+=1
        if got!=pred: bad.append((coef,p,got,pred))
print("   deg<=3, coefs in [-2,2]: %d cases, %d mismatches"%(cnt,len(bad)))
for b in bad[:6]: print("     c=%s  p=%s  measured=%d  DClose=%d"%b)
print("   old formula #supp(p): mismatches =", sum(1 for b in bad if b[2]!=sum(1 for c in b[1] if c!=0)) if bad else "n/a")
