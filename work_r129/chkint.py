import sys
sys.stdout.reconfigure(encoding="utf-8")
def r_of(t): return t - (1 << (t.bit_length()-1))
W, T = 1500, 700
mask = (1 << (2*W+1)) - 1
a = 1 << W
st = [a]
for _ in range(T):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    st.append(a)
bad = 0
for t in range(1, T+1):
    r = r_of(t)
    subs = [s for s in range(0, (t>>1)+1) if (s & r) == s]
    runs = []
    if subs:
        x = y = subs[0]
        for s in subs[1:]:
            if s == y+1: y = s
            else: runs.append((x,y)); x = y = s
        runs.append((x,y))
    pred = sorted((t-2*b-1, t-2*a) for (a,b) in runs)
    seg = [j for j in range(0, t+1) if ((st[t] >> (j+W)) & 1) == 0]
    act = []
    if seg:
        x = y = seg[0]
        for s in seg[1:]:
            if s == y+1: y = s
            else: act.append((x,y)); x = y = s
        act.append((x,y))
    if pred != sorted(act):
        bad += 1
        if bad <= 3: print("bad", t, pred[:4], sorted(act)[:4])
print("interval decomposition into [t-2b-1, t-2a] over maximal runs of submasks: violations t<=%d = %d" % (T, bad))
