
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def sig(d):
    return [u for u in range(d+1) if (u & ((u+d)//2)) == u]

print("d | Sigma_d | even | odd | f(d) | f(d+1)")
for d in range(0,13):
    S=sig(d); e=[u for u in S if u%2==0]; o=[u for u in S if u%2==1]
    print(f"{d:2d} | {S} | {len(e)} | {len(o)} | {fusc(d)} | {fusc(d+1)}")
print()
print("check rule: #{u in S_d : u = d mod 2} == f(d+1);  #{u : u != d mod 2} == f(d)")
bad=0
for d in range(0,600):
    S=sig(d)
    same=[u for u in S if (u-d)%2==0]; diff=[u for u in S if (u-d)%2!=0]
    if len(same)!=fusc(d+1) or len(diff)!=fusc(d): bad+=1
print("  violations:",bad)
print()
print("lifting: u in Sigma_e -> 2u in Sigma_2e ?")
for e in range(0,20):
    S2=set(sig(2*e)); Se=sig(e)
    ok=all(2*u in S2 for u in Se)
    even2=[u for u in S2 if u%2==0]
    print(f"  e={e:2d}  |Sigma_e|={len(Se)}  all doubled in Sigma_2e: {ok}   even part of Sigma_2e = doubles: {sorted(even2)==sorted(2*u for u in Se)}")
print()
print("odd part of Sigma_2e:")
for e in range(0,20):
    S2=sig(2*e); odd=[u for u in S2 if u%2==1]
    mapped=sorted((u-1)//2 for u in odd)
    print(f"  e={e:2d}  odd part = {odd}  -> half = {mapped}   Sigma_e={sig(e)}")
