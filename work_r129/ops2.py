
import sys
sys.stdout.reconfigure(encoding="utf-8")
def g(W,k): return W.get(abs(k), 1)
def Phi_on(W, hi):
    return {j: (1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0, hi+1)}
def S_on(W, hi):
    return {j: W.get(abs(j)//2,1) for j in range(0, hi+1)}
L=6
bad1=[]; bad2=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    # I1: Phi^2(S(S(W))) ?= S(Phi(S(W)))
    SS=S_on(S_on(W, 3*L+10), 5*L+10)
    L1=Phi_on(Phi_on(SS, 5*L+8), 5*L+6)
    PSW=Phi_on(S_on(W, 3*L+10), 5*L+8)
    R1=S_on(PSW, 5*L+10)
    if any(L1.get(p,1)!=R1.get(p,1) for p in range(0, 3*L+4)): bad1.append(bits)
    # I2: Phi^2(S(Phi(S(W)))) ?= S(Phi(Phi(S(W))))
    SFS=Phi_on(S_on(W,3*L+10), 5*L+8)
    L2=Phi_on(Phi_on(SFS, 5*L+8), 5*L+6)
    R2=S_on(Phi_on(Phi_on(S_on(W,3*L+10),5*L+8),5*L+6), 5*L+10)
    if any(L2.get(p,1)!=R2.get(p,1) for p in range(0, 3*L+4)): bad2.append(bits)
print("I1' Phi^2 S S = S Phi S      failures:", len(bad1), "/", 1<<(L+1), bad1[:6])
print("I2' Phi^2 S Phi S = S Phi^2 S failures:", len(bad2), "/", 1<<(L+1), bad2[:6])
