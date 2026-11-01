import sys, time
sys.stdout.reconfigure(encoding="utf-8")

def r_of(t):
    return t - (1 << (t.bit_length()-1))

def formula_zero(t, j):
    if t == 0: return j == 0
    if abs(j) > t: return False
    s = (t - abs(j)) >> 1
    return (s & r_of(t)) == s

# ---- naive independent simulation (plain lists) ----
Wn, Tn = 900, 300
n = 2*Wn+1
a = [0]*n; a[Wn] = 1
naive = [a[:]]
for _ in range(Tn):
    b = [0]*n
    for i in range(1, n-1):
        if a[i-1] == a[i] == a[i+1]: b[i] = 1
    a = b; naive.append(a[:])

# ---- bitmask simulation ----
def simulate(W, T):
    mask = (1 << (2*W+1)) - 1
    a = 1 << W
    out = [a]
    for _ in range(T):
        L = (a << 1) & mask
        R = a >> 1
        a = ((L & a & R) | (~(L | a | R) & mask)) & mask
        out.append(a)
    return out
W, T = 4200, 2000
st = simulate(W, T)

# cross-implementation check
bad = []
for t in range(Tn+1):
    lim = min(t, Wn - t - 2)
    for j in range(-lim, lim+1):
        if ((st[t] >> (j+W)) & 1) != naive[t][j+Wn]:
            bad.append((t,j)); break
    if bad: break
print("X1) bitmask vs naive-list simulation disagreements (t<=%d): %s" % (Tn, bad[:3]))

# ---- exhaustive closed-form check t<=2000, all |j|<=t ----
bad = 0
t0 = time.time()
for t in range(1, T+1):
    r = r_of(t)
    lim = min(t, W - t - 2)
    for j in range(0, lim+1):
        act = (st[t] >> (j+W)) & 1
        s = (t - j) >> 1
        pred = 0 if ((s & r) == s) else 1
        if act != pred:
            bad += 1
            if bad <= 5: print("   mismatch t,j=", t, j)
            break
print("X2) exhaustive closed-form check t<=%d, 0<=j<=t (and by symmetry j<0): mismatches=%d  [%.1fs]"
      % (T, bad, time.time()-t0))

# ---- no zeros outside light cone; count ----
badout = [t for t in range(1, T+1)
          if ((~st[t]) & ((1 << (2*W+1))-1) & ~(((1 << (2*min(t,W-t-2)+1))-1) << (W-min(t,W-t-2)))) != 0]
print("X3) zeros outside |j|<=t (within trusted window): ", badout[:5])
bad = []
for t in range(1, T+1):
    z = (~st[t]) & ((1 << (t+1)) - 1) << W
    if bin(z).count('1') != (1 << bin(t).count('1')): bad.append((t, bin(z).count('1')))
print("X4) |Z(t) cap [0,t]| = 2^popcount(t) violations:", bad[:5])

# ---- middle column ----
bad = [t for t in range(1, T+1) if (((st[t] >> W) & 1) == 0) != ((t & (t+1)) == 0)]
print("X5) middle column (A267442) violations:", bad[:5])

# ---- era recursion of zero set ----
def Rzero(t):
    return frozenset(j for j in range(0, t+1) if ((st[t] >> (j+W)) & 1) == 0)
bad = []
for t in range(2, T//2):
    K = t.bit_length()-1; m = t - (1 << K)
    Rt = Rzero(t)
    if m < (1 << (K-1)):
        ps = {(1 << (K-1)) + x for x in Rzero(t - (1 << (K-1)))}
    else:
        Rm = Rzero(m); ps = set(Rm) | {(1 << K) + x for x in Rm}
    if set(Rt) != ps: bad.append(t)
print("X6) era recursion, violations t<=%d: %d" % (T//2-1, len(bad)), bad[:5])

# ---- edge process ----
def E(t):
    return {j for j in range(-t-1, t+1) if ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1)}

TE = 1200
Es = {t: E(t) for t in range(0, TE+1)}
print("X7) E_0..E_8:", [sorted(Es[t]) for t in range(9)])

bad = []
for t in range(0, TE-1):
    for j in range(-t-1, t+1):
        x0 = ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1)
        xl = ((st[t] >> (j-1+W)) & 1) != ((st[t] >> (j+W)) & 1)
        xr = ((st[t] >> (j+1+W)) & 1) != ((st[t] >> (j+2+W)) & 1)
        nxt = ((st[t+1] >> (j+W)) & 1) != ((st[t+1] >> (j+1+W)) & 1)
        if nxt != ((not x0) and (xl != xr)): bad.append((t,j))
print("X8) edge CA = rule 18 violations:", len(bad), bad[:4])

def Rh(t): return {j for j in Es[t] if j >= 0}
bad1 = [m for m in range(0, TE//2) if Rh(2*m+1) != {2*j+1 for j in Rh(m)}]
bad2 = [m for m in range(1, TE//2) if Rh(2*m) != {2*i for i in (Rh(m-1) | {j+1 for j in Rh(m-1)})}]
print("X9)  R_{2m+1} = 2R_m+1 violations m<=%d: %d %s" % (TE//2-1, len(bad1), bad1[:4]))
print("X10) R_{2m} = 2(R_{m-1} u (R_{m-1}+1)) violations m<=%d: %d %s" % (TE//2-1, len(bad2), bad2[:4]))

bad = []
for t in range(0, TE):
    for j in Es[t]:
        ok = ((j - (t+1)) % 2 == 0) if j < 0 else ((j - t) % 2 == 0)
        if not ok: bad.append((t,j))
print("X11) parity invariant violations:", len(bad), bad[:4])

bad = []
for t in range(1, TE):
    lhs = ((st[t] >> W) & 1) == 0          # x(t,0)==0
    e = ((st[t-1] >> W) & 1) != ((st[t-1] >> (W+1)) & 1)
    if lhs != e: bad.append(t)
print("X12) x(t,0)=0 iff e_{t-1}(0)=1 violations:", len(bad), bad[:4])

bad = [t for t in range(0, TE) if (0 in Es[t]) != ((t+2) & (t+1) == 0)]
print("X13) e_t(0)=1 iff t+2=2^k violations:", len(bad), bad[:6])

for k in range(1, 11):
    t = (1 << k) - 2
    if t > TE: break
    pred = {j for j in range(-(t+1), t+2)
            if ((j < 0 and (j-(t+1)) % 2 == 0) or (j >= 0 and (j-t) % 2 == 0))}
    if Es[t] != pred: print("   full-alt FAIL at t=", t)
print("X14) full-alternating E_t at t=2^k-2 verified for k<=10 (t<=%d)" % TE)

# claim: |E_{2^k+m}| = 2|E_m|
hits = []; misses = []
for k in range(1, 8):
    for m in range(0, 20):
        t = (1 << k) + m
        if t > TE: continue
        (hits if len(Es[t]) == 2*len(Es[m]) else misses).append((k, m, len(Es[t]), 2*len(Es[m])))
print("X15) |E_{2^k+m}| = 2|E_m|: holds %d, fails %d; first fails %s" % (len(hits), len(misses), misses[:6]))
print("     |E_t| for t=0..20:", [len(Es[t]) for t in range(21)])
