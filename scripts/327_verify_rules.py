
def r(t): return 0 if t==0 else t-(1<<(t.bit_length()-1))
def shell(t):
    rt=r(t); out=set()
    m=rt
    while True:
        out.add(t-2*m); out.add(t-2*m-1)
        if m==0: break
        m=(m-1)&rt
    return out
def rule_f(n):
    return lambda a,b,c: (n>>((a<<2)|(b<<1)|c))&1
def evolve(n, T=20):
    f=rule_f(n)
    row=[1]                      # t=0: only centre alive
    rows=[row]
    for t in range(T):
        L=len(row)
        new=[0]*(L+1)
        for d in range(L+1):
            a = row[d-1] if d>=1 else row[0]        # dup boundary
            b = row[d] if d<L else 0
            c = row[d+1] if d+1<L else 0
            new[d]=f(a,b,c)
        row=new; rows.append(row)
    return rows

T=18
print("check 1: 129 closed form  x_t(d) = 1 - [d in shell(t)]")
rows=evolve(129,T); bad=0
for t in range(1,T+1):
    S=shell(t)
    for d in range(len(rows[t])):
        want = 0 if d in S else 1
        if rows[t][d]!=want: bad+=1
print("   violations:",bad)

print("check 2: 90 closed form  x_t(d) = [d in shell(t)]   (i.e. 90 = 1-129)")
rows90=evolve(90,T); bad=0
for t in range(1,T+1):
    S=shell(t)
    for d in range(len(rows90[t])):
        want = 1 if d in S else 0
        if rows90[t][d]!=want: bad+=1
print("   violations:",bad)

print("check 3: 90 == 1-129 pointwise (t>=1)")
bad=sum(1 for t in range(1,T+1) for d in range(len(rows[t])) if rows90[t][d] != 1-rows[t][d])
print("   violations:",bad)

print("check 4: the claimed 129-orbit {129,133,161,165} identical, and {90,94,122,126} identical")
orbA=[129,133,161,165]; orbB=[90,94,122,126]
rA={n:evolve(n,T) for n in orbA}; rB={n:evolve(n,T) for n in orbB}
print("   orbit A identical:", all(rA[n]==rA[129] for n in orbA))
print("   orbit B identical:", all(rB[n]==rB[90] for n in orbB))

print("check 5: which of the 256 rules equal 129 or 1-129 for all t<=T ?")
same=[]; comp=[]
base=evolve(129,T)
for n in range(256):
    rn=evolve(n,T)
    if rn==base: same.append(n)
    elif all(rn[t][d]==1-base[t][d] for t in range(1,T+1) for d in range(len(base[t]))) and \
         all(rn[t][d]== (1-base[t][d]) for t in [0] for d in range(len(base[0]))): comp.append(n)
print("   identical to 129:",same)
print("   complement of 129:",comp)
