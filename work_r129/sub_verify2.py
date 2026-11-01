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
    M = 1
    i = 0
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
    # bit j (j>=0) = 1 iff floor(j/2) is a submask of r(t)  (i.e. zero at depth j)
    M = submask_mask(r_of(t))
    return doubled(M)

# ---------- Run A: small window, full structural tests ----------
W, T = 1100, 600
st = simulate_store(W, T)
print("A) stored rows W=%d T=%d" % (W, T))

# formula check all t, |j|<=t
bad = 0
for t in range(1, T+1):
    A = (st[t] >> W) & ((1 << (t+1)) - 1)
    D = pred_zero_mask(t) & ((1 << (t+1)) - 1)
    if A != D:
        bad += 1
        if bad <= 3:
            print("   mismatch t=", t, bin(A ^ D))
print("A1) formula mismatches t<=%d (all |j|<=t): %d" % (T, bad))

# era recursion
def Rset(t):
    return frozenset(j for j in range(0, t+1) if (st[t] >> (j+W)) & 1 == 0)
bad = []
for t in range(2, T+1):
    K = t.bit_length()-1; m = t - (1 << K)
    Rt = Rset(t)
    if m < (1 << (K-1)):
        ps = {(1 << (K-1)) + x for x in Rset(t - (1 << (K-1)))}
    else:
        Rm = Rset(m); ps = set(Rm) | {(1 << K) + x for x in Rm}
    if set(Rt) != ps: bad.append(t)
print("A2) era recursion violations t<=%d: %d" % (T, len(bad)), bad[:5])

# decimation identities, using byte arrays for speed
NB = (2*W+1+7)//8
maxrow = 2*300+1
rows = [st[t].to_bytes(NB, 'little') for t in range(maxrow+1)]
def gb(t, j):
    idx = j + W
    return (rows[t][idx >> 3] >> (idx & 7)) & 1
f1=f2=f3=0; ex=[]
for t in range(1, 301):
    for j in range(-t-1, t+2):
        if gb(2*t+1, 2*j) != gb(t, j):
            f1 += 1
            if len(ex) < 3: ex.append(("i", t, j))
        wall = (gb(t-1, j) != gb(t-1, j+1))
        if (gb(2*t, 2*j+1) == 0) != wall:
            f2 += 1
            if len(ex) < 6: ex.append(("ii", t, j))
        p = (gb(t, j) == 0) and (((j - t) & 1) == 0)
        if (gb(2*t, 2*j) == 0) != p:
            f3 += 1
            if len(ex) < 9: ex.append(("iii", t, j))
print("A3) decimation i,ii,iii failures (t<=300):", f1, f2, f3, ex)

# counterexample rows for naive hypotheses
print("A4) example rows (j from -t..t):")
for t in [6, 10, 13, 14, 173]:
    if t <= T:
        row = "".join(str((st[t] >> (j+W)) & 1) for j in range(-t, t+1))
        print("   t=%3d %s" % (t, row[:90] + ("..." if len(row) > 90 else "")))
print("   R(6) =", sorted(Rset(6)), " R(2) =", sorted(Rset(2)))

# ---------- Run B: huge window, streamed formula check ----------
W2, T2 = 40001, 20000
mask = (1 << (2*W2+1)) - 1
a = 1 << W2
badcount = 0; badout = 0
t0 = time.time()
for t in range(1, T2+1):
    L = (a << 1) & mask
    R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    # check formula for j=0..t
    A = (a >> W2) & ((1 << (t+1)) - 1)
    D = pred_zero_mask(t) & ((1 << (t+1)) - 1)
    if A != D:
        badcount += 1
        if badcount <= 3: print("   B mismatch t=", t)
    # no zeros outside [-t,t]
    zeros = (~a) & mask
    win = ((1 << (2*t+1)) - 1) << (W2 - t)
    if zeros & ~win:
        badout += 1
        if badout <= 3: print("   B outside-cone zero at t=", t)
print("B) streamed W=%d T=%d: formula mismatches %d, zeros outside cone %d, %.1fs"
      % (W2, T2, badcount, badout, time.time() - t0))
