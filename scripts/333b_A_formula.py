
from math import comb
N=7
def M0(): return [[2**i if l==i else 0 for l in range(N+1)] for i in range(N+1)]
def M1(): return [[comb(i,l)*2**(l+1) if (l<=i and (i-l)%2==0) else 0 for l in range(N+1)] for i in range(N+1)]
def matmul(A,B):
    n=len(A); C=[[0]*n for _ in range(n)]
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

def Aprod(k,j,lsb_left=True):
    A=[[1 if i==l else 0 for l in range(N+1)] for i in range(N+1)]
    rng = range(k) if lsb_left else range(k-1,-1,-1)
    if lsb_left:
        for t in range(k-1,-1,-1):
            A=matmul(M1() if ((j>>t)&1) else M0(), A)
    else:
        for t in range(k):
            A=matmul(M1() if ((j>>t)&1) else M0(), A)
    return A

for label,lsb in (("b0 leftmost (recursion order)",True),("b0 rightmost",False)):
    bad=0; tot=0
    for k in range(1,5):
        for j in range(1<<k):
            A=Aprod(k,j,lsb)
            for i in range(N+1):
                for l in range(N+1):
                    tot+=1
                    pred = 2**(k*l)*comb(i,l)*S(j,i-l) if i>=l else 0
                    if A[i][l]!=pred: bad+=1
    print("order [%s]: %d entries, %d mismatches"%(label,tot,bad))
