
from fractions import Fraction as F

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))
def wt(n): return bin(n).count("1")
def bits(m): return [i for i in range(m.bit_length()) if (m >> i) & 1]

def subm(r):
    out=[]; m=r
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&r
    return out

def shell(t):
    rt=r(t); out=[]
    for m in subm(rt):
        out.append(t-2*m); out.append(t-2*m-1)
    return out

def cardS(t): return 2*(1<<wt(r(t)))

def zc(c): return lambda t: sum(c(d) for d in shell(t))
def cardS_seq(t): return cardS(t)

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
                for j in range(col,ncol):
                    rows[i][j]=F(rows[i][j])-f*F(rows[rk][j])
        rk+=1
        if rk==m: break
    return rk

def krank(a,KMAX=6,M=30):
    need=(1<<KMAX)*(M+2)+4
    vals=[a(t) for t in range(need+1)]
    out=[]
    for K in (4,5,6):
        rows=[]
        for k in range(K+1):
            for j in range(1<<k):
                rows.append([vals[(1<<k)*n+j] for n in range(1,M+1)])
        out.append(rank(rows,M))
    return out

def fitdeg(f, lo=1, hi=40):
    v=[f(d) for d in range(lo,hi+1)]
    for deg in range(0,8):
        w=v[:]; ok=True
        for _ in range(deg):
            w=[w[i+1]-w[i] for i in range(len(w)-1)]
        if all(x==0 for x in w[:len(w)-deg-2]): return deg
    return None

tests = {
 "c=1 (ray)":                lambda d: 1,
 "c=2 (line, no patch)":     lambda d: 2,
 "c=d+1 (orthant vN)":       lambda d: d+1,
 "c=2d+1 (orthant Moore)":   lambda d: 2*d+1,
 "c=3d+2":                   lambda d: 3*d+2,
 "c=d^2":                    lambda d: d*d,
 "c=d^2+d+1":                lambda d: d*d+d+1,
 "c=6d^2+2":                 lambda d: 6*d*d+2,
 "c=d^3":                    lambda d: d**3,
 "c=d^4":                    lambda d: d**4,
 "c=wt(d)":                  lambda d: wt(d),
 "c=d+wt(d)":                lambda d: d+wt(d),
 "c=3^wt(d)":                lambda d: 3**wt(d),
 "c=(-1)^wt(d)":             lambda d: (-1)**wt(d),
 "c=2^d (tree b=2)":         lambda d: 2**d,
 "c=floor(d^1.585)":         lambda d: int(d**1.585),
 "c=d!":                     lambda d: __import__('math').factorial(min(d,20)),
}
print("| c | deg(1..40) | rank(c) | rank(Z_c) |")
print("|---|---|---|---|")
for name,c in tests.items():
    rc=krank(c); rz=krank(zc(c))
    print(f"| {name} | {fitdeg(c)} | {rc} | {rz} |")
