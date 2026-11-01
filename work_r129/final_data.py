import sys, random
sys.stdout.reconfigure(encoding="utf-8")
def r_of(t): return t - (1 << (t.bit_length()-1))

# raw simulation, W=4200 T=2000, streamed
W, T = 4200, 2000
mask = (1 << (2*W+1)) - 1
a = 1 << W
st = [a]
for _ in range(T):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    st.append(a)

def zero_formula(t, j):
    if t == 0: return j != 0
    if abs(j) > t: return False
    s = (t - abs(j)) >> 1
    return (s & r_of(t)) == s

# final: zero-set formula incl. t=0
bad = 0
for t in range(0, T+1):
    lim = min(t, W - t - 3)
    for j in range(-lim, lim+1):
        if (((st[t] >> (j+W)) & 1) == 0) != zero_formula(t, j): bad += 1
print("FINAL zero-set formula (incl. t=0): mismatches over t<=%d = %d" % (T, bad))

print()
print("Zero sets Z(t) cap [0,t] for t=0..20:")
for t in range(0, 21):
    zs = [j for j in range(0, t+1) if zero_formula(t, j)]
    print("  t=%2d r=%2d  |Z|=%2d  %s" % (t, r_of(t) if t else 0, len(zs), zs))

print()
print("Row r(t) interpretation, t=173 = 10101101_2, r=45 = 101101_2")
subs = [s for s in range(0, 46) if (s & 45) == s]
print("  submasks of 45:", subs)
Z = sorted({x for s in subs for x in (173-2*s, 173-2*s-1) if x >= 0})
print("  Z(173) cap [0,173]:", Z)
# merge
merged = []
for x in Z:
    if merged and x == merged[-1][1]+1: merged[-1] = (merged[-1][0], x)
    else: merged.append((x,x))
print("  merged:", merged)

print()
print("ASCII diagram rows t=0..31, columns j=-31..31  (# = 1, . = 0), r(t) at right")
for t in range(0, 32):
    row = "".join("#" if ((st[t] >> (j+W)) & 1) else "." for j in range(-31, 32))
    print("%2d %s  r=%d" % (t, row, r_of(t) if t else 0))

print()
print("Counts: |Z(t) cap [0,t]| = 2^popcount(t); |E_t| = 2^popcount(t+1)")
for t in [0,1,2,3,6,7,10,14,15,31,63,127,173,255]:
    if t <= T:
        zc = sum(1 for j in range(0,t+1) if zero_formula(t,j))
        ec = sum(1 for j in range(-t-1, t+1) if ((st[t] >> (j+W)) & 1) != ((st[t] >> (j+1+W)) & 1))
        print("  t=%3d popcount(t)=%d  |Z|=%d (2^%d)   popcount(t+1)=%d  |E|=%d"
              % (t, bin(t).count('1'), zc, bin(t).count('1'), bin(t+1).count('1'), ec))
