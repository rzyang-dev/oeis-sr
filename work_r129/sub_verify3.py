import sys, time
sys.stdout.reconfigure(encoding="utf-8")

def simulate_store(W, T):
    mask = (1 << (2*W+1)) - 1
    a = 1 << W
    out = [a]
    for _ in range(T):
        L = (a << 1) & mask
        R = a >> 1
        a = ((L & a & R) | (~(L | a | R) & mask)) & mask
        out.append(a)
    return out

def r_of(t):
    return t - (1 << (t.bit_length()-1))

DOUBLE = [0]*256
for b in range(256):
    v = 0
    for i in range(8):
        if (b >> i) & 1: v |= 3 << (2*i)
    DOUBLE[b] = v

def submask_mask(r):
    M = 1; i = 0
    while r:
        if r & 1: M |= M << (1 << i)
        r >>= 1; i += 1
    return M

def doubled(M):
    out = 0; sh = 0
    while M:
        out |= DOUBLE[M & 0xFF] << sh
        M >>= 8; sh += 16
    return out

def pred_zero_mask(t):
    return doubled(submask_mask(r_of(t)))

# ---------- Run A ----------
W, T = 1400, 700
st = simulate_store(W, T)
print("A) stored rows W=%d T=%d" % (W, T))

bad = 0
for t in range(1, T+1):
    stbits = (st[t] >> W) & ((1 << (t+1)) - 1)
    Zsim = stbits ^ ((1 << (t+1)) - 1)
    D = pred_zero_mask(t) & ((1 << (t+1)) - 1)
    if Zsim != D:
        bad += 1
        if bad <= 3: print("   mismatch t=", t, bin(Zsim ^ D))
print("A1) closed-form mismatches t<=%d (all |j|<=t): %d" % (T, bad))

import functools
def Rzero(t):
    return frozenset(j for j in range(0, t+1) if ((st[t] >> (j+W)) & 1) == 0)
bad = []
for t in range(2, T//2+1):
    K = t.bit_length()-1; m = t - (1 << K)
    Rt = Rzero(t)
    if m < (1 << (K-1)):
        ps = {(1 << (K-1)) + x for x in Rzero(t - (1 << (K-1)))}
    else:
        Rm = Rzero(m); ps = set(Rm) | {(1 << K) + x for x in Rm}
    if set(Rt) != ps: bad.append(t)
print("A2) era recursion of zero set, violations t<=%d: %d" % (T//2, len(bad)), bad[:5])

# edge sets
def E(t, jmax=None):
    if jmax is None: jmax = t+1
    s = set()
    for j in range(-jmax, jmax+1):
        if ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1): s.add(j)
    return s
print("A3) E_0 =", sorted(E(0)), " E_1 =", sorted(E(1)), " E_2 =", sorted(E(2)), " E_3 =", sorted(E(3)), " E_4 =", sorted(E(4)))

# rule 18 check
bad = []
for t in range(0, T-1):
    for j in range(-(t+1), t+2):
        x0 = ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1)
        xl = ((st[t] >> (j-1+W)) & 1) != ((st[t] >> (j+W)) & 1)
        xr = ((st[t] >> (j+1+W)) & 1) != ((st[t] >> (j+2+W)) & 1)
        nxt = ((st[t+1] >> (j+W)) & 1) != ((st[t+1] >> (j+1+W)) & 1)
        if nxt != ((not x0) and (xl != xr)): bad.append((t,j))
print("A4) edge CA = rule 18 violations:", len(bad), bad[:4])

# edge-recursion checks
bad1=[]; bad2=[]; bad3=[]
for m in range(0, T//2):
    Rm = E(m) ; Rm = {j for j in Rm if j >= 0}
    R2m1 = {j for j in E(2*m+1) if j >= 0}
    if R2m1 != {2*j+1 for j in Rm}: bad1.append(m)
for m in range(1, T//2):
    Rm1 = {j for j in E(m-1) if j >= 0}
    R2m = {j for j in E(2*m) if j >= 0}
    pred = {2*j for j in (Rm1 | {j+1 for j in Rm1})}
    if R2m != pred: bad2.append(m)
print("A5) R_{2m+1} = 2R_m+1 violations m<=%d: %d" % (T//2-1, len(bad1)), bad1[:5])
print("A6) R_{2m} = 2(R_{m-1} u (R_{m-1}+1)) violations m<=%d: %d" % (T//2-1, len(bad2)), bad2[:5])

# parity invariant, middle-cell relation, full-alternating states, target theorem
bad=[]; 
for t in range(0, T//2):
    for j in E(t):
        par = (j - (t+1)) % 2 == 0 if j < 0 else (j - t) % 2 == 0
        if not par: bad.append((t,j))
print("A7) parity invariant violations:", len(bad), bad[:4])

bad = [t for t in range(1, T//2) if (((st[t] >> W) & 1) == 1) != (((st[t-1] >> (W)) & 1) != ((st[t-1] >> (W+1)) & 1))]
print("A8) state_t(0) = 1 - e_{t-1}(0) violations:", len(bad), bad[:4])

bad = [t for t in range(0, T//2) if ((0 in E(t)) != ((t+2) & (t+1) == 0))]
print("A9) e_t(0)=1 iff t+2 is a power of 2, violations t<=%d:" % (T//2), len(bad), bad[:6])

# full alternating at t = 2^k-2
for k in range(1, 10):
    t = (1 << k) - 2
    if t > T//2: break
    Et = E(t)
    pred = {j for j in range(-(t+1), t+2) if ((j < 0 and (j - (t+1)) % 2 == 0) or (j >= 0 and (j - t) % 2 == 0))}
    print("   t=%-4d full-alternating E_t == predicted: %s (|E|=%d, t+2=%d)" % (t, Et == pred, len(Et), t+2))

# claim 6: |E_{2^k+m}| = 2|E_m| ?
print("A10) test |E_{2^k+m}| = 2|E_m| for k<=6, m<=11:")
hits=[]; misses=[]
for k in range(1, 7):
    for m in range(0, 12):
        t = (1<<k)+m
        if t > T//2: continue
        lhs = len(E(t)); rhs = 2*len(E(m))
        (hits if lhs==rhs else misses).append((k,m,lhs,rhs))
print("   holds:", len(hits), " fails:", len(misses), " first fails:", misses[:6])

# closed-form edge formula
bad=[]
for t in range(1, T//2):
    r = r_of(t)
    for j in range(0, t+1):
        d = t - j
        if d & 1:
            pred = 0
        else:
            s = d >> 1
            a = ((s & r) == s)
            b = s > 0 and (((s-1) & r) == (s-1))
            pred = 1 if a != b else 0
        act = 1 if ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1) else 0
        if pred != act: bad.append((t,j))
print("A11) closed-form edge formula violations:", len(bad), bad[:4])
