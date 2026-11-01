
from math import comb
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def shell(t):
    rt=r(t); out=set(); m=rt
    while True:
        out.add(t-2*m); out.add(t-2*m-1)
        if m==0: break
        m=(m-1)&rt
    return out
bad=0; tot=0
for t in range(1,40):
    S=shell(t)
    for d in range(0,t+1):
        tot+=1
        s=(t+d)//2
        want = 1 if (s<=t and comb(t,s)%2==1) else 0
        if want != (1 if d in S else 0): bad+=1
print("Sierpinski identity  [d in shell(t)] = C(t,(t+d)/2) mod 2 : %d cases, %d violations"%(tot,bad))
