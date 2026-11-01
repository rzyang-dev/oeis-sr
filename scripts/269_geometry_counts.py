def rmask(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))
def S(t):
    r = rmask(t)
    return sorted({t - 2*m for m in []} | {x for m in range(0, r+1) if (m & r) == m for x in (t-2*m, t-2*m-1) if 0 <= x <= t})
T = 24
one, vn, mo, tree = [], [], [], []
for t in range(1, T+1):
    s = S(t)
    one.append(sum(1 if d == 0 else 2 for d in s))
    vn.append(sum(1 if d == 0 else 4*d for d in s))
    mo.append(sum(1 if d == 0 else 8*d for d in s))
    tree.append(sum(2**d for d in s))
print("S(t) for t=1..8:", [S(t) for t in range(1,9)])
print("1D      :", ",".join(map(str, one)))
print("vN      :", ",".join(map(str, vn)))
print("Moore   :", ",".join(map(str, mo)))
print("tree    :", ",".join(map(str, tree)))
