
import sys
sys.stdout.reconfigure(encoding="utf-8")
# half-line model: W on j>=0, even extension, 1 outside the enumerated window
def g(W,k): return W.get(abs(k), 1)
def Phi(W, upto):
    return {j: (1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0, upto)}
def S(W, upto):
    return {j: W.get(abs(j)//2,1) for j in range(0, upto)}
def good(W, L, pcheck=16):
    SW=S(W, 3*L+6); P2=Phi(Phi(SW, 2*L+6), 2*L+4)
    PW=Phi(W, 2*L+4); SP=S(PW, 3*L+6)
    return all(P2.get(p,1)==SP.get(p,1) for p in range(0,pcheck+1))
L=8
bad=[]
goodset=[]
for bits in range(1<<(L+1)):
    W={j:(bits>>j)&1 for j in range(0,L+1)}
    if good(W,L):
        goodset.append(bits)
        PW=Phi(W, L)
        # PW is good on [0..L-1] with 1 tail; check it
        if not good(PW, L-1):
            bad.append(bits)
print("good count:", len(goodset), "of", 1<<(L+1))
print("closure failures Phi(good)->good:", len(bad), bad[:5])
# check V1 is good
V1={0:0,1:0,2:1,3:1,4:1,5:1,6:1,7:1,8:1}
print("V_1 good:", good(V1,L))
