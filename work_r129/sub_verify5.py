import sys, time, random
sys.stdout.reconfigure(encoding="utf-8")

def r_of(t): return t - (1 << (t.bit_length()-1))

def simulate(W, T, keep=False):
    mask = (1 << (2*W+1)) - 1
    a = 1 << W
    out = [a] if keep else None
    for _ in range(T):
        L = (a << 1) & mask
        R = a >> 1
        a = ((L & a & R) | (~(L | a | R) & mask)) & mask
        if keep: out.append(a)
    return out

# ---- 1) spot-check closed form at large t (W=40001, T=20000) ----
W, T = 40001, 20000
random.seed(12345)
checks = [(t, random.randrange(0, t+1)) for t in random.sample(range(1, T+1), 250) for _ in range(120)]
checks.sort()
mask = (1 << (2*W+1)) - 1
a = 1 << W
idx = 0; bad = 0; done = 0
t0 = time.time()
for t in range(1, T+1):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    if t >= 1:
        z = (~a) & mask
        # no zeros outside [-t,t]
        win = ((1 << (2*t+1)) - 1) << (W - t)
        if z & ~win:
            print("   light-cone violation at t=", t); break
    while idx < len(checks) and checks[idx][0] == t:
        _, j = checks[idx]; idx += 1; done += 1
        act = (a >> (j+W)) & 1
        s = (t - j) >> 1; r = r_of(t)
        pred = 0 if ((s & r) == s) else 1
        if act != pred:
            bad += 1
            if bad <= 5: print("   large-t mismatch", t, j)
print("Y1) large-t spot check (250 random t<=%d, 120 random j each): %d checks, %d mismatches, %.1fs"
      % (T, done, bad, time.time()-t0))

# ---- 2) edge-count law from stored rows ----
W2, T2 = 4200, 2000
st = simulate(W2, T2, keep=True)
NB = (2*W2+1+7)//8
def ebit(t, j):
    # edge between j and j+1, from row bytes
    return ((st[t] >> (j+W2)) & 1) != ((st[t] >> (j+1+W2)) & 1)
bad = []
for t in range(0, T2+1):
    cnt = sum(1 for j in range(-t-1, t+1) if ebit(t, j))
    if cnt != (1 << bin(t+1).count('1')): bad.append((t, cnt, 1 << bin(t+1).count('1')))
print("Y2) |E_t| = 2^popcount(t+1) violations t<=%d: %d" % (T2, len(bad)), bad[:5])

# ---- 3) parent's claim |E_{2^k+m}| = 2|E_m| ----
def Ecount(t):
    return sum(1 for j in range(-t-1, t+1) if ebit(t, j))
res = {}
for k in range(1, 8):
    for m in range(0, 64):
        t = (1<<k)+m
        if t > 900: continue
        res[(k,m)] = (Ecount(t) == 2*Ecount(m))
bad = [km for km, ok in res.items() if not ok]
bad_nocarry = [km for km in bad if km[1] < (1<<km[0])-1]
print("Y3) claim |E_{2^k+m}|=2|E_m|: tested %d, fails %d;" % (len(res), len(bad)))
print("    all failures have m >= 2^k - 1 ?", all(km[1] >= (1<<km[0])-1 for km in bad), " first:", bad[:6])
print("    |E_t| at t=2^k-1 (should be 2):", [(k, Ecount((1<<k)-1)) for k in range(1,8)])

# ---- 4) closed-form edge formula, extended ----
bad = 0
for t in range(1, 1001):
    r = r_of(t)
    for j in range(0, t+1):
        d = t - j
        if d & 1: pred = 0
        else:
            s = d >> 1
            A = ((s & r) == s); B = s > 0 and (((s-1) & r) == (s-1))
            pred = 1 if A != B else 0
        if pred != (1 if ebit(t,j) else 0):
            bad += 1
print("Y4) closed-form edge formula e_t(j)=[t-j even]*([s subset r] xor [s-1 subset r]), t<=1000: mismatches", bad)

# ---- 5) zero intervals from submasks, and t=0 convention ----
def formula_zero(t, j):
    if t == 0: return j == 0
    if abs(j) > t: return False
    s = (t - abs(j)) >> 1
    return (s & r_of(t)) == s
bad = 0
for t in range(0, 1001):
    lim = min(t, W2 - t - 3)
    for j in range(-lim, lim+1):
        if ((st[t] >> (j+W2)) & 1) == 0 != formula_zero(t, j):
            bad += 1
print("Y5) zero-set closed form incl. t=0, t<=1000: mismatches", bad)
