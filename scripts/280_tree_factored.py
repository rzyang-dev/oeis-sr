"""280_tree_factored.py -- check the exact Lean statement

   sum_{d in S(t)} b^d = (b+1) * b^(t-1-2r(t)) * prod_{i in bits(r(t))} (1 + b^(2^(i+1)))

with bits(r) = {i < r : the i-th bit of r is set} (the Lean definition uses
Finset.range r, not the bit length, so the two agree for every r).
"""

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def bits(m):
    return [i for i in range(m) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def direct(b, t):
    return sum(b ** d for d in shell(t))

def factored(b, t):
    if t == 0:
        return 1
    p = 1
    for i in bits(r(t)):
        p *= 1 + b ** (2 ** (i + 1))
    return (b + 1) * b ** (t - 1 - 2 * r(t)) * p

bad = 0
for b in range(2, 9):
    for t in range(1, 301):
        if direct(b, t) != factored(b, t):
            bad += 1
            if bad < 6:
                print("MISMATCH b=%d t=%d %d %d" % (b, t, direct(b, t), factored(b, t)))
print("b = 2..8, t = 1..300: factored form mismatches =", bad)

print()
print("  t   bits(r(t))      b=2 count   factors")
for t in range(1, 13):
    bs = bits(r(t))
    print("%3d   %-14s   %-10d   %s" % (t, str(bs), direct(2, t),
          " * ".join(["(1+2^%d)" % (2 ** (i + 1)) for i in bs]) or "1"))
