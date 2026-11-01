"""278_shell_matrix_rank.py -- what the zero counts can and cannot see.

The counts are  #Z(t) = sum_{d in S(t)} c_d  with  S(t) = {d : (t-d)/2 subset r(t)}.
Two questions:
  (1) is the map  c |-> (#Z(t))_{t>=1}  injective?
  (2) if not, what is its kernel?

The shell is a disjoint union of the consecutive pairs {t-2m, t-2m-1}, so the
alternating weight (-1)^d cancels on every shell: the kernel contains the
alternating sequence.  The rank computation shows the kernel is exactly that.
"""
from fractions import Fraction

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

bad = 0
for t in range(1, 5001):
    s = shell(t)
    if sum(1 if d % 2 == 0 else -1 for d in s) != 0:
        bad += 1
        print("alternating sum does not vanish at t =", t)
    if len([d for d in s if d % 2 == 0]) != len([d for d in s if d % 2 == 1]):
        bad += 1
        print("parity balance fails at t =", t)
print("t <= 5000: every shell has equally many even and odd levels:",
      "0 failures" if bad == 0 else "%d failures" % bad)

def rank(rows, ncols):
    M = [[Fraction(x) for x in row] for row in rows]
    nrows = len(M)
    rk = 0
    for col in range(ncols):
        piv = None
        for i in range(rk, nrows):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        pv = M[rk][col]
        M[rk] = [x / pv for x in M[rk]]
        for i in range(nrows):
            if i != rk and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk

for T in [4, 6, 10, 14, 20, 30]:
    rows = []
    for t in range(1, T + 1):
        row = [0] * (T + 1)
        for d in shell(t):
            row[d] = 1
        rows.append(row)
    rk = rank(rows, T + 1)
    print("T=%2d: %2d equations, %2d unknown levels, rank = %2d  (kernel dimension %d)"
          % (T, T, T + 1, rk, T + 1 - rk))

print()
print("S(t) for t = 1..8:", [shell(t) for t in range(1, 9)])
print("the pairs {t-2m, t-2m-1} are visible in every one of them")
