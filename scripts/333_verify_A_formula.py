
from math import comb
from fractions import Fraction as F

# M0, M1 as matrices over rows i (0..N), cols l (0..N)
N=7
def M0():
    return [[2**i if l==i else 0 for l in range(N+1)] for i in range(N+1)]
def M1():
    return [[comb(i,l)*2**(l+1) if (l<=i and (i-l)%2==0) else 0 for l in range(N+1)] for i in range(N+1)]
def matmul(A,B):
    n=len(A); C=[[0]*(n) for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if A[i][k]:
                for j in range(n):
                    if B[k][j]: C[i][j]+=A[i][k]*B[k][j]
    return C
def subm(j):
    out=[]; m=j
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&j
    return out
def S(j,d): return sum((j-2*m)**d for m in subm(j))
def wt(n): return bin(n).count("1")

def Aprod(k,j):
    # A(k,j) = M_{b0} * M_{b1} * ... with b0 = LSB
    A=[[1 if i==l else 0 for l in range(N+1)] for i in range(N+1)]
    for t in range(k):
        b=(j>>t)&1
        A=matmul(M1() if b else M0(), A)
    return A

print("(V1) closed form  A(k,j)[i][l] = 2^(k*l) * C(i,l) * S_j(i-l)")
bad=0; tot=0
for k in range(1,5):
    for j in range(1<<k):
        A=Aprod(k,j)
        for i in range(N+1):
            for l in range(N+1):
                tot+=1
                pred = 2**(k*l)*comb(i,l)*S(j,i-l) if i>=l else 0
                if A[i][l]!=pred:
                    bad+=1
                    if bad<4: print("   MISMATCH k=%d j=%d i=%d l=%d  got=%d pred=%d"%(k,j,i,l,A[i][l],pred))
print("   %d entries, %d mismatches"%(tot,bad))

print("(V2) S_j(odd)=0  and  S_j(0)=2^wt(j), j<64, odd d<=5")
bad=0
for j in range(64):
    if S(j,0)!=2**wt(j): bad+=1
    for d in (1,3,5):
        if S(j,d)!=0: bad+=1
print("   violations:",bad)
