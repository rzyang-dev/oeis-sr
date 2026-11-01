
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def r(t):
    return 0 if t==0 else t-(1<<(t.bit_length()-1))
def subm(r):
    out=[]; m=r
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&r
    return out
def shell(t):
    out=[]
    for m in subm(r(t)):
        out.append(t-2*m); out.append(t-2*m-1)
    return set(out)

# FINAL CONSOLIDATED CHECK (independent implementations)
# (1) dual closed form on a fresh range 2^14 <= t < 2^15, sampled densely
bad=0; n=0
for t in range(1<<14, 1<<15, 7):
    S=shell(t); s=(1<<t.bit_length())-t; u=s-1
    for d in range(0, t+1, 3):
        n+=1
        if ((u & ((u+d)//2)) == u) != (d in S): bad+=1
print("(1) dual closed form, t in [2^14,2^15) sampled: %d cases, %d mismatches"%(n,bad))

# (2) A(d) = fusc(d)+fusc(d+1) via the ORIGINAL submask condition (not the land form)
bad=0
for d in range(0,4001):
    cnt=sum(1 for u in range(d+1) if (u & ((u+d)//2)) == u)
    if cnt != fusc(d)+fusc(d+1): bad+=1
print("(2) A(d)=fusc(d)+fusc(d+1) via submask form, d<=4000: %d mismatches"%bad)

# (3) per-block dead counts really equal A(d): direct count inside block k for d small
bad=0
for k in range(2,15):
    lo,hi=1<<k,(1<<(k+1))
    cnt={}
    for t in range(lo,hi):
        for dd in shell(t):
            if dd<32: cnt[dd]=cnt.get(dd,0)+1
    for dd in range(0,31):
        if cnt.get(dd,0)!=fusc(dd)+fusc(dd+1): bad+=1
print("(3) per-block counts equal A(d) for d<31, blocks k=2..14: %d mismatches"%bad)

# (4) block-sum identity
print("(4) sum_{d<2^k} A(d) vs 3^k:", [(sum(fusc(d)+fusc(d+1) for d in range(1<<k)), 3**k) for k in range(0,9)][:9])
