
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def sig(d):
    return [u for u in range(d+1) if (u & ((u+d)//2)) == u]

# --- candidate predicates that might split Sigma_d into f(d) and f(d+1)
preds = {
 "u even": lambda u,d: u%2==0,
 "u odd": lambda u,d: u%2==1,
 "u<d/2": lambda u,d: 2*u<d,
 "u>=d/2": lambda u,d: 2*u>=d,
 "u<=d/2": lambda u,d: 2*u<=d,
 "popcount even": lambda u,d: bin(u).count('1')%2==0,
 "u submask d": lambda u,d: (u & d)==u,
 "u submask floor(d/2)": lambda u,d: (u & (d//2))==u,
 "2u submask d+u": lambda u,d: (2*u & (d+u))==2*u,
 "d-u even": lambda u,d: (d-u)%2==0,
 "top bit of u <= top bit d/2": lambda u,d: u.bit_length()<=max(d//2,0).bit_length(),
}
print("checking whether #{u in Sigma_d : pred} equals fusc(d) or fusc(d+1), for d<=200")
for name,p in preds.items():
    ok0=all(sum(1 for u in sig(d) if p(u,d))==fusc(d)   for d in range(0,201))
    ok1=all(sum(1 for u in sig(d) if p(u,d))==fusc(d+1) for d in range(0,201))
    print(f"  {name:35s} == f(d): {ok0}   == f(d+1): {ok1}")

# --- does Sigma_{2e} contain the binary lifts of Sigma_e ?
print()
for e in range(0,12):
    S2=set(sig(2*e)); Se=sig(e)
    lift_even=set(2*u for u in Se); lift_odd=set(2*u+1 for u in Se)
    print(f"e={e:3d}  |Sigma_e|={len(Se):2d} |Sigma_2e|={len(S2):2d}  2Se subset: {lift_even<=S2}  (2Se+1) subset: {lift_odd<=S2}  #(2Se in S2)={len(lift_even&S2)}  #(2Se+1 in S2)={len(lift_odd&S2)}")
