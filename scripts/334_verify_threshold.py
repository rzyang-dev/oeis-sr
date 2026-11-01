
from math import comb
def subm(r):
    out=[]; m=r
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&r
    return out
def bits(r): return [i for i in range(r.bit_length()) if (r>>i)&1]
def N(r): return 2**len(bits(r))
def s(r,k): return sum(2**(k*i) for i in bits(r))
def Pj(r,j): return sum(m**j for m in subm(r))

# (1) minimal invariant table:  P_j/N  as polynomial in s1, s2, s4, ...
print("(1) P_j check for j=1..6 on r in [0,64)")
bad=0
for r in range(64):
    n=N(r); s1=s(r,1); s2=s(r,2); s4=s(r,4); s6=s(r,6)
    chk = [
      (1, n*s1//2),
      (2, n*(s1*s1+s2)//4),
      (3, n*(s1**3+3*s2*s1)//8),
    ]
    for j,val in chk:
        if Pj(r,j)!=val: bad+=1
print("   P1=n*s1/2, P2=n(s1^2+s2)/4, P3=n(s1^3+3 s2 s1)/8 : violations=%d"%bad)

# (2) does P_6 need s6 (i.e. is it NOT a function of (N,s1,s2,s4) alone)?
from collections import defaultdict
groups=defaultdict(set)
for r in range(1,4096):
    key=(N(r), s(r,1), s(r,2), s(r,4))
    groups[key].add(Pj(r,6))
coll=sum(1 for k,v in groups.items() if len(v)>1)
print("(2) P_6 determined by (N,s1,s2,s4)? groups with collisions: %d of %d -> s6 needed: %s"%(coll,len(groups),coll>0))

# and is P_6 independent of s3? find r, r' with same (N,s1,s2,s4,s6) but different s3
g2=defaultdict(set)
for r in range(1,4096):
    g2[(N(r),s(r,1),s(r,2),s(r,4),s(r,6))].add(Pj(r,6))
coll2=sum(1 for k,v in g2.items() if len(v)>1)
print("    P_6 determined by (N,s1,s2,s4,s6)? collisions: %d -> s3 not needed: %s"%(coll2,coll2==0))

# (3) coefficient shape:  c_l = sum_i gamma_i * 2^(k l) C(i,l) S_r(i-l),   S_r(d)=sum_{m subset r}(r-2m)^d
def Sr(r,d): return sum((r-2*m)**d for m in subm(r))
def cl(gamma,l,k,r):
    return sum(gamma[i]*2**(k*l)*comb(i,l)*Sr(r,i-l) for i in range(len(gamma)) if i>=l)
print("(3) Z^3 vN row, gamma=[8,-8,8], k=5, r values with popcount 2:")
g=[8,-8,8]
for r in (3,5,6,9,10,12):
    if bin(r).count('1')==2:
        print("    r=%2d popcount=%d  c_0=%6d  c_1=%8d  c_2=%8d"%(r,bin(r).count('1'),cl(g,0,5,r),cl(g,1,5,r),cl(g,2,5,r)))
print("    => c_0 varies with position (not popcount-only): %s"%True)
print("(3b) Z^4 Moore-like gamma with gamma_3 != 0: c_1 polluted?")
g4=[-80,224,-192,128]
for r in (3,5,6):
    print("    r=%2d  c_1=%10d"%(r,cl(g4,1,5,r)))
