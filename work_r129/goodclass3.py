
import sys
sys.stdout.reconfigure(encoding="utf-8")
L=9
def Phi(W, j):
    def g(k): return W.get(abs(k), 1)
    return 1 if (g(j-1)==g(j)==g(j+1)) else 0
def step(W, upto=60):
    return {j: Phi(W,j) for j in range(0, upto)}
def S(W, upto=120):
    return {j: W.get(abs(j)//2,1) for j in range(0, upto)}
good=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    SW=S(W); P2SW=step(step(SW)); SPW=S(step(W))
    if all(P2SW.get(p,1)==SPW.get(p,1) for p in range(0,17)):
        good.append(bits)
print("PASS Phi^2 S = S Phi :", len(good), "/", 1<<(L+1))
for bits in good:
    print("pass:", "".join(str((bits>>j)&1) for j in range(0,L+1)))
