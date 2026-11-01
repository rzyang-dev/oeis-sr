
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]
def hyp(n): return [(u,h) for u in range(n+1) for h in range(n//2+1) if (u&h)==0 and u+2*h==n]

# (a) bijection  Phi_d : SIGMA_d -> Hyp(d) + Hyp(d-1),  u |-> (u, floor((d-u)/2), (d-u)%2)
bad=0
for d in range(0,400):
    img=set()
    for u in sig(d):
        h=(d-u)//2; par=(d-u)%2
        assert (u&h)==0
        img.add((u,h,par))
    # expected:  {(u,h,0) for (u,h) in Hyp(d)} union {(u,h,1) for (u,h) in Hyp(d-1)}
    exp=set()
    for (u,h) in hyp(d): exp.add((u,h,0))
    if d>=1:
        for (u,h) in hyp(d-1): exp.add((u,h,1))
    if img!=exp: bad+=1
print("(a) Phi_d is a bijection SIGMA_d -> Hyp(d) + Hyp(d-1)  (d<=399): violations=%d"%bad)

# (b) |Hyp(n)| = fusc(n+1)
bad=0
for n in range(0,600):
    if len(hyp(n))!=fusc(n+1): bad+=1
print("(b) |Hyp(n)| = fusc(n+1)  (n<=599): violations=%d"%bad)

# (c) run-length characterisation
def Tset(d): return set(i for i in range(d.bit_length()+1) if ((d>>i)&1)!=((d>>(i+1))&1))
def runs(u):
    out=[]; i=0; b=u.bit_length()
    while i<b:
        if (u>>i)&1:
            a=i
            while i<b and (u>>i)&1: i+=1
            out.append((a,i-1))
        else: i+=1
    return out
def const_on(d,a,b):
    return len(set((d>>i)&1 for i in range(a,b+1)))==1
bad=0
for d in range(0,600):
    T=Tset(d)
    for u in range(0,d+1):
        cond=all((b in T) and const_on(d,a,b) for (a,b) in runs(u))
        if cond != ((u & ((u+d)//2))==u): bad+=1
print("(c) run-length characterisation  (d<=599, all u): violations=%d"%bad)

# (d) A(2e)+A(2e+1) = 3 A(e)
bad=0
for e in range(0,300):
    if len(sig(2*e))+len(sig(2*e+1)) != 3*len(sig(e)): bad+=1
print("(d) A(2e)+A(2e+1) = 3 A(e)  (e<=299): violations=%d"%bad)

# (e) no two-copy decomposition:  |SIGMA_{2e}| - |SIGMA_e| = fusc(e)  (not |SIGMA_e|)
bad=0
for e in range(0,300):
    if len(sig(2*e))-len(sig(e)) != fusc(e): bad+=1
print("(e) |SIGMA_{2e}| - |SIGMA_e| = fusc(e)  (e<=299): violations=%d"%bad)
