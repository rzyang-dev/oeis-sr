
import math
N0=1<<17
f=[0]*(N0+2); f[1]=1
for n in range(2,N0+2):
    if n%2==0: f[n]=f[n//2]
    else: f[n]=f[n//2]+f[n//2+1]
A=[f[d]+f[d+1] for d in range(N0+1)]
pref=[0]*(N0+2)
for d in range(N0+1): pref[d+1]=pref[d]+A[d]
print("sanity A(0..11) =",A[0:12])

lg=math.log(3,2)
print("(c) S(N)/N^{log2 3}, N = 2^k * (1 + j/8)")
for k in range(6,17):
    row=[]
    for j in range(9):
        N=(1<<k)+j*((1<<k)//8)
        row.append(pref[N]/(N**lg))
    print("  k=%2d "%k + " ".join("%.4f"%v for v in row))
