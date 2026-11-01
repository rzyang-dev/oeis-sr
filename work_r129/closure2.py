
import sys
sys.stdout.reconfigure(encoding="utf-8")
def g(W,k): return W.get(abs(k), 1)
def Phi_on(W, hi):
    return {j: (1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0, hi+1)}
def S_on(W, hi):
    return {j: W.get(abs(j)//2,1) for j in range(0, hi+1)}
def good(W, L):
    # W: dict on [0..L], 1 outside.  check identity for p in [0, 2L+2]
    SW=S_on(W, 2*L+8); P2=Phi_on(Phi_on(SW, 2*L+6), 2*L+4)
    PW=Phi_on(W, 2*L+4); SP=S_on(PW, 2*L+8)
    return all(P2.get(p,1)==SP.get(p,1) for p in range(0, 2*L+3))
L=7
goodset=[]; bad=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    if good(W,L):
        goodset.append((bits,W))
        PW = Phi_on(W, L+1)          # true values on [0..L+1], 1 outside
        if not good(PW, L+1): bad.append(bits)
print("L=7 good:", len(goodset), "/", 1<<(L+1), " closure failures:", len(bad), bad[:6])
V1={0:0,1:0,2:1,3:1,4:1,5:1,6:1,7:1}
print("V_1 good:", good(V1,L))
# what do good states look like: print a few
print("sample good patterns (j=0..L):")
for bits,W in goodset[:12]:
    print("  ", "".join(str(W[j]) for j in range(0,L+1)))
