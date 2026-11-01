
import sys
sys.stdout.reconfigure(encoding="utf-8")
# Test F^2 o S = S o F on restricted classes of even configurations.
# U given on j>=0; even extension U(-j)=U(j); U=1 outside window.
def F(conf, lo, hi):
    return {j: (1 if (conf.get(j-1,1)==conf.get(j,1)==conf.get(j+1,1)) else 0) for j in range(lo, hi)}
def S(U, hi):
    out={}
    for j in range(0,hi+1):
        v=U.get(j,1)
        if j==0: out[-1]=out[0]=out[1]=v
        else:
            for p in (2*j,2*j+1,-2*j,-2*j-1): out[p]=v
    return out
def even_ext(U, lo, hi):
    d={}
    for j in range(lo, hi+1): d[j]=U.get(abs(j),1)
    return d
M=5  # U on 0..M
res={'O':[0,0], 'E':[0,0], 'all':[0,0]}
first={}
for bits in range(1<<(M+1)):
    U={j:(bits>>j)&1 for j in range(0,M+1)}
    inO = all(U[2*j]==U[2*j+1] for j in range(0,(M)//2+1) if 2*j+1<=M)
    inE = all(U[2*j+1]==U[2*j+2] for j in range(0,(M)//2+1) if 2*j+2<=M)
    # build S(U) on [-..], F twice, and S(F(U))
    SU = S(U, M)
    SUe = even_ext(SU, -4*M-4, 4*M+4)
    F1 = F(SUe, -4*M-2, 4*M+2)
    F2 = F(F1, -4*M, 4*M)
    Ufull = even_ext(U, -M, M)
    FU = F(Ufull, -M+1, M-1)
    SFU = S(FU, M)
    sfue = even_ext(SFU, -4*M-4, 4*M+4)
    bad = any(F2.get(p,1)!=sfue.get(p,1) for p in range(-2*M-2, 2*M+3))
    for key,cond in (('O',inO),('E',inE),('all',True)):
        if cond:
            res[key][1]+=1
            if bad:
                res[key][0]+=1
                first.setdefault(key,(U,))
print("class-restricted F^2 o S = S o F  (failures / total):", res)
print("first failures:", first)
