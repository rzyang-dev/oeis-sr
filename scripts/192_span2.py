import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
good = [0, 4, 32, 36, 90, 94, 122, 126, 128, 129, 132, 133, 150, 160, 161, 164, 165, 200, 204, 218, 219, 222, 223, 232, 236, 250, 251, 254, 255]
def bitrule(f):
    n = 0
    for l, c, r in itertools.product([0,1], repeat=3):
        if f(l,c,r): n |= 1 << (4*l+2*c+r)
    return n
A = bitrule(lambda l,c,r: l ^ r)
B = bitrule(lambda l,c,r: c)
C = bitrule(lambda l,c,r: (l,c,r)==(0,1,0))
D = bitrule(lambda l,c,r: (l,c,r)==(1,0,1))
E = bitrule(lambda l,c,r: (l,c,r)==(0,0,0))
F = bitrule(lambda l,c,r: (l,c,r)==(1,1,1))
ONE = 255
gens = [A,B,C,D,E,F,ONE]
print("gens:", gens)
span = set()
for mask in range(128):
    v = 0
    for i in range(7):
        if mask >> i & 1: v ^= gens[i]
    span.add(v)
print("span size:", len(span))
print("29 all in span?", all(g in span for g in good))
print("missing:", [g for g in good if g not in span])
print("extra:", sorted(span - set(good))[:40])
