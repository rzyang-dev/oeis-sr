
import sys
sys.stdout.reconfigure(encoding="utf-8")
# half-line model with even extension; X on j>=0, 1-tail
def g(W,k): return W.get(abs(k), 1)
def Phi(W, hi):
    return {j: (1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0, hi+1)}
def S(W, hi):
    return {j: W.get(abs(j)//2,1) for j in range(0, hi+1)}
def build_even(X, hi):
    # W(0)=1 ; W(2j)=[X(j-1)=X(j)] (j>=1) ; W(2j+1)=[X(j)=X(j+1)] (j>=0)
    W={0:1}
    for j in range(1, hi//2+2):
        W[2*j] = 1 if X.get(j-1,1)==X.get(j,1) else 0
    for j in range(0, hi//2+2):
        W[2*j+1] = 1 if X.get(j,1)==X.get(j+1,1) else 0
    return {k:v for k,v in W.items() if k<=hi}
L=6
bad=[]
for bits in range(1<<(L+1)):
    X={j:(bits>>j)&1 for j in range(0,L+1)}
    W=build_even(X, 3*L+12)
    lhs=Phi(Phi(S(W, 3*L+12), 3*L+10), 3*L+8)
    rhs=S(Phi(W, 3*L+10), 3*L+12)
    if any(lhs.get(p,1)!=rhs.get(p,1) for p in range(0, 2*L+2)):
        bad.append((bits, [p for p in range(0,2*L+2) if lhs.get(p,1)!=rhs.get(p,1)][:3]))
print("case (b) identity Phi^2 S W = S Phi W for W = even-row built from X:")
print("  failures:", len(bad), "/", 1<<(L+1), bad[:5])
