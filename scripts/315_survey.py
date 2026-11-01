
from fractions import Fraction
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]
def A(d): return len(sig(d))

# ---- (a) Stirling numbers of the second kind mod 2
S=[[0]*60 for _ in range(60)]
S[0][0]=1
for n in range(1,60):
    for k in range(1,n+1):
        S[n][k]=S[n-1][k-1]+k*S[n-1][k]
odd=[sum(1 for k in range(n+1) if S[n][k]%2==1) for n in range(60)]
print("(a) #{k : S2(n,k) odd} for n=2..14 :", odd[2:15])
print("    A(d) for d=0..12            :", [A(d) for d in range(13)])
print("    match A(d) == #{k : S2(d+2,k) odd} for d<=56 :", all(A(d)==odd[d+2] for d in range(57)))

# ---- (b) hyperbinary representations
def HB(n):
    # representations n = sum e_i 2^i with e_i in {0,1,2}
    reps=[[]]
    for i in range(n.bit_length()+2):
        new=[]
        for r in reps:
            for e in (0,1,2):
                new.append(r+[e])
        reps=new
    return sum(1 for r in reps if sum(e*(1<<i) for i,e in enumerate(r))==n)
bad=[(n,HB(n),fusc(n+1)) for n in range(0,14) if HB(n)!=fusc(n+1)]
print("(b) hyperbinary HB(n) vs fusc(n+1), n<14, mismatches:", bad)

# ---- (c) A(d) mod 2
m2=[A(d)%2 for d in range(24)]
print("(c) A(d) mod 2, d=0..23:", m2)
print("    period 3 from d=0 ?", all(m2[i]==m2[i+3] for i in range(21)))
print("    A(d) mod 2 == 1 iff d mod 3 == ?:", sorted(set(d%3 for d in range(24) if A(d)%2==1)))

# ---- (d) block mass and dimension
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def subm(rr):
    out=[]; m=rr
    while True:
        out.append(m)
        if m==0: break
        m=(m-1)&rr
    return out
def shell(t):
    out=set()
    for m in subm(r(t)):
        out.add(t-2*m); out.add(t-2*m-1)
    return out
print("(d) dead cells per block sum_t |S(t)| vs 2*3^k:")
for k in range(0,13):
    tot=sum(len(shell(t)) for t in range(1<<k,1<<(k+1)))
    print("    k=%2d  got %8d   2*3^k = %8d   %s"%(k,tot,2*3**k,tot==2*3**k))
print("    sum_{n<2^k} fusc(n) = (3^k-1)/2 ?", all(sum(fusc(n) for n in range(1<<k))==(3**k-1)//2 for k in range(0,13)))

# ---- (e) continued fraction of the Calkin-Wilf rational from the bit run lengths
def runlengths(n):
    return [len(x) for x in bin(n)[2:].split('0')]  # crude, for illustration
def cf(p,q):
    out=[]
    while q:
        out.append(p//q); p,q=q,p%q
    return out
print("(e) n, fusc(n)/fusc(n+1), its continued fraction:")
for n in range(1,12):
    p,q=fusc(n),fusc(n+1)
    print("    n=%2d  %d/%d  CF=%s   bits=%s"%(n,p,q,cf(p,q),bin(n)[2:]))
