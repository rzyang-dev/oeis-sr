
from math import comb
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]

N=800
# Stirling2 mod 2 via DP (row by row, only parity needed)
S=[[0]*(N+2) for _ in range(N+2)]
S[0][0]=1
for n in range(1,N+2):
    prev=S[n-1]; cur=S[n]
    for k in range(1,n+1):
        cur[k]=(prev[k-1]+ (k%2)*prev[k])%2

# C1: criterion  S(n,k) odd  <=>  (n-k) & ((k-1)//2) == 0
bad=0; tot=0
for n in range(1,N+1):
    for k in range(1,n+1):
        tot+=1
        if S[n][k] != (1 if (((n-k) & ((k-1)//2))==0) else 0): bad+=1
print("C1 parity criterion (n<=%d, %d pairs): violations=%d"%(N,tot,bad))

# C2: binomial form  S(n,k) == C(n - (k+2)//2, (k-1)//2) mod 2
bad=0
for n in range(1,N+1):
    for k in range(1,n+1):
        z=n-(k+2)//2; w=(k-1)//2
        c = (comb(z,w)%2) if (0<=w<=z) else 0
        if S[n][k] != c: bad+=1
print("C2 binomial form: violations=%d"%bad)

# C3: SET identity  {k in [1,d+1] : S(d+1,k) odd} == {d+1-u : u in SIGMA_d}
bad=0
for d in range(0,300):
    lhs=sorted(d+1-k for k in range(1,d+2) if S[d+1][k]==1)
    rhs=sorted(d+1-u for u in sig(d))
    if lhs!=rhs: bad+=1
print("C3 set identity as multisets (d<=299): violations=%d"%bad)

# C4: T5  #{k even: S(n,k) odd} = fusc(n-1),  #{k odd: S(n,k) odd} = fusc(n)
bad=0
for n in range(2,N+1):
    ev=sum(1 for k in range(2,n+1,2) if S[n][k]==1)
    od=sum(1 for k in range(1,n+1,2) if S[n][k]==1)
    if ev!=fusc(n-1) or od!=fusc(n): bad+=1
print("C4 T5 even/odd split (n<=%d): violations=%d"%(N,bad))

# C5: T6  S(2n,n) odd <=> n fibbinary (no two consecutive 1 bits)
def fibbin(n):
    b=bin(n)[2:]
    return '11' not in b
bad=0
for n in range(1,N//2):
    if S[2*n][n] != (1 if fibbin(n) else 0): bad+=1
print("C5 T6 centre Stirling fibbinary (n<=%d): violations=%d"%(N//2,bad))

# C6: sanity -- A(d) = #odd = fusc(d)+fusc(d+1)
bad=0
for d in range(0,300):
    cnt=sum(1 for k in range(1,d+2) if S[d+1][k]==1)
    if cnt != fusc(d)+fusc(d+1): bad+=1
print("C6 A(d) = #odd = fusc(d)+fusc(d+1) (d<=299): violations=%d"%bad)
