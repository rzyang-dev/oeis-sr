import sys
from math import comb
sys.stdout.reconfigure(encoding="utf-8")
lo, hi = -200, 200
def step(E):
    newE = set()
    for j in range(lo, hi):
        b = (j in E); a = ((j-1) in E); c = ((j+1) in E)
        if (not b) and (a != c): newE.add(j)
    return newE
E = {-1, 0}
T = []
for t in range(30):
    T.append(set(E)); E = step(E)
def e(t,j): return 1 if j in T[t] else 0
def r90(t,j):
    # from initial cells at -1 and 0: C(t, j-(-1)) + C(t, j-0) mod 2
    s = 0
    for p in (-1, 0):
        d = j - p
        if 0 <= d <= t: s += comb(t, d)
    return s % 2
bad = []
for t in range(25):
    for j in range(-t-1, t+2):
        if e(t,j) == 1 and r90(t,j) == 0: bad.append((t,j))
print("violations of subset:", len(bad), bad[:10])
# also check: e_t(j) and e_t(-1-j) symmetry
sym = all(e(t,j)==e(t,-1-j) for t in range(20) for j in range(-20,20))
print("symmetry:", sym)
# check rule 18 vs rule 90 relationship on the diagonal
print("sample t=10:", [(j, e(10,j), r90(10,j)) for j in range(-11,12)])
