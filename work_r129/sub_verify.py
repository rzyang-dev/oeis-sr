import sys
sys.stdout.reconfigure(encoding="utf-8")

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

def bit(a, j, W):
    return (a >> (j + W)) & 1

def r_of(t):
    return t - (1 << (t.bit_length()-1))

def pred(t, j):
    if t == 0:
        return 1 if j == 0 else 0
    if abs(j) > t:
        return 1
    s = (t - abs(j)) >> 1
    return 0 if (s & r_of(t)) == s else 1

W, T = 1100, 500
st = simulate(W, T)

mism = []
for t in range(T+1):
    lim = min(t+4, W-t-1)
    for j in range(-lim, lim+1):
        b = bit(st[t], j, W); p = pred(t,j)
        if b != p: mism.append((t,j,b,p))
print("1) closed-form mismatches (t<=%d, |j|<=t+4): %d" % (T, len(mism)), mism[:5])

# 5) corrected pair property: x(t,j) == x(t,j-1) when (t-j) even, j>=1
bad = []
for t in range(1, T+1):
    for j in range(1, t+1):
        if ((t-j) & 1) == 0 and bit(st[t],j,W) != bit(st[t],j-1,W):
            bad.append((t,j))
print("5) depth-pair property x(t,j)=x(t,j-1) for (t-j) even: violations", len(bad), bad[:5])

# 9) maximal zero intervals vs maximal runs of submasks of r(t)
bad = []
for t in range(1, T+1):
    r = r_of(t)
    sub = [s for s in range(0, (t>>1)+2) if (s & r) == s]
    # maximal runs of consecutive submasks
    runs = []
    if sub:
        a = b = sub[0]
        for s in sub[1:]:
            if s == b+1: b = s
            else: runs.append((a,b)); a = b = s
        runs.append((a,b))
    pred_int = [(t-2*b-1, t-2*a) for (a,b) in runs]
    # actual
    seg = [j for j in range(0, t+1) if bit(st[t], j, W) == 0]
    act = []
    if seg:
        a = b = seg[0]
        for x in seg[1:]:
            if x == b+1: b = x
            else: act.append((a,b)); a = b = x
        act.append((a,b))
    if pred_int != act: bad.append((t, pred_int, act))
print("9) zero intervals = [t-2b-1, t-2a] over maximal runs of submasks: violations", len(bad), bad[:3])

# 8) decimation hypotheses (TMAX so that 2t+1 <= T)
TMAX = 249
f1=[]; f2=[]; f3=[]
for t in range(1, TMAX+1):
    for j in range(-t-1, t+2):
        if abs(2*j)+2*t+1 <= W:
            if bit(st[2*t+1], 2*j, W) != bit(st[t], j, W): f1.append((t,j))
        if abs(2*j+1)+2*t <= W:
            wall = (bit(st[t-1], j, W) != bit(st[t-1], j+1, W))
            if (bit(st[2*t], 2*j+1, W) == 0) != wall: f2.append((t,j))
        if abs(2*j)+2*t <= W:
            p = (bit(st[t], j, W) == 0) and (((j - t) & 1) == 0)
            if (bit(st[2*t], 2*j, W) == 0) != p: f3.append((t,j))
print("8a) V_{2t+1}(2j)=V_t(j): fails", len(f1), f1[:5])
print("8b) V_{2t}(2j+1)=0 iff wall(t-1,j): fails", len(f2), f2[:5])
print("8c) V_{2t}(2j)=0 iff V_t(j)=0 and j=t mod 2: fails", len(f3), f3[:5])

# 10) print a few rows for sanity
for t in [0,1,2,3,5,6,7,10,11,13,14,15]:
    row = "".join(str(bit(st[t],j,W)) for j in range(-t,t+1))
    print("t=%2d  %s" % (t, row))
