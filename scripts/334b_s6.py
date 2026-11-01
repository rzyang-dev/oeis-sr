
import random
def bits(r): return [i for i in range(r.bit_length()) if (r>>i)&1]
def subm(r):
    out=[]; m=r
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&r
    return out
def N(r): return 2**len(bits(r))
def s(r,k): return sum(2**(k*i) for i in bits(r))
def Pj(r,j): return sum(m**j for m in subm(r))
# search for r, r' with same (N,s1,s2,s4) but different P6
from collections import defaultdict
g=defaultdict(list)
random.seed(1)
cands=list(range(1,1<<18,7))+[random.randrange(1,1<<24) for _ in range(200000)]
for r in cands:
    g[(N(r),s(r,1),s(r,2),s(r,4))].append(r)
coll=[v for v in g.values() if len(v)>1]
print("groups:",len(g)," colliding groups:",len(coll))
if coll:
    for v in coll[:3]:
        print("  r values:",v[:4],"  P6:",[Pj(r,6) for r in v[:4]], "  P6/N:",[Pj(r,6)//N(r) for r in v[:4]])
else:
    print("  no collision found -> invariants (N,s1,s2,s4) separate all sampled r")
    print("  => 无法用此法判定 s6 是否必要（需要更大范围或符号论证）")
