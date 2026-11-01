
import sys
sys.stdout.reconfigure(encoding="utf-8")
# half-line model: W on j>=0, even extension W(-j)=W(j), 1 outside (W(j)=1 for j>L)
def Phi(W, j):
    def g(k): return W.get(abs(k), 1)
    return 1 if (g(j-1)==g(j)==g(j+1)) else 0
def step(W):
    return {j: Phi(W,j) for j in range(0, 40)}
def S(W):
    return {j: W.get(abs(j)//2,1) for j in range(0, 80)}
L=5
good=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    # Phi^2(S(W)) at p ; S(Phi(W)) at p
    SW=S(W); PSW=step(SW); P2SW=step(PSW)
    PW=step(W); SPW=S(PW)
    ok = all(P2SW.get(p,1)==SPW.get(p,1) for p in range(0,16))
    if ok: good.append(bits)
print("PASS: Phi^2 o S = S o Phi  ->", len(good), "of", 1<<(L+1))
for bits in good:
    print("pass:", [(bits>>j)&1 for j in range(0,L+1)])
