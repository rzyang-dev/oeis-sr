"""268_sigma_formula.py -- closed form for the universal shell sum.

Claim:
  S(t)   = { t - 2m : m submask of r } union { t - 2m - 1 : m submask of r }
  sigma(t) = sum_{d in S(t), d>=1} d = 2^popcount(r) * (2t - 1 - 2r),
  eps(t)   = [0 in S(t)] = [t = 2^k - 1],
with r = r(t) = t - 2^floor(log2 t).
"""
def rmask(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def S_brute(t):
    return [d for d in range(t + 1) if (((t - d) // 2) & rmask(t)) == ((t - d) // 2)]

def S_formula(t):
    r = rmask(t)
    r = rmask(t)
    out = set()
    m = r
    while True:
        out.add(t - 2 * m)
        out.add(t - 2 * m - 1)
        if m == 0:
            break
        m = (m - 1) & r
    return sorted(d for d in out if 0 <= d <= t)

def sigma_brute(t):
    return sum(d for d in S_brute(t) if d >= 1)

def sigma_formula(t):
    r = rmask(t)
    return (1 << bin(r).count("1")) * (2 * t - 1 - 2 * r)

bad_S = bad_sig = bad_eps = 0
for t in range(1, 2001):
    if S_brute(t) != S_formula(t):
        bad_S += 1
        if bad_S <= 3:
            print("S mismatch t=%d" % t)
    if sigma_brute(t) != sigma_formula(t):
        bad_sig += 1
        if bad_sig <= 3:
            print("sigma mismatch t=%d brute=%d formula=%d" % (t, sigma_brute(t), sigma_formula(t)))
    e = 1 if 0 in S_brute(t) else 0
    pred = 1 if (t & (t + 1)) == 0 else 0
    if e != pred:
        bad_eps += 1
print("t<=2000: S set mismatches=%d, sigma mismatches=%d, eps mismatches=%d" % (bad_S, bad_sig, bad_eps))
print()
print("t  r  popcount  sigma")
for t in range(1, 21):
    r = rmask(t)
    print("%-3d %-3d %-8d %d" % (t, r, bin(r).count("1"), sigma_formula(t)))
