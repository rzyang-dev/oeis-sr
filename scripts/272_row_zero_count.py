"""272_row_zero_count.py -- the 1-D zero count from the shell set.

Claim: number of j with row t j = 0  =  2 * #shell t - [0 in shell t].
Checked against a direct simulation of rule 129 (all three neighbours equal)
from a single 1 at the origin.
"""
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def shell(t):
    r = r_of(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & r == ((t - d) // 2)]

def sim(T):
    R = 2 * T + 3
    N = 2 * R + 1
    g = [0] * N
    g[R] = 1
    rows = [g[:]]
    for _ in range(T):
        new = [0] * N
        for i in range(1, N - 1):
            v = g[i]
            new[i] = 1 if (g[i-1] == v and g[i] == v and g[i+1] == v) else 0
        g = new
        rows.append(g[:])
    return rows, R

T = 30
rows, R = sim(T)
bad = 0
for t in range(1, T + 1):
    zeros = sum(1 for j in range(R - t, R + t + 1) if rows[t][j] == 0)
    s = shell(t)
    pred = 2 * len(s) - (1 if 0 in s else 0)
    if zeros != pred:
        bad += 1
        print("mismatch t=%d sim=%d pred=%d" % (t, zeros, pred))
print("t<=%d: %d mismatches" % (T, bad))
print("zero counts:", [sum(1 for j in range(R - t, R + t + 1) if rows[t][j] == 0) for t in range(1, 17)])
print("#shell t   :", [len(shell(t)) for t in range(1, 17)])
