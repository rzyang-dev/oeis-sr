
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]
N=800
S=[[0]*(N+2) for _ in range(N+2)]
S[0][0]=1
for n in range(1,N+2):
    prev=S[n-1]; cur=S[n]
    for k in range(1,n+1):
        cur[k]=(prev[k-1]+ (k%2)*prev[k])%2

# C3 corrected:  {n-k : S(n,k) odd, 1<=k<=n}  ==  SIGMA_{n-1}
bad=0
for d in range(0,400):
    n=d+1
    lhs=sorted(n-k for k in range(1,n+1) if S[n][k]==1)
    if lhs != sig(d): 
        bad+=1
        if bad<3: print("  d=%d lhs=%s sig=%s"%(d,lhs,sig(d)))
print("C3' {n-k : S(n,k) odd} == SIGMA_{n-1} (d<=399): violations=%d"%bad)

# C3'' the k-set form stated by the subagent
bad=0
for d in range(0,400):
    n=d+1
    kset=sorted(k for k in range(1,n+1) if S[n][k]==1)
    refl=sorted(n-u for u in sig(d))
    if kset!=refl: bad+=1
print("C3'' k-set == {d+1-u : u in SIGMA_d} (d<=399): violations=%d"%bad)
