import sys
sys.stdout.reconfigure(encoding="utf-8")
W, T = 4200, 2000
mask = (1 << (2*W+1)) - 1
a = 1 << W
st = [a]
for _ in range(T):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    st.append(a)
bad = 0
for t in range(1, T+1):
    for j in range(1, t+1):
        if ((t-j) & 1) == 0:
            if ((st[t] >> (j+W)) & 1) != ((st[t] >> (j-1+W)) & 1):
                bad += 1
                if bad <= 3: print("bad", t, j)
print("depth-pair property x(t,j)=x(t,j-1) for t-j even, t<=%d: violations %d" % (T, bad))
