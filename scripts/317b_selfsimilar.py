
import math
N0=1<<16
f=[0]*(N0+2); f[1]=1
for n in range(2,N0+2):
    if n%2==0: f[n]=f[n//2]
    else: f[n]=f[n//2]+f[n//2+1]
A=[f[d]+f[d+1] for d in range(N0+1)]
pref=[0]*(N0+2)
for d in range(N0+1): pref[d+1]=pref[d]+A[d]
# is S(2N) = 3 S(N) exactly?
bad=[N for N in range(1,N0//2) if pref[2*N]!=3*pref[N]]
print("S(2N) == 3 S(N) for all N <%d : %s"%(N0//2, len(bad)==0), bad[:5])
lg=math.log(3,2)
N=1234
print("S(N)/N^{log2 3} for N=1234, 2468, 4936 :", ["%.6f"%(pref[n]/n**lg) for n in (1234,2468,4936,9872)])
print("=> S(N) = N^{log2 3} * F(log2 N) with F exactly 1-periodic.")
# values of F on [0,1)
print("F(x) = S(2^x)/2^{x log2 3} for x = 0, .1, ..., .9:")
print("  ", ["%.4f"%(pref[round(2**(10+x*10))-1]/((2**(10+x*10))**lg)) for x in [i/10 for i in range(10)]])
