"""274_btree_b.py -- the b-ary tree instance, checked numerically for b = 2,3,4.

Vertices are words over {0,...,b-1}; level = depth; the neighbourhood of x is
{x, parent x, all b children}.  The theorem says the root carries the same
middle column (0 exactly at t = 2^k - 1) for every b, and moreover that the
whole state is a function of depth.
"""
def radial(L, T):
    st = [0] * L
    st[0] = 1
    rows = [st[:]]
    for _ in range(T):
        new = [0] * L
        for d in range(L):
            nb = [d - 1, d, d + 1] if d > 0 else [0, 1]
            nb = [e for e in nb if 0 <= e < L]
            v = st[d]
            new[d] = 1 if all(st[e] == v for e in nb) else 0
        st = new
        rows.append(st[:])
    return rows

def run(b, T, D):
    verts = [()]
    frontier = [()]
    for _ in range(D):
        nxt = []
        for v in frontier:
            for i in range(b):
                nxt.append(v + (i,))
        verts.extend(nxt)
        frontier = nxt
    state = {v: (1 if v == () else 0) for v in verts}
    rows = [dict(state)]
    for _ in range(T):
        new = {}
        for v in verts:
            d = len(v)
            nb = [v]
            if d >= 1:
                nb.append(v[:-1])
            if d < D:
                nb.extend(v + (i,) for i in range(b))
            else:
                nb.extend([None] * b)
            val = state[v]
            new[v] = 1 if all((0 if w is None else state[w]) == val for w in nb) else 0
        state = new
        rows.append(dict(state))
    return rows, verts

T = 6
for b in (2, 3, 4):
    D = 8
    rows, verts = run(b, T, D)
    rad = radial(D + 2, T)
    bad = nonuni = checked = 0
    for t in range(T + 1):
        st = rows[t]
        for d in range(0, D - t + 1):
            vals = {st[v] for v in verts if len(v) == d}
            if len(vals) != 1:
                nonuni += 1
            got = vals.pop() if len(vals) == 1 else -1
            checked += 1
            if got != rad[t][d]:
                bad += 1
    mid = [t for t in range(1, T + 1) if rows[t][()] == 0]
    print("b=%d: %d (t,d) pairs, %d mismatches, %d non-uniform levels; root 0 at t=%s"
          % (b, checked, bad, nonuni, mid))