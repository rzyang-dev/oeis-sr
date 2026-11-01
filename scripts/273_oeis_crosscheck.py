"""273_oeis_crosscheck.py -- check the shell/scaling law against OEIS data.

Published terms (from the OEIS JSON records):

  A169699 (offset 0): total number of ON cells at stage n of the 2-D
      5-neighbour outer totalistic rule 510.  52 terms.
  A071051 (offset 0): number of ON cells at generation n of 1-D rule 126
      (= number of 1's in the n-th row of A071035).  First 20 terms.

Our theorem says (N = 2^wt(r), r = n - 2^k for 2^k <= n < 2^(k+1)):

  zero shells:   S(n) = {n - 2m, n - 2m - 1 : m submask of r}
  count vN:      a_vN(n) = 4*sigma(n) + eps(n),  sigma = sum_{d in S, d>=1} d
  count 1-D:     a_1D(n) = 2*#S(n) - eps(n)

with sigma(n) = N*(2n-1-2r) and eps(n) = [n = 2^i - 1].  Hence

  a_vN(n) = (2^(k+1)-1) * 2^(1+wt(n)) + [n = 2^i - 1]
  a_1D(n) = 2^(1+wt(n))              - [n = 2^i - 1]

The formula currently printed in A169699 has "+1 if n is a power of 2"
instead of "+1 if n = 2^i - 1"; the script exhibits the discrepancy.
"""
A169699 = [int(x) for x in "1,5,12,25,28,56,56,113,60,120,120,240,120,240,240,481,124,248,248,496,248,496,496,992,248,496,496,992,496,992,992,1985,252,504,504,1008,504,1008,1008,2016,504,1008,1008,2016,1008,2016,2016,4032,504,1008,1008,2016".split(",")]
A071051 = [int(x) for x in "1,3,4,7,4,8,8,15,4,8,8,16,8,16,16,31,4,8,8,16".split(",")]

def wt(n):
    return bin(n).count("1")

def k_of(n):
    return n.bit_length() - 1

def r_of(n):
    return 0 if n == 0 else n - (1 << k_of(n))

def is_mersenne(n):
    return n >= 1 and (n & (n + 1)) == 0

def is_pow2(n):
    return n >= 1 and (n & (n - 1)) == 0

def shells(n):
    r = r_of(n)
    out = set()
    m = r
    while True:
        out.add(n - 2 * m)
        out.add(n - 2 * m - 1)
        if m == 0:
            break
        m = (m - 1) & r
    return sorted(d for d in out if 0 <= d <= n)

def our_vN(n):
    if n == 0:
        return 1
    return 4 * sum(d for d in shells(n) if d >= 1) + (1 if 0 in shells(n) else 0)

def our_1D(n):
    if n == 0:
        return 1
    s = shells(n)
    return 2 * len(s) - (1 if 0 in s else 0)

def stated_A169699(n):
    """The formula printed in the OEIS entry."""
    if n == 0:
        return 1
    v = ((1 << (k_of(n) + 1)) - 1) * (1 << (1 + wt(n)))
    return v + (1 if is_pow2(n) else 0)

def wt_form_vN(n):
    """our formula rewritten with wt(n)."""
    if n == 0:
        return 1
    v = ((1 << (k_of(n) + 1)) - 1) * (1 << (1 + wt(n)))
    return v + (1 if is_mersenne(n) else 0)

print("A169699: %d published terms" % len(A169699))
bad_ours = [(n, A169699[n], our_vN(n)) for n in range(len(A169699)) if A169699[n] != our_vN(n)]
bad_wt = [(n, A169699[n], wt_form_vN(n)) for n in range(len(A169699)) if A169699[n] != wt_form_vN(n)]
bad_stated = [(n, A169699[n], stated_A169699(n)) for n in range(len(A169699)) if A169699[n] != stated_A169699(n)]
print("  our shell formula  : %d mismatches" % len(bad_ours))
print("  our wt form        : %d mismatches" % len(bad_wt))
print("  OEIS stated formula: %d mismatches" % len(bad_stated))
print("  mismatching n (stated): %s" % [x[0] for x in bad_stated])
print("  e.g. n=2: published %d, stated formula %d" % (A169699[2], stated_A169699(2)))

print()
print("A071051: %d published terms" % len(A071051))
bad1 = [(n, A071051[n], our_1D(n)) for n in range(len(A071051)) if A071051[n] != our_1D(n)]
print("  our 1-D formula    : %d mismatches" % len(bad1))

print()
print("n   shells                     #S  sigma  1-D  vN   A169699")
for n in range(1, 17):
    s = shells(n)
    print("%-3d %-26s %-3d %-5d %-4d %-4d %d" % (n, str(s), len(s),
          sum(d for d in s if d >= 1), our_1D(n), our_vN(n), A169699[n]))
