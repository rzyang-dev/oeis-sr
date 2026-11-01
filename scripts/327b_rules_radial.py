
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def shell(t):
    rt=r(t); out=set(); m=rt
    while True:
        out.add(t-2*m); out.add(t-2*m-1)
        if m==0: break
        m=(m-1)&rt
    return out
def rule_f(n): return lambda a,b,c: (n>>((a<<2)|(b<<1)|c))&1

def evolve_radial(n, T=20, dup=True):
    """radial state on the ray; track d=0..t and a constant exterior E for d>t"""
    f=rule_f(n)
    row=[1]; E=0; rows=[row]; Es=[E]
    for t in range(T):
        L=len(row)              # L = t+1
        new=[]
        for d in range(L+1):
            a = row[d-1] if d>=1 else (row[0] if dup else 0)
            b = row[d] if d<L else E
            c = row[d+1] if d+1<L else E
            new.append(f(a,b,c))
        E2 = f(E,E,E)
        row=new; E=E2; rows.append(row); Es.append(E)
    return rows, Es

T=18
for name,n in (("129",129),("90",90)):
    rows,Es=evolve_radial(n,T)
    bad=0
    for t in range(1,T+1):
        S=shell(t)
        for d in range(t+1):            # formula only claimed for d <= t
            want = 0 if d in S else 1
            if name=="90": want = 1-want
            if rows[t][d]!=want: bad+=1
    print("rule %s: closed form for d<=t, t<=%d : violations=%d   (exterior E_t: %s)"%(name,T,bad,Es[:6]))

rows129,_=evolve_radial(129,T); rows90,_=evolve_radial(90,T)
bad=sum(1 for t in range(1,T+1) for d in range(t+1) if rows90[t][d] != 1-rows129[t][d])
print("90 == 1-129 on the cone (d<=t): violations=%d"%bad)
orbA=[129,133,161,165]; orbB=[90,94,122,126]
bA=sum(1 for n in orbA for t in range(T+1) for d in range(t+1) if evolve_radial(n,T)[0][t][d]!=rows129[t][d])
bB=sum(1 for n in orbB for t in range(T+1) for d in range(t+1) if evolve_radial(n,T)[0][t][d]!=rows90[t][d])
print("orbits identical on the cone: A viol=%d, B viol=%d"%(bA,bB))
