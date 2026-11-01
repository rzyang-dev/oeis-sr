"""Exact sequence solvers used by the baselines."""
from __future__ import annotations

from fractions import Fraction


def poly_predict(vals, k, maxdeg=12):
    cols = [list(vals)]
    for deg in range(1, maxdeg + 1):
        prev = cols[-1]
        if len(prev) < 2:
            return None
        cols.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
        row = cols[-1]
        if len(row) >= 2 and len(set(row)) == 1:
            out = []
            for _ in range(k):
                cols[-1].append(cols[-1][-1])
                for j in range(len(cols) - 2, -1, -1):
                    cols[j].append(cols[j][-1] + cols[j + 1][-1])
                out.append(cols[0][-1])
            return out
    return None


def berlekamp_massey(s):
    C = [Fraction(1)]
    B = [Fraction(1)]
    L = 0
    m = 1
    b = Fraction(1)
    for n in range(len(s)):
        d = sum(C[i] * s[n - i] for i in range(min(L, n) + 1))
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d / b
        if len(C) < len(B) + m:
            C += [Fraction(0)] * (len(B) + m - len(C))
        for j, bj in enumerate(B):
            C[j + m] -= coef * bj
        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1
    return C, L


def bm_predict(vals, k, maxorder=12):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L + 1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        out.append(-sum(C[i] * out[n - i] for i in range(1, L + 1)) / C[0])
    return out[-k:]


def null_vector(rows, ncols):
    m = [row[:] for row in rows]
    pivot_cols = []
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(m)):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        pv = m[r][c]
        m[r] = [x / pv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r])]
        pivot_cols.append(c)
        r += 1
        if r == len(m):
            break
    free = [c for c in range(ncols) if c not in pivot_cols]
    if not free:
        return None
    fc = free[-1]
    sol = [Fraction(0)] * ncols
    sol[fc] = Fraction(1)
    for i, c in enumerate(pivot_cols):
        sol[c] = -m[i][fc]
    return sol


def precursive_guess(vals, r, d):
    ncols = (r + 1) * (d + 1)
    nrows = len(vals) - r
    if nrows < ncols + 3:
        return None
    rows = []
    for n in range(r, len(vals)):
        row = []
        for i in range(r + 1):
            a = Fraction(vals[n - i])
            for j in range(d + 1):
                row.append(a * (n ** j))
        rows.append(row)
    return null_vector(rows, ncols)


def precursive_predict(vals, coef, r, d, k):
    out = list(vals)
    for n in range(len(vals), len(vals) + k):
        s = Fraction(0)
        p0 = Fraction(0)
        for i in range(r + 1):
            p = sum(coef[i * (d + 1) + j] * (n ** j) for j in range(d + 1))
            if i == 0:
                p0 = p
            else:
                s += p * out[n - i]
        if p0 == 0:
            return None
        v = -s / p0
        out.append(v.numerator if v.denominator == 1 else v)
    return out[-k:]


def solve(vals, k):
    """Try polynomial, then linear recurrence, then P-recursive."""
    pred = poly_predict(vals, k)
    if pred is not None:
        return pred, "poly"
    pred = bm_predict(vals, k)
    if pred is not None:
        return pred, "bm"
    for r, d in ((1, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3)):
        coef = precursive_guess(vals, r, d)
        if coef is None:
            continue
        pred = precursive_predict(vals, coef, r, d, k)
        if pred is not None:
            return pred, f"pre({r},{d})"
    return None, None

def solve_validated(vals, k, hold=5):
    """Solve only if the method also reproduces a held-out tail of known terms."""
    if len(vals) <= hold + 10:
        return None, None
    pred, _ = solve(vals[:-hold], hold)
    if pred is None or list(pred) != list(vals[-hold:]):
        return None, None
    return solve(vals, k)
