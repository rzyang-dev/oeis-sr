
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def r(t):
    return 0 if t==0 else t-(1<<(t.bit_length()-1))
def subm(rr):
    out=[]; m=rr
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&rr
    return out
def shell(t):
    out=[]
    for m in subm(r(t)):
        out.append(t-2*m); out.append(t-2*m-1)
    return set(out)
bad=0; checked=0
for k in range(1,16):
    lo,hi=1<<k,(1<<(k+1)); lim=min(lo,40)
    cnt={}
    for t in range(lo,hi):
        for dd in shell(t):
            if dd<lim: cnt[dd]=cnt.get(dd,0)+1
    for dd in range(0,lim):
        checked+=1
        if cnt.get(dd,0)!=fusc(dd)+fusc(dd+1):
            bad+=1
            if bad<5: print("  mismatch k=%d d=%d got=%d want=%d"%(k,dd,cnt.get(dd,0),fusc(dd)+fusc(dd+1)))
print("(3') per-block counts = A(d) for d < 2^k, k=1..15: %d checks, %d mismatches"%(checked,bad))
