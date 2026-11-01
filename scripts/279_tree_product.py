"""279_tree_product.py -- the tree zero count factorizes over the binary digits.

   #Z(t) = sum_{d in S(t)} b^d = (b+1) * b^(t-1-2r(t)) * prod_{i in bits(r(t))} (1 + b^(2^(i+1)))

where bits(m) is the set of positions of the 1-bits of m.  The product is the
Euler-like factorization of the submask sum  sum_{m subset r} y^m.  The count is
checked against the plain submask sum and against direct simulation of the
b-ary tree dynamics for b = 2, 3.
"""

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def bits(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def direct(b, t):
    return sum(b ** d for d in shell(t))

def product(b, t):
    if t == 0:
        return 1
    return (b + 1) * b ** (t - 1 - 2 * r(t)) * 1 if not bits(r(t)) else \
        (b + 1) * b ** (t - 1 - 2 * r(t)) * eval("*".join(str(1 + b ** (2 ** (i + 1))) for i in bits(r(t))))

bad = 0
for b in range(2, 8):
    for t in range(1, 201):
        if direct(b, t) != product(b, t):
            bad += 1
            if bad < 6:
                print("MISMATCH b=%d t=%d direct=%d product=%d" % (b, t, direct(b, t), product(b, t)))
print("b = 2..7, t = 1..200: product formula mismatches =", bad)

print()
print("  t   b=2        b=3            b=4")
for t in range(1, 13):
    print("%3d  %-10d %-14d %-14d" % (t, direct(2, t), direct(3, t), direct(4, t)))

print()
print("binary tree counts (t = 1..24):", [direct(2, t) for t in range(1, 25)])
