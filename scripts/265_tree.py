"""265_tree.py -- the all-equal rule on the infinite binary tree.

Vertices are finite binary words.  Level = depth.  The neighbourhood of a
vertex is {itself, its parent, its two children} (3 cells at the root).
Rule: y'(v) = 1 iff all neighbours of v carry the same value as v does.

Compare with the 1D radial level dynamics (level d, nbhd {d-1,d,d+1}),
which is another geometry satisfying (H1)-(H4).
"""
import sys

T = 12
D = T + 3

# ---- radial level dynamics on N -------------------------------------
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

L = D + 2
rad = radial(L, T)

# ---- tree dynamics ---------------------------------------------------
def parent(v): return v[:-1]
def kids(v): return (v + (0,), v + (1,))

def vertices(depth):
    out = [()]
    frontier = [()]
    for _ in range(depth):
        nxt = []
        for v in frontier:
            nxt.extend(kids(v))
        out.extend(nxt)
        frontier = nxt
    return out

verts = vertices(D)
state = {v: (1 if v == () else 0) for v in verts}
rows = [dict(state)]

for _ in range(T):
    new = {}
    for v in verts:
        d = len(v)
        nb = [v]
        if d >= 1:
            nb.append(parent(v))
        if d < D:
            nb.extend(kids(v))
        else:
            nb.extend([None, None])   # truncated: value 0 outside
        val = state[v]
        ok = all((0 if w is None else state[w]) == val for w in nb)
        new[v] = 1 if ok else 0
    state = new
    rows.append(dict(state))

# ---- compare ---------------------------------------------------------
bad = 0
checked = 0
nonuniform = 0
for t in range(T + 1):
    st = rows[t]
    # level uniformity + comparison with the radial rows, inside the cone
    for d in range(0, D - t + 1):
        vals = {st[v] for v in verts if len(v) == d}
        if len(vals) != 1:
            nonuniform += 1
        got = vals.pop() if len(vals) == 1 else -1
        exp = rad[t][d]
        checked += 1
        if got != exp:
            bad += 1
            if bad <= 5:
                print("MISMATCH t=%d d=%d tree=%s radial=%d" % (t, d, got, exp))

print("checked %d (t,d) pairs, %d mismatches, %d non-uniform levels" % (checked, bad, nonuniform))

mid = [t for t in range(1, T + 1) if rows[t][()] == 0]
pred = [t for t in range(1, T + 1) if (t & (t + 1)) == 0]
print("root is 0 at t =", mid)
print("2^k - 1          :", pred)
print("MATCH" if mid == pred else "FAIL")
