import sys, random
sys.stdout.reconfigure(encoding="utf-8")
random.seed(5)
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length()-1))
def sub(m, s): return (m & s) == m
def formula(t, d):
    if d > t: return 1
    return 0 if sub((t-d)//2, r_of(t)) else 1
# tiny deterministic structure: levels 0..3, one element each, neighborhood {d-1,d,d+1}
lev = {(d,0): d for d in range(4)}
nb = {}
for d in range(4):
    S = {(d,0)}
    if d >= 1: S.add((d-1,0))
    if d+1 <= 3: S.add((d+1,0))
    nb[(d,0)] = S
elems = list(lev)
state = {e: (1 if lev[e]==0 else 0) for e in elems}
print("t=0:", {e: state[e] for e in elems})
for t in range(1, 9):
    ns = {e: (1 if all(state[y] == state[e] for y in nb[e]) else 0) for e in elems}
    state = ns
    got = {d: state[(d,0)] for d in range(4)}
    exp = {d: formula(t, d) for d in range(4)}
    print(f"t={t}: got={got} expected={exp} match={got==exp}")
