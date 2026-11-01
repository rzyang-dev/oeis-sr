"""266_shells.py -- the zero set of the all-equal rule on Z^2 is a union
of complete level shells, and the number of zeros is a shell sum.

Closed form (universal theorem):
    x_t(v) = 0  <=>  |v| <= t  and  floor((t-|v|)/2) is a submask of r(t),
    r(t) = t - 2^floor(log2 t).
Hence in EVERY geometry the zero set is a union of whole shells, and
    #zeros(t) = sum_{d} c_d * [condition(d)],
c_d = shell size.  We check this against a direct simulation.
"""

def rmask(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def cond(t, d):
    if d > t:
        return False
    m = (t - d) // 2
    return (m & rmask(t)) == m

MOORE = "moore"
VN = "vn"

def nbrs(v, kind):
    i, j = v
    if kind == MOORE:
        return [(i + a, j + b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    return [(i, j), (i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]

def level(v, kind):
    i, j = v
    return max(abs(i), abs(j)) if kind == MOORE else abs(i) + abs(j)

def step(Z, kind):
    """Z = set of cells carrying 0.  Returns the new set of zeros."""
    out = set()
    cand = set()
    for v in Z:
        cand.add(v)
        cand.update(nbrs(v, kind))
    for v in cand:
        nb = nbrs(v, kind)
        if v in Z:
            if any(w not in Z for w in nb):   # a 1 next door
                out.add(v)
        else:
            if any(w in Z for w in nb):       # a 0 next door
                out.add(v)
    return out

def run(T, kind):
    # t = 1 is known analytically: the zeros are exactly the neighbourhood of
    # the origin (the origin itself is not all-equal because of its 0 neighbours).
    Z = {(i, j) for i in range(-1, 2) for j in range(-1, 2)} if kind == MOORE         else {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}
    rows = [None, set(Z)]
    for _ in range(T - 1):
        Z = step(Z, kind)
        rows.append(set(Z))
    return rows

T = 32
for kind, name, sh in ((MOORE, "Z^2 Moore (9-cell)", lambda d: 1 if d == 0 else 8 * d),
                       (VN, "Z^2 von Neumann (5-cell)", lambda d: 1 if d == 0 else 4 * d)):
    rows = run(T, kind)
    struct_bad = 0
    count_bad = 0
    counts = []
    for t in range(1, T + 1):
        Z = rows[t]
        lv = {level(v, kind) for v in Z}
        # every present level must be completely zero, and no other level may appear
        for d in lv:
            ring = set()
            for v in Z:
                if level(v, kind) == d:
                    ring.add(v)
            # build the full shell by expanding from a point of that level
            # (cheap: iterate over the bounding box of radius d)
            full = {(i, j) for i in range(-d, d + 1) for j in range(-d, d + 1)
                    if level((i, j), kind) == d}
            if not full <= Z:
                struct_bad += 1
        if lv != {d for d in range(t + 1) if cond(t, d)}:
            struct_bad += 1
        pred = sum(sh(d) for d in range(t + 1) if cond(t, d))
        if pred != len(Z):
            count_bad += 1
        counts.append(len(Z))
    print("%s: shell violations = %d, shell-sum mismatches = %d" % (name, struct_bad, count_bad))
    print("   #zeros t=1..%d: %s" % (T, counts))

print()
print("t   zero shells (d with cond)      #zeros 1D   #zeros vN   #zeros Moore")
for t in range(1, 25):
    ds = [d for d in range(t + 1) if cond(t, d)]
    z1 = sum(1 if d == 0 else 2 for d in ds)
    zv = sum(1 if d == 0 else 4 * d for d in ds)
    zm = sum(1 if d == 0 else 8 * d for d in ds)
    print("%-3d %-30s %-11d %-11d %d" % (t, str(ds), z1, zv, zm))
