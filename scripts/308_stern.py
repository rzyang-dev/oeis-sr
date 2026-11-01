
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a

def sigma_set(d):
    return [u for u in range(d+1) if (u & ((u+d)//2)) == u]

print("fusc(0..15) =", [fusc(i) for i in range(16)])
bad=0
for d in range(0,4001):
    A=len(sigma_set(d)); pred=fusc(2*d+1)
    if A!=pred:
        bad+=1
        if bad<10: print("MISMATCH d=%d A=%d fusc(2d+1)=%d"%(d,A,pred))
print("A(d) == fusc(2d+1) for d<=4000: mismatches =",bad)

bad=0
for d in range(0,4001):
    if fusc(2*d+1)!=fusc(d)+fusc(d+1): bad+=1
print("identity fusc(2d+1)==fusc(d)+fusc(d+1) mismatches:",bad)

# split of Sigma_d: even vs odd u  -> candidate for fusc(d), fusc(d+1)
print()
print("d | A(d) | #{u even} | #{u odd} | fusc(d) | fusc(d+1)")
for d in range(0,16):
    S=sigma_set(d); e=sum(1 for u in S if u%2==0); o=len(S)-e
    print(f"{d} | {len(S)} | {e} | {o} | {fusc(d)} | {fusc(d+1)}")
