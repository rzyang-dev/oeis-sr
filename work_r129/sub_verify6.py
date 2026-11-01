import sys, time, random
sys.stdout.reconfigure(encoding="utf-8")

def r_of(t): return t - (1 << (t.bit_length()-1))
def formula_zero(t, j):
    if t == 0: return j == 0
    if abs(j) > t: return False
    s = (t - abs(j)) >> 1
    return (s & r_of(t)) == s

# ---- large-t spot check: W=40001, T=20000 ----
W, T = 40001, 20000
random.seed(12345)
ts = random.sample(range(1, T+1), 250)
checks = []
for t in ts:
    for _ in range(120):
        checks.append((t, random.randrange(0, t+1)))
checks.sort()
mask = (1 << (2*W+1)) - 1
a = 1 << W
idx = 0; bad = 0; done = 0; cone_bad = 0
t0 = time.time()
for t in range(1, T+1):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    z = (~a) & mask
    allowed = ((1 << (2*t+1)) - 1) << (W - t)
    tr = W - t - 2
    trusted = ((1 << (2*tr+1)) - 1) << (W - tr)
    if (z & ~allowed) & trusted:
        cone_bad += 1
        if cone_bad <= 3: print("   cone violation t=", t)
    while idx < len(checks) and checks[idx][0] == t:
        _, j = checks[idx]; idx += 1; done += 1
        act = (a >> (j+W)) & 1
        pred = 0 if formula_zero(t, j) else 1
        if act != pred:
            bad += 1
            if bad <= 5: print("   large-t mismatch", t, j)
print("Y1) large-t: %d cells checked (t<=%d random), mismatches %d, cone violations %d, %.1fs"
      % (done, T, bad, cone_bad, time.time()-t0))

# ---- exhaustive light cone over full range from stored rows ----
W2, T2 = 4200, 2000
mask2 = (1 << (2*W2+1)) - 1
a = 1 << W2
st = [a]
for _ in range(T2):
    L = (a << 1) & mask2; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask2)) & mask2
    st.append(a)
bad = []
for t in range(1, T2+1):
    z = (~st[t]) & mask2
    allowed = ((1 << (2*t+1)) - 1) << (W2 - t)
    tr = W2 - t - 2
    trusted = ((1 << (2*tr+1)) - 1) << (W2 - tr)
    if (z & ~allowed) & trusted: bad.append(t)
print("Y6) light cone: no zeros with t<|j|<=W-t-2, violations t<=%d: %d" % (T2, len(bad)), bad[:5])

# ---- zero set closed form incl. t=0 (parenthesised) ----
bad = 0
for t in range(0, 1001):
    lim = min(t, W2 - t - 3)
    for j in range(-lim, lim+1):
        act_zero = (((st[t] >> (j+W2)) & 1) == 0)
        if act_zero != formula_zero(t, j): bad += 1
print("Y5) zero-set closed form incl. t=0, t<=1000: mismatches", bad)

# ---- |E_t| = 2^popcount(t+1) already checked; give counts table ----
