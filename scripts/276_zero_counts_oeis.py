"""276_zero_counts_oeis.py -- the power-of-two forms of the zero counts.

   #subm r      = 2^popcount(r)
   #shell t     = 2^wt(t)                     (two copies of the submasks of r t)
   1-D window   = 2^(1+wt(t)) - [t = 2^i-1]    = A267447(t)
   quarter Moore= 2^(1+wt(t)+floor(log2 t))    = A189007(t+1)

Also writes the first 80 terms of both sequences to sequences-276.txt so that
they can be compared with the OEIS b-lists.
"""

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def subm_count(n):
    return 1 << wt(n)

def subm_count_brute(n):
    return sum(1 for m in range(n + 1) if m & n == m)

def shell(t):
    return [d for d in range(t + 1) if ((t - d) // 2) & r(t) == (t - d) // 2]

def isM1(t):
    return t > 0 and ((t + 1) & t) == 0

Z1 = lambda t: 0 if t == 0 else (1 << (1 + wt(t))) - (1 if isM1(t) else 0)
ZM = lambda t: 0 if t == 0 else 1 << (1 + wt(t) + (t.bit_length() - 1))

bad = 0
for t in range(0, 1201):
    if subm_count_brute(r(t)) != subm_count(r(t)):
        bad += 1
        print("subm", t)
    if t >= 1:
        s = shell(t)
        if len(s) != 1 << wt(t):
            bad += 1
            print("shell", t, len(s), 1 << wt(t))
        if 2 * len(s) - (1 if 0 in s else 0) != Z1(t):
            bad += 1
            print("1D", t)
        if 4 * subm_count(r(t)) * (t - r(t)) != ZM(t):
            bad += 1
            print("Moore", t)
print("t <= 1200: #subm = 2^popcount, #shell = 2^wt, 1-D and Moore power forms:",
      "0 mismatches" if bad == 0 else "%d mismatches" % bad)

with open("sequences-276.txt", "w") as f:
    f.write("A267447-like (1-D zeros, n>=0): " + ",".join(str(Z1(t)) for t in range(0, 80)) + chr(10))
    f.write("A189007-like (Moore zeros, t>=0): " + ",".join(str(ZM(t)) for t in range(0, 80)) + chr(10))
print("wrote sequences-276.txt")

print()
print("  t  #shell   1-D zeros   Moore zeros")
for t in range(1, 17):
    print("%3d  %6d  %10d  %12d" % (t, len(shell(t)), Z1(t), ZM(t)))
