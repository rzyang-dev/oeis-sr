"""270_a169699.py -- check the closed form against A169699 (52 terms).

A169699 = total number of ON cells at stage n of the 2-D 5-neighbour
outer totalistic rule 510 (Wolfram, NKS p. 170).

Claim: the ON set of rule 510 is exactly the zero set of the 5-cell
"all neighbours equal" rule, and the zero set is a union of complete
L1 shells with shell set
    S(t) = { t - 2m, t - 2m - 1 : m submask of r(t) },
so   a(t) = 1 (t=0),   a(t) = 4*sigma(t) + eps(t)   for t >= 1,
sigma(t) = 2^wt(r) * (2t - 1 - 2r),  eps(t) = [t = 2^k - 1].
"""
DATA = "1,5,12,25,28,56,56,113,60,120,120,240,120,240,240,481,124,248,248,496,248,496,496,992,248,496,496,992,496,992,992,1985,252,504,504,1008,504,1008,1008,2016,504,1008,1008,2016,1008,2016,2016,4032,504,1008,1008,2016".split(",")
DATA = [int(x) for x in DATA]

def rmask(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def sigma(t):
    r = rmask(t)
    return (1 << bin(r).count("1")) * (2 * t - 1 - 2 * r)

def eps(t):
    return 1 if (t & (t + 1)) == 0 else 0

def formula(t):
    return 1 if t == 0 else 4 * sigma(t) + eps(t)

bad = [(t, DATA[t], formula(t)) for t in range(len(DATA)) if DATA[t] != formula(t)]
print("A169699: %d terms checked, %d mismatches" % (len(DATA), len(bad)))
for x in bad[:5]:
    print("  n=%d oeis=%d formula=%d" % x)

# also the OEIS-stated remark: (2^(k+1)-1)*2^(1+wt(n)) + [n power of 2]
def remark(t):
    if t == 0:
        return 1
    k = t.bit_length() - 1
    v = ((1 << (k + 1)) - 1) * (1 << (1 + bin(t).count("1")))
    return v + (1 if (t & (t - 1)) == 0 else 0)

bad2 = [(t, DATA[t], remark(t)) for t in range(len(DATA)) if DATA[t] != remark(t)]
print("OEIS remark formula: %d mismatches" % len(bad2))
print("our formula == OEIS remark for n=1..2000:",
      all(formula(t) == remark(t) for t in range(1, 2001)))
