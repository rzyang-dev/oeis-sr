import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
good = [0, 4, 32, 36, 90, 94, 122, 126, 128, 129, 132, 133, 150, 160, 161, 164, 165, 200, 204, 218, 219, 222, 223, 232, 236, 250, 251, 254, 255]
# atomic boolean functions as rule numbers (bit index = 4l+2c+r)
def bitrule(f):
    n = 0
    for l, c, r in itertools.product([0,1], repeat=3):
        if f(l,c,r): n |= 1 << (4*l+2*c+r)
    return n
A = bitrule(lambda l,c,r: l ^ r)          # XOR of neighbors
B = bitrule(lambda l,c,r: c)              # identity
C = bitrule(lambda l,c,r: (l,c,r)==(0,1,0))  # isolated 1
D = bitrule(lambda l,c,r: (l,c,r)==(1,0,1))  # isolated 0
ONE = 255
print("A,B,C,D,1 =", A, B, C, D, ONE)
gens = [A, B, C, D, ONE]
span = set()
for mask in range(32):
    v = 0
    for i in range(5):
        if mask >> i & 1: v ^= gens[i]
    span.add(v)
print("span size:", len(span))
print("29 rules all in span?", all(g in span for g in good))
missing = [g for g in good if g not in span]
print("missing from span:", missing)
print("span elements not in the 29:", sorted(span - set(good)))
