import sys, itertools
sys.stdout.reconfigure(encoding="utf-8")
# minimal polynomial arithmetic over GF(2), exponents: (x, f0, f1, ..., f_{k-1})
def p_add(a, b):
    r = dict(a)
    for e, c in b.items():
        if e in r: r[e] ^= c
        else: r[e] = c
        if r[e] == 0: del r[e]
    return r
def p_mul_mono(a, mono):
    r = {}
    for e, c in a.items():
        ne = tuple(x+y for x, y in zip(e, mono))
        r[ne] = r.get(ne, 0) ^ c
    return {e: c for e, c in r.items() if c}
def p_mul(a, b):
    r = {}
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            ne = tuple(x+y for x, y in zip(e1, e2))
            r[ne] = r.get(ne, 0) ^ (c1 & c2)
    return {e: c for e, c in r.items() if c}
def lead(a, order):
    return max(a, key=order)
def reduce_poly(p, basis, order):
    p = dict(p)
    changed = True
    while changed and p:
        changed = False
        for g in basis:
            if not g: continue
            lg = lead(g, order); lp = lead(p, order)
            if all(lp[i] >= lg[i] for i in range(len(lp))):
                m = tuple(lp[i]-lg[i] for i in range(len(lp)))
                p = p_add(p, p_mul_mono(g, m))
                changed = True
                break
    return p
def buchberger(gens, order, max_iters=400):
    basis = [g for g in gens if g]
    pairs = [(i, j) for i in range(len(basis)) for j in range(i+1, len(basis))]
    it = 0
    while pairs and it < max_iters:
        it += 1
        i, j = pairs.pop(0)
        gi, gj = basis[i], basis[j]
        li, lj = lead(gi, order), lead(gj, order)
        m = tuple(max(a, b) for a, b in zip(li, lj))
        si = p_mul_mono(gi, tuple(m[k]-li[k] for k in range(len(m))))
        sj = p_mul_mono(gj, tuple(m[k]-lj[k] for k in range(len(m))))
        s = p_add(si, sj)
        r = reduce_poly(s, basis, order)
        if r:
            basis.append(r)
            for k in range(len(basis)-1):
                pairs.append((k, len(basis)-1))
    return basis, it
# A036987: k=3, vars (x, f0, f1, f2); equations:
# f0 + f1^2 + x f0^2 ; f1 + f1^2 + x f2^2 ; f2 + f2^2 + x f2^2
def mono(**kw):
    return (kw.get('x',0), kw.get('f0',0), kw.get('f1',0), kw.get('f2',0))
def const():
    return {(0,0,0,0): 1}
g0 = p_add({mono(f0=1): 1}, p_add({mono(f1=2): 1}, {mono(x=1,f0=2): 1}))
g1 = p_add({mono(f1=1): 1}, p_add({mono(f1=2): 1}, {mono(x=1,f2=2): 1}))
g2 = p_add({mono(f2=1): 1}, p_add({mono(f2=2): 1}, {mono(x=1,f2=2): 1}))
# lex order with f1 > f2 > f0 > x ? we want to eliminate f1,f2 -> order f1 > f2 > f0 > x
def lex(p):
    # compare tuples in variable order (f1, f2, f0, x) -> (idx1, idx2, idx0, idxX)
    return (p[2], p[3], p[1], p[0])
basis, iters = buchberger([g0, g1, g2], lex, max_iters=200)
print("basis size:", len(basis), "iters:", iters)
for g in basis:
    print("  ", sorted(g.items()))
