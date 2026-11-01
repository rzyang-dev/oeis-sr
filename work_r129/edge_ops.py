
import sys
sys.stdout.reconfigure(encoding="utf-8")
def Psi(r, hi):
    out={}
    for n in range(0, hi+1):
        if n==0: out[0] = (1-r.get(0,0)) * (r.get(0,0) ^ r.get(1,0))
        else: out[n] = (1-r.get(n,0)) * (r.get(n-1,0) ^ r.get(n+1,0))
    return out
def T(r, hi):
    return {2*n+1: r.get(n,0) for n in range(0, hi//2+1)}
L=6
bad=[]
for bits in range(1<<(L+1)):
    r={n:(bits>>n)&1 for n in range(0,L+1)}
    # T(Psi(r)) vs Psi^2(T(r))
    lhs = T(Psi(r, 2*L+6), 2*L+6)
    PTr = Psi(T(r, 2*L+8), 2*L+8)
    rhs = Psi(PTr, 2*L+6)
    if any(lhs.get(p,0)!=rhs.get(p,0) for p in range(0, 2*L+2)): bad.append(bits)
print("edge identity  T o Psi = Psi^2 o T  failures:", len(bad), "/", 1<<(L+1), bad[:8])
