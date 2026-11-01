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
for t in range(25):
    T.append(set(E)); E = step(E)
def e(t, j): return 1 if j in T[t] else 0
# test candidates
cands = {
 "C(t,j+1)": lambda t,j: comb(t, j+1) % 2 if 0 <= j+1 <= t else 0,
 "C(t,j+2)": lambda t,j: comb(t, j+2) % 2 if 0 <= j+2 <= t else 0,
 "C(t+1,j+1)": lambda t,j: comb(t+1, j+1) % 2 if 0 <= j+1 <= t+1 else 0,
 "C(t+1,j+2)": lambda t,j: comb(t+1, j+2) % 2 if 0 <= j+2 <= t+1 else 0,
 "C(t+2,j+2)": lambda t,j: comb(t+2, j+2) % 2 if 0 <= j+2 <= t+2 else 0,
}
for name, f in cands.items():
    ok = 0; tot = 0
    for t in range(0, 20):
        for j in range(-t-1, t+2):
            tot += 1
            if f(t, j) == e(t, j): ok += 1
    print(f"{name}: {ok}/{tot}")
print("actual E_t for t=0..8:")
for t in range(9):
    print(t, sorted(T[t]))
