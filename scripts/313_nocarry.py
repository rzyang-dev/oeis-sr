
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a

# (1)  u subset u+h  <=>  u & h == 0
bad=0
for u in range(0,300):
    for h in range(0,300):
        if ((u & (u+h)) == u) != ((u & h)==0): bad+=1
print("LEMMA  u subset u+h  <=>  u & h = 0 :  violations =",bad)

# (2)  Sigma_d = {u : u & floor((d-u)/2) == 0}
def sig(d): return [u for u in range(d+1) if (u & ((u+d)//2)) == u]
bad=0
for d in range(0,600):
    if sig(d)!=[u for u in range(d+1) if (u & ((d-u)//2))==0]: bad+=1
print("Sigma_d = {u : u & floor((d-u)/2) = 0} :  violations =",bad)

# (3)  c(n) = #{(u,h) : u & h == 0, u+2h = n}  ==  fusc(n+1) ?
def c(n): return sum(1 for h in range(n//2+1) if ((n-2*h) & h)==0)
bad=0
for n in range(0,800):
    if c(n)!=fusc(n+1):
        bad+=1
        if bad<6: print("  c mismatch n=%d c=%d fusc(n+1)=%d"%(n,c(n),fusc(n+1)))
print("c(n) = fusc(n+1) :  violations =",bad)
print("c(0..15) =",[c(n) for n in range(16)])
print("fusc(1..16) =",[fusc(n) for n in range(1,17)])

# (4)  A(d) = c(d) + c(d-1)
bad=0
for d in range(0,400):
    if len(sig(d)) != c(d) + (c(d-1) if d>0 else 0): bad+=1
print("A(d) = c(d)+c(d-1) : violations =",bad)
