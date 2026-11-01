
def bit(x,i): return (x>>i)&1
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]
def local_ok(u,d):
    L=max(u,d).bit_length()+3
    for i in range(L):
        if bit(u,i)==1:
            if bit(u,i+1) != (bit(d,i) ^ bit(d,i+1) ^ 1): return False
    return True
bad=0
for d in range(0,500):
    A=[u for u in range(0,d+1) if local_ok(u,d)]
    if A!=sig(d):
        bad+=1
        if bad<4: print("MISMATCH",d,A,sig(d))
print("LOCAL RULE  bit_i(u)=1 => bit_{i+1}(u) xor bit_{i+1}(d) xor bit_i(d) = 1 : violations =",bad)
