import sys, random
sys.stdout.reconfigure(encoding="utf-8")
random.seed(5)
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length()-1))
def sub(m, s): return (m & s) == m
def formula(t, d):
    if d > t: return 1
    return 0 if sub((t-d)//2, r_of(t)) else 1
def build(levels_max=6, tries=200):
    # build a random leveled structure: elements (d, i), neighborhoods satisfying hypotheses
    elems = []
    for d in range(levels_max+1):
        for i in range(random.randint(2,4)):
            elems.append((d,i))
    lev = {e: e[0] for e in elems}
    nb = {}
    for e in elems:
        d = e[0]
        S = {e}
        if d >= 1:
            cands = [x for x in elems if x[0] == d-1]
            if cands: S.add(random.choice(cands))
            else: return None
        cands = [x for x in elems if x[0] == d+1]
        if cands: S.add(random.choice(cands))
        else: return None
        # optionally add more within levels d-1,d,d+1
        for x in elems:
            if abs(x[0]-d) <= 1 and random.random() < 0.3:
                S.add(x)
        nb[e] = S
    return elems, lev, nb
def simulate(elems, lev, nb, T):
    state = {e: (1 if lev[e]==0 else 0) for e in elems}
    states = [dict(state)]
    for t in range(T):
        ns = {}
        for e in elems:
            ns[e] = 1 if all(state[y] == state[e] for y in nb[e]) else 0
        state = ns
        states.append(dict(state))
    return states
bad = 0; tot = 0; built = 0
for _ in range(60):
    B = build()
    if B is None: continue
    elems, lev, nb = B
    built += 1
    states = simulate(elems, lev, nb, 40)
    for t in range(1, 41):
        for e in elems:
            tot += 1
            if states[t][e] != formula(t, lev[e]): bad += 1
print(f"structures built: {built}, cells checked: {tot}, formula mismatches: {bad}")
