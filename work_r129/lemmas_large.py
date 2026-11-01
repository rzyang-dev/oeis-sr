
import sys
sys.stdout.reconfigure(encoding="utf-8")
def g(W,k): return W.get(abs(k),1)
def P(W,hi): return {j:(1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0,hi+1)}
def St(W,hi): return {j: W.get(abs(j)//2,1) for j in range(0,hi+1)}
def build_even(X,hi):
    W={0:1}
    for j in range(1,hi//2+2): W[2*j]=1 if X.get(j-1,1)==X.get(j,1) else 0
    for j in range(0,hi//2+2): W[2*j+1]=1 if X.get(j,1)==X.get(j+1,1) else 0
    return {k:v for k,v in W.items() if k<=hi}
for L in (9,10):
    b1=b2=0
    for bits in range(1<<(L+1)):
        X={j:(bits>>j)&1 for j in range(0,L+1)}
        SS=St(St(X,4*L+24),4*L+28); l=P(P(SS,4*L+28),4*L+26); r=St(P(St(X,4*L+24),4*L+26),4*L+28)
        if any(l.get(p,1)!=r.get(p,1) for p in range(0,2*L+4)): b1+=1
        W=build_even(X,4*L+28)
        l2=P(P(St(W,4*L+28),4*L+26),4*L+24); r2=St(P(W,4*L+26),4*L+28)
        if any(l2.get(p,1)!=r2.get(p,1) for p in range(0,2*L+4)): b2+=1
    print(f"L={L}: patterns={1<<(L+1)}  J1 failures={b1}  J2 failures={b2}")
