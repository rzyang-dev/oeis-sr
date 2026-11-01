
def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))
def subm(r):
    out=[]; m=r
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&r
    return out
def shell(t):
    rt=r(t); out=[]
    for m in subm(rt):
        out.append(t-2*m); out.append(t-2*m-1)
    return sorted(out)

# CHECK 1: dual closed form.  s = 2^bitlen(t) - t,  u = s-1.
# claim: d in shell(t)  <=>  u & floor((u+d)/2) == u
bad=0; checked=0
for t in range(1, 1<<14):
    S=set(shell(t)); s=(1<<t.bit_length())-t; u=s-1
    for d in range(0, t+1):
        claim = (u & ((u+d)//2)) == u
        checked+=1
        if claim != (d in S):
            bad+=1
            if bad<6: print("MISMATCH t=%d d=%d s=%d u=%d claim=%s actual=%s"%(t,d,s,u,claim,d in S))
print("CHECK1 checked=%d mismatches=%d"%(checked,bad))

# CHECK 2: dual sum form  Z = sum over B superset of u
import random
random.seed(7)
for trial in range(200):
    c=[random.randint(-5,5) for _ in range(4000)]
    for t in [random.randint(1,3000) for _ in range(6)]:
        z1=sum(c[d] for d in shell(t))
        s=(1<<t.bit_length())-t; u=s-1
        z2=0
        # B superset of u  <=>  B = u | extra bits
        limit=t
        # enumerate supersets of u up to (limit+u)/2
        top=(limit+u)//2
        B=u
        # enumerate all supersets of u below 2^bitlen(top) : brute force small
        for BB in range(u, top+1):
            if BB & u == u:
                z2+=c[2*BB-u]+c[2*BB-u+1] if 2*BB-u+1<=limit else c[2*BB-u]
        if z1!=z2:
            print("DUALSUM MISMATCH t=%d z1=%d z2=%d"%(t,z1,z2)); break
print("CHECK2 done")

# A(d): number of s in [1,d+1] with (s-1) submask floor((s-1+d)/2)
def A(d):
    return sum(1 for s in range(1,d+2) if ((s-1) & ((s-1+d)//2)) == (s-1))
seq=[A(d) for d in range(0,80)]
print("A(0..79) =", seq)
