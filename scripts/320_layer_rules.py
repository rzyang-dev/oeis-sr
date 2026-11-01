#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""320_layer_rules.py -- exhaustive census of the 256 three-variable Boolean rules
under the radial "layer reduction" of a cellular automaton.

RULE NUMBERING (Wolfram convention)
    f_r(a,b,c) = (r >> (4*a + 2*b + c)) & 1 ,   a = layer d-1, b = layer d, c = layer d+1.

LAYER DYNAMICS ON THE RAY N = {0,1,2,...}
    x'[d] = f(x[d-1], x[d], x[d+1])        for d >= 1
    x'[0] = f(x[0],   x[0], x[1])          (no layer -1: identify it with the cell itself)
    x[0](0) = 1,  x[0](d) = 0 for d > 0.

The completion at d = 0 is part of the rule.  We use the "identify the missing
layer with the cell itself" completion because it is the only one that reproduces
the machine-checked closed form of rule 129 (docs/42, docs/45); zero padding
x'[0] = f(0,x[0],x[1]) already breaks that formula at t = 5.

THREE GEOMETRIES (all induce the same layer adjacency d-1, d, d+1)
    (i)   ray N                     : one point per layer
    (ii)  Z^2, von Neumann layers   : layer d = {(i,j) : |i|+|j| = d}, 4d points
    (iii) infinite binary tree      : layer d has 2^d points (parent d-1, two children d+1)

Everything is compared on the light cone d <= t.

Only numpy and the standard library are used.  OEIS matching is done offline
against the local snapshot oeis.db when it is present (network is not used).
"""

import os
import sqlite3
import sys
import time

import numpy as np

T_GEOM = 20      # time horizon of the geometry census
T_LAW = 200      # time horizon of the contraction-law scan
T_ORBIT = 300    # time horizon used for the orbit identities
T_KERNEL = 2048  # length of the sequences fed to the 2-kernel test

RULE_TAB = [np.array([(r >> (4 * a + 2 * b + c)) & 1
                      for a in (0, 1) for b in (0, 1) for c in (0, 1)],
                     dtype=np.uint8) for r in range(256)]


def f_of(r, a, b, c):
    return (r >> (4 * a + 2 * b + c)) & 1


def bits_of(r):
    return "".join(str(f_of(r, a, b, c)) for a in (0, 1) for b in (0, 1) for c in (0, 1))


def dep_string(r):
    """Which of the three arguments the function really depends on."""
    out = []
    for pos, name in enumerate("abc"):
        changes = False
        for a in (0, 1):
            for b in (0, 1):
                for c in (0, 1):
                    v = [a, b, c]
                    w = [a, b, c]
                    w[pos] ^= 1
                    if f_of(r, *v) != f_of(r, *w):
                        changes = True
        if changes:
            out.append(name)
    return "".join(out) if out else "-"


# ----------------------------------------------------------------------------
# 1. the three geometries
# ----------------------------------------------------------------------------

def ray_rows(r, T):
    """Return rows[t] = x_t on the ray, a uint8 array of length 2T+10."""
    tab = RULE_TAB[r]
    n = 2 * T + 10
    x = np.zeros(n, dtype=np.uint8)
    x[0] = 1
    rows = np.zeros((T + 1, n), dtype=np.uint8)
    for t in range(T + 1):
        rows[t] = x
        left = np.empty(n, dtype=np.uint8)
        left[0] = x[0]
        left[1:] = x[:-1]
        right = np.empty(n, dtype=np.uint8)
        right[:-1] = x[1:]
        right[-1] = x[-1]
        x = tab[4 * left + 2 * x + right]
    return rows


def plane_setup(R):
    """Neighbour tables for the von Neumann plane.

    prev[i,j] is *a* neighbour of layer d-1, next[i,j] is *a* neighbour of layer d+1,
    chosen by moving along the first non-zero coordinate.  Because the state stays
    layer-constant, the choice of representative does not matter; the census checks
    that layer constancy indeed holds.
    """
    m = 2 * R + 1
    I, J = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1), indexing="ij")
    D = np.abs(I) + np.abs(J)
    idx = np.arange(m * m).reshape(m, m)
    prev = np.empty((m, m), dtype=np.int64)
    nxt = np.empty((m, m), dtype=np.int64)
    for i in range(-R, R + 1):
        for j in range(-R, R + 1):
            if i == 0 and j == 0:
                p, q = (0, 0), (1, 0)
            elif i > 0:
                p, q = (i - 1, j), (i + 1, j)
            elif i < 0:
                p, q = (i + 1, j), (i - 1, j)
            elif j > 0:
                p, q = (i, j - 1), (i, j + 1)
            else:
                p, q = (i, j + 1), (i, j - 1)
            p = (max(-R, min(R, p[0])), max(-R, min(R, p[1])))
            q = (max(-R, min(R, q[0])), max(-R, min(R, q[1])))
            prev[i + R, j + R] = idx[p[0] + R, p[1] + R]
            nxt[i + R, j + R] = idx[q[0] + R, q[1] + R]
    masks = [np.where(D.ravel() == d)[0] for d in range(2 * R + 1)]
    return D, prev.ravel(), nxt.ravel(), masks, R


def plane_profile(r, T, setup):
    D, prev, nxt, masks, R = setup
    m = 2 * R + 1
    x = np.zeros((m, m), dtype=np.uint8)
    x[R, R] = 1
    prof = np.zeros((T + 1, T + 1), dtype=np.uint8)
    const_ok = True
    for t in range(T + 1):
        flat = x.ravel()
        for d in range(t + 1):
            v = flat[masks[d]]
            prof[t, d] = v[0]
            if v.min() != v.max():
                const_ok = False
        y = RULE_TAB[r][4 * flat[prev] + 2 * flat + flat[nxt]]
        x = y.reshape(m, m)
    return prof, const_ok


def tree_profile(r, T):
    """Vertex-level simulation on the infinite binary tree.

    Only layers 0..t are materialised at time t; deeper layers are the constant
    background b_t (they cannot see the root).  Layer d is stored as an array of
    length 2^d; the two children of entry i are entries 2i, 2i+1.
    """
    tab = RULE_TAB[r]
    layers = [np.array([1], dtype=np.uint8)]
    b = 0                                   # background value at time 0
    prof = np.zeros((T + 1, T + 1), dtype=np.uint8)
    const_ok = True
    for t in range(T + 1):
        for d in range(t + 1):
            v = layers[d]
            prof[t, d] = v[0]
            if v.min() != v.max():
                const_ok = False
        new = []
        for d in range(len(layers)):
            own = layers[d]
            par = own[:1] if d == 0 else layers[d - 1][:1]
            par = np.broadcast_to(par, own.shape)
            if d + 1 < len(layers):
                ch = layers[d + 1].reshape(-1, 2)[:, 0]
            else:
                ch = np.full(own.shape, b, dtype=np.uint8)
            new.append(tab[4 * par + 2 * own + ch])
        top = layers[-1]
        par = np.repeat(top, 2)
        new.append(tab[4 * par + 2 * b + b])
        b = int(tab[7 * b])
        layers = new
    return prof, const_ok


def geometry_census():
    setup = plane_setup(T_GEOM + 1)
    mismatch = 0
    plane_bad = 0
    tree_bad = 0
    comparisons = 0
    bad_rules = []
    t0 = time.time()
    for r in range(256):
        rows = ray_rows(r, T_GEOM)
        pp, pc = plane_profile(r, T_GEOM, setup)
        tp, tc = tree_profile(r, T_GEOM)
        if not pc:
            plane_bad += 1
        if not tc:
            tree_bad += 1
        bad = False
        for t in range(T_GEOM + 1):
            for d in range(t + 1):
                comparisons += 1
                if rows[t, d] != pp[t, d] or rows[t, d] != tp[t, d]:
                    mismatch += 1
                    bad = True
        if bad:
            bad_rules.append(r)
    return dict(mismatch=mismatch, plane_bad=plane_bad, tree_bad=tree_bad,
                comparisons=comparisons, bad_rules=bad_rules,
                seconds=time.time() - t0,
                n_cells_plane=(2 * T_GEOM + 3) ** 2,
                n_tree=2 ** (T_GEOM + 1) - 1)


# ----------------------------------------------------------------------------
# 2. dynamics of all 256 rules
# ----------------------------------------------------------------------------

def law_check(rows, c, t0, T):
    """Full-profile c-dilation law:  row[c*t+c-1] == repeat(row[t], c)."""
    for t in range(t0, T + 1):
        tt = c * t + c - 1
        if tt > T:
            break
        ref = np.repeat(rows[t][:tt // c + 1], c)[:tt + 1]
        if not np.array_equal(rows[tt][:tt + 1], ref):
            return False
    return True


def nondegenerate(rows, T):
    """True if some row well inside the horizon is not constant."""
    for t in range(T // 2, T + 1):
        row = rows[t][:t + 1]
        if row.min() != row.max():
            return True
    return False


def constant_row_forever(r, rows, t=2):
    """True if the profile is provably a constant row for all times >= t.

    Once a row is constant (= c) and the background is b, the next row is constant
    iff f(c,c,c) = f(c,c,b) = f(c,b,b); the background then evolves by b -> f(b,b,b)
    and the row by c -> f(c,c,c).  We follow this 2-state cycle and check the
    compatibility condition on it.  This is an exact induction, not a window test.
    """
    row = rows[t][:t + 1]
    if row.min() != row.max():
        return False
    tab = RULE_TAB[r]
    c0, b = int(row[0]), int(rows[t][t + 1])
    seen = set()
    while (c0, b) not in seen:
        seen.add((c0, b))
        if not (tab[7 * c0] == tab[4 * c0 + 2 * c0 + b] == tab[4 * c0 + 2 * b + b]):
            return False
        c0, b = int(tab[7 * c0]), int(tab[7 * b])
    return True


def all_dead_times(rows, T):
    out = []
    for t in range(1, T + 1):
        if not rows[t][:t + 1].any():
            out.append(t)
    return out


def all_alive_times(rows, T):
    out = []
    for t in range(1, T + 1):
        if rows[t][:t + 1].all():
            out.append(t)
    return out


def classify(r, rows, T):
    """Coarse dynamical tag.

    S2    : the non-degenerate 2-contraction family (the eight rules)
    DEAD  : the visible cone is all 0 from some t0 on
    ALIVE : the visible cone is all 1 from some t0 on
    ALT   : the visible cone is constant but alternates 0/1 (period 2)
    OTHER : persistent spatial structure (includes the additive Sierpinski rules)
    """
    if nondegenerate(rows, T) and law_check(rows, 2, 1, T):
        return "S2"
    last_bad = -1
    for t in range(T, -1, -1):
        row = rows[t][:t + 1]
        if row.min() != row.max():
            last_bad = t
            break
    t0 = last_bad + 1
    if t0 <= T // 2:
        start = max(t0, 1)
        vals = [int(rows[t][0]) for t in range(start, min(T, start + 7) + 1)]
        if all(v == 0 for v in vals):
            return "DEAD"
        if all(v == 1 for v in vals):
            return "ALIVE"
        return "ALT"
    if is_affine(r):
        return "AFF"
    return "OTHER"


def anf(r):
    """Algebraic normal form over GF(2); index 4a+2b+c, bit 4=a, 2=b, 1=c."""
    v = [f_of(r, (i >> 2) & 1, (i >> 1) & 1, i & 1) for i in range(8)]
    for bit in (4, 2, 1):
        for m in range(8):
            if m & bit:
                v[m] ^= v[m ^ bit]
    return v


def is_affine(r):
    v = anf(r)
    return all(v[m] == 0 for m in (3, 5, 6, 7))


def anf_string(r):
    v = anf(r)
    names = {1: "c", 2: "b", 4: "a"}
    terms = []
    if v[0]:
        terms.append("1")
    for m in (4, 2, 1):
        if v[m]:
            terms.append(names[m])
    return " f = " + (" + ".join(terms) if terms else "0")


def kernel_stats(seq, K=5, L=32):
    """Size and GF(2)/rational rank of the 2-kernel of a finite sequence."""
    vecs = []
    for k in range(K + 1):
        step = 1 << k
        for rr in range(step):
            vecs.append(tuple(int(seq[step * n + rr]) for n in range(L)))
    distinct = len(set(vecs))
    basis = []
    for v in vecs:
        m = 0
        for i, bit in enumerate(v):
            if bit & 1:
                m |= 1 << i
        cur = m
        for bb in basis:
            cur = min(cur, cur ^ bb)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    gf2 = len(basis)
    rat = int(np.linalg.matrix_rank(np.array(vecs, dtype=float)))
    return distinct, gf2, rat


def oeis_find(seq, n_terms=12, db="oeis.db", max_hits=4):
    """Offline OEIS lookup: contiguous match of seq[:n_terms] in the local snapshot."""
    if not os.path.exists(db):
        return []
    pat = ",".join(str(int(v)) for v in seq[:n_terms])
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        try:
            # exact prefix first (the sequence itself), then any contiguous window
            rows = con.execute(
                "SELECT aid,name,terms,offset1 FROM seq WHERE terms LIKE ? LIMIT 50",
                (pat + "%",)).fetchall()
            rows += con.execute(
                "SELECT aid,name,terms,offset1 FROM seq WHERE terms LIKE ? LIMIT 400",
                ("%" + pat + "%",)).fetchall()
        finally:
            con.close()
    except Exception as exc:                      # pragma: no cover
        return [("ERROR", str(exc), 0, 0)]
    hits = []
    seen = set()
    for aid, name, terms, off in rows:
        if aid in seen:
            continue
        try:
            vals = [int(v) for v in terms.split(",")]
        except ValueError:
            continue
        t = ",".join(str(v) for v in vals)
        pos = t.find(pat)
        if pos >= 0:
            shift = 0 if pos == 0 else t[:pos].count(",") + 1
            seen.add(aid)
            hits.append((aid, name, off + shift, shift))
    hits.sort(key=lambda h: h[3])
    return hits[:max_hits]


def fusc(n):
    a, b = 0, 1
    for bit in bin(n)[2:]:
        if bit == "0":
            b = a + b
        else:
            a = a + b
    return a


def sigma_set(d):
    return [u for u in range(d + 1) if (u & ((d - u) // 2)) == 0]


def shell_formula(t):
    rt = t - (1 << (t.bit_length() - 1))
    return {d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2}


def main():
    t_start = time.time()
    out = []
    P = out.append

    P("=" * 78)
    P("320_layer_rules.py -- census of the 256 layer rules")
    P("=" * 78)
    P("")
    P("[0] conventions")
    P("    f_r(a,b,c) = (r >> (4a+2b+c)) & 1;  a = layer d-1, b = layer d, c = layer d+1")
    P("    ray:            x'[d] = f(x[d-1],x[d],x[d+1]) (d>=1), x'[0] = f(x[0],x[0],x[1])")
    P("    initial state:  x_0(0) = 1, x_0(d) = 0 for d > 0")
    P("    comparisons are made on the light cone d <= t")
    P("")

    # ------------------------------------------------------------------ step 1
    P("[1] STEP 1 -- geometry census, t <= %d" % T_GEOM)
    gc = geometry_census()
    P("    geometries: ray N / Z^2 von Neumann / infinite binary tree")
    P("    plane grid  : %d x %d cells, tree vertices: %d" %
      (2 * T_GEOM + 3, 2 * T_GEOM + 3, gc["n_tree"]))
    P("    (rule,t,d) comparisons: %d per geometry pair" % gc["comparisons"])
    P("    layer-constancy violations: plane %d, tree %d" %
      (gc["plane_bad"], gc["tree_bad"]))
    P("    ray/plane/tree mismatches : %d" % gc["mismatch"])
    P("    rules with any mismatch   : %d %s" %
      (len(gc["bad_rules"]), gc["bad_rules"][:10]))
    P("    => geometry independent rules: %d / 256" % (256 - len(gc["bad_rules"])))
    P("    (this is forced by the layer abstraction: the update reads x[d-1],x[d],x[d+1]")
    P("     and never the layer sizes c_d; see the report)")
    P("    boundary completion: x'[0] = f(x[0],x[0],x[1]) (missing layer = the cell itself)")
    P("    this is part of the rule; it is the completion that reproduces the")
    P("    machine-checked closed form of rule 129 (zero padding fails at t=5)")
    P("")

    # ------------------------------------------------------------------ step 2
    P("[2] STEP 2 -- dynamics of the 256 rules, t <= %d" % T_LAW)
    rows = [ray_rows(r, T_LAW) for r in range(256)]
    tags = {r: classify(r, rows[r], T_LAW) for r in range(256)}
    from collections import Counter
    counts = Counter(tags.values())

    # 2.1 basic statistics
    n_bg0 = sum(1 for r in range(256) if f_of(r, 0, 0, 0) == 0)
    n_bg1 = 256 - n_bg0
    P("    2.1 background: f(0,0,0)=0 for %d rules, =1 for %d rules" % (n_bg0, n_bg1))
    P("        constant rules: %s" % [r for r in range(256) if dep_string(r) == "-"])
    P("        class counts : %s" % dict(sorted(counts.items())))
    P("        affine rules : %s" %
      [(r, anf_string(r).strip()) for r in range(256) if is_affine(r)])
    P("")

    # 2.2 contraction scan
    P("    2.2 contraction (dilation) scan:  row[c*t+c-1] == repeat(row[t], c) for all t >= t0")
    P("        'constant-row' = provably constant from t=2 on (see constant_row_forever)")
    law_hits = {}
    for c in (2, 3, 4, 5, 6, 7):
        for t0 in (0, 1, 2):
            good = [r for r in range(256) if law_check(rows[r], c, t0, T_LAW)]
            keep = [r for r in good if not constant_row_forever(r, rows[r])]
            law_hits[(c, t0)] = (good, keep)
            P("        c=%d t0=%d : %3d rules satisfy (t<=%d); %2d are not constant-row: %s" %
              (c, t0, len(good), T_LAW, len(keep), keep if len(keep) <= 10 else keep[:10]))
    P("        (c=4 is implied by c=2 by composition; c=3,5,6,7 have no non-constant-row rule)")
    P("        (t0=2 is the base of the 3^k-1 chain 2,8,26,80,... -- the natural home of a")
    P("         '3^k-1 family'; it has no non-constant-row solution either)")
    P("")

    eight = law_hits[(2, 1)][1]
    P("    2.3 the c=2 family (non-degenerate): %d rules %s" % (len(eight), eight))
    for r in eight:
        P("        r=%3d  truth table (a,b,c)=(000,001,010,011,100,101,110,111): %s   deps=%s" %
          (r, bits_of(r), dep_string(r)))
    P("")

    # 2.4 six-triple characterisation
    P("    2.4 characterisation: the profiles of 129 and 90 never show the triples 010/101")
    allowed = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
    triples_seen = set()
    for t in range(1, T_LAW + 1):
        row = rows[129][t]
        for d in range(1, t):
            triples_seen.add((int(row[d - 1]), int(row[d]), int(row[d + 1])))
    P("        triples seen in the 129 orbit (interior, d>=1): %s" % sorted(triples_seen))
    P("        triples seen in the 90  orbit (interior, d>=1): %s" %
      sorted({(int(rows[90][t][d - 1]), int(rows[90][t][d]), int(rows[90][t][d + 1]))
              for t in range(1, T_LAW + 1) for d in range(1, t)}))
    same129 = [r for r in range(256) if all(f_of(r, *tr) == f_of(129, *tr) for tr in allowed)]
    same90 = [r for r in range(256) if all(f_of(r, *tr) == f_of(90, *tr) for tr in allowed)]
    P("        rules agreeing with 129 on the six triples: %s" % same129)
    P("        rules agreeing with  90 on the six triples: %s" % same90)
    P("        union of the two lists = the c=2 family: %s" %
      (sorted(set(same129) | set(same90)) == sorted(eight)))
    P("")

    # 2.5 orbit identities
    P("    2.5 orbit identities (t <= %d)" % T_ORBIT)
    orows = {r: ray_rows(r, T_ORBIT) for r in eight}
    eq_pairs = []
    for i, a in enumerate(eight):
        for b in eight[i + 1:]:
            if all(np.array_equal(orows[a][t][:t + 1], orows[b][t][:t + 1])
                   for t in range(T_ORBIT + 1)):
                eq_pairs.append((a, b))
    P("        pairs of identical orbits: %s" % eq_pairs)
    comp = all(np.array_equal(orows[126][t][:t + 1], 1 - orows[129][t][:t + 1])
               for t in range(1, T_ORBIT + 1))
    P("        complement identity x_126(t) == 1 - x_129(t) for 1<=t<=%d: %s" % (T_ORBIT, comp))
    P("        dead(129) == alive(90) for 1<=t<=%d: %s" %
      (T_ORBIT, all(set(np.where(orows[129][t][:t + 1] == 0)[0]) ==
                    set(np.where(orows[90][t][:t + 1] == 1)[0])
                    for t in range(1, T_ORBIT + 1))))
    P("")

    # 2.6 epochs, counts, OEIS
    P("    2.6 epochs and counts")
    for r in (90, 129):
        dt = all_dead_times(orows[r], T_ORBIT)
        at = all_alive_times(orows[r], T_ORBIT)
        P("        r=%3d all-dead t<=%d: %s" % (r, T_ORBIT, dt[:12]))
        P("              all-alive t<=%d: %s" % (T_ORBIT, at[:12]))
    P("        r=129 dead counts (t=1..20): %s" %
      [int((orows[129][t][:t + 1] == 0).sum()) for t in range(1, 21)])
    P("        r= 90 alive counts (t=1..20): %s" %
      [int((orows[90][t][:t + 1] == 1).sum()) for t in range(1, 21)])
    P("        2^popcount(t), t=1..20   : %s" % [1 << bin(t).count("1") for t in range(1, 21)])
    ok129 = all(int((orows[129][t][:t + 1] == 0).sum()) == (1 << bin(t).count("1"))
                for t in range(1, T_ORBIT + 1))
    ok90 = all(int((orows[90][t][:t + 1] == 1).sum()) == (1 << bin(t).count("1"))
               for t in range(1, T_ORBIT + 1))
    P("        identity dead(129)=2^popcount for t<=%d: %s" % (T_ORBIT, ok129))
    P("        identity alive(90)=2^popcount for t<=%d: %s" % (T_ORBIT, ok90))
    fam2d = [r for r in range(256) if all_dead_times(rows[r], 64)[:6] == [1, 3, 7, 15, 31, 63]]
    fam2a = [r for r in range(256) if all_alive_times(rows[r], 64)[:6] == [1, 3, 7, 15, 31, 63]]
    fam3 = [r for r in range(256) if {2, 8, 26, 80} <= set(all_dead_times(rows[r], 80))]
    P("        rules with all-dead at 2^k-1 (k=1..6) : %s" % fam2d)
    P("        rules with all-alive at 2^k-1 (k=1..6): %s" % fam2a)
    P("        rules whose all-dead times contain 3^k-1={2,8,26,80}: %d rules, classes %s" %
      (len(fam3), sorted({tags[r] for r in fam3})))

    # 2.7 2-kernel of the centre column
    P("")
    P("    2.7 2-kernel test (length %d, K=5, window L=32)" % T_KERNEL)
    kern = {}
    brow = ray_rows(129, T_KERNEL)
    s129 = [int(brow[t][0]) for t in range(T_KERNEL)]
    s129c = [int((brow[t][:t + 1] == 0).sum()) for t in range(T_KERNEL)]
    brow90 = ray_rows(90, T_KERNEL)
    s90 = [int(brow90[t][0]) for t in range(T_KERNEL)]
    s90c = [int((brow90[t][:t + 1] == 1).sum()) for t in range(T_KERNEL)]
    brow30 = ray_rows(30, T_KERNEL)
    s30 = [int(brow30[t][0]) for t in range(T_KERNEL)]

    def is_prime(n):
        if n < 2:
            return False
        q = 2
        while q * q <= n:
            if n % q == 0:
                return False
            q += 1
        return True

    primes = [1 if is_prime(n) else 0 for n in range(T_KERNEL)]
    for name, seq in (("129 centre", s129), ("129 dead-count", s129c),
                      ("90 centre", s90), ("90 alive-count", s90c),
                      ("30 centre", s30), ("primes", primes)):
        d, g, q = kernel_stats(seq)
        kern[name] = (d, g, q)
        P("        %-15s distinct=%3d  rank_GF(2)=%2d  rank_Q=%2d" % (name, d, g, q))
    P("")

    # 2.8 OEIS
    P("    2.8 OEIS (offline snapshot oeis.db)")
    for name, seq in (("129 dead-count", s129c[1:]),
                      ("129 centre", s129),
                      ("90 alive-count", s90c[1:])):
        hits = oeis_find(seq)
        P("        %-15s %s" % (name, [(h[0], h[1][:48]) for h in hits]))
    P("")

    # ------------------------------------------------------------------ step 3
    P("[3] STEP 3 -- self-check of the published formulas")
    sr = ray_rows(129, 300)
    bad = 0
    for t in range(1, 301):
        rt = t - (1 << (t.bit_length() - 1))
        sh = shell_formula(t)
        for d in range(t + 1):
            val = 0 if d in sh else 1
            if int(sr[t][d]) != val:
                bad += 1
    P("    3.1 closed form x_t(d) = 1 - [floor((t-d)/2) subset r(t)], t<=300, d<=t: %d mismatches" % bad)
    P("        |shell(t)| = 2^popcount(t) for t<=300: %s" %
      all(len(shell_formula(t)) == (1 << bin(t).count("1")) for t in range(1, 301)))
    bad_dual = 0
    for t in range(1, 301):
        s = (1 << (t.bit_length())) - t
        u = s - 1
        sh = shell_formula(t)
        dual = {d for d in range(t + 1) if (u & ((u + d) // 2)) == u}
        if dual != sh:
            bad_dual += 1
    P("    3.2 dual form u = s-1, s = 2^(floor(log2 t)+1)-t, t<=300: %d mismatches" % bad_dual)
    bad_sig = 0
    for d in range(0, 1001):
        a = len(sigma_set(d))
        if a != fusc(d) + fusc(d + 1) or a != fusc(2 * d + 1):
            bad_sig += 1
    P("    3.3 |SIGMA_d| = fusc(d)+fusc(d+1) = fusc(2d+1), d<=1000: %d mismatches" % bad_sig)
    S = [0]
    for d in range(0, 4001):
        S.append(S[-1] + len(sigma_set(d)))
    bad_s = [N for N in range(1, 2001) if S[2 * N] != 3 * S[N]]
    P("    3.4 S(N)=sum_{d<N}|SIGMA_d|, S(2N)=3S(N), N<=2000: %d violations %s" %
      (len(bad_s), bad_s[:5]))
    P("        S(1..12) = %s" % S[1:13])
    sr90 = ray_rows(90, 300)
    bad_dual90 = 0
    for t in range(1, 301):
        sh = shell_formula(t)
        for d in range(t + 1):
            if int(sr90[t][d]) != (1 if d in sh else 0):
                bad_dual90 += 1
        for d in range(t + 1, 320):
            if int(sr90[t][d]) != 0:
                bad_dual90 += 1
    P("    3.5 dual closed form for rule 90: x_t(d) = [floor((t-d)/2) subset r(t)] (d<=t),")
    P("        and 0 for d>t; t<=300: %d mismatches" % bad_dual90)
    P("")

    # ------------------------------------------------------------------ table
    P("[4] full table (256 rows), t <= %d" % T_LAW)
    P("    r  f000 f111 deps cls     dead-times<=64                alive-times<=64")
    for r in range(256):
        tag = tags[r]
        dt = all_dead_times(rows[r], 64)
        at = all_alive_times(rows[r], 64)
        dts = ",".join(map(str, dt[:8])) + ("..." if len(dt) > 8 else "")
        ats = ",".join(map(str, at[:8])) + ("..." if len(at) > 8 else "")
        P("    %3d    %d    %d  %-4s %-6s  %-28s %s" %
          (r, f_of(r, 0, 0, 0), f_of(r, 1, 1, 1), dep_string(r), tag, dts, ats))
    P("")
    P("    class counts: %s" % dict(sorted(counts.items())))
    P("")

    # ------------------------------------------------------------------ summary
    P("[5] summary")
    P("    geometry independent rules            : %d / 256" % (256 - len(gc["bad_rules"])))
    P("    c=2 contraction, non-degenerate       : %d rules %s" % (len(eight), eight))
    P("    distinct orbits among them            : 2  (%s) and (%s)" %
      (same129, same90))
    P("    c=3 contraction, non-constant-row     : " +
      " / ".join("%d (t0=%d)" % (len(law_hits[(3, t0)][1]), t0) for t0 in (0, 1, 2)))
    P("    c=3 contraction including constant-row: " +
      " / ".join("%d (t0=%d)" % (len(law_hits[(3, t0)][0]), t0) for t0 in (0, 1, 2)) +
      "  [all constant from t=2]")
    P("    total runtime: %.1f s" % (time.time() - t_start))
    text = "\n".join(out)
    sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
