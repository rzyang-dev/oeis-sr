"""Script 286 -- the fourth submask moment and the invariant tower.

For a submask m = sum_{i in bits r} eps_i 2^i with independent fair eps_i,
the moments of m are moments of W = sum eps_i 2^i.  With
    mu = r/2,  c2 = Q/4,  c4 = -P16/8   (P_j = sum_{i in bits r} 2^(j i))
the cumulant expansion gives

    E[W^2] = mu^2 + c2                        ->  P_2 = r^2 + Q
    E[W^3] = mu^3 + 3 mu c2                   ->  P_3 = r^3 + 3 Q r
    E[W^4] = mu^4 + 6 mu^2 c2 + 3 c2^2 + c4   ->  P_4 = r^4 + 6 Q r^2 + 3 Q^2 - 2 P16

so the fourth moment is the FIRST one that needs an invariant beyond r and Q.
"""
def bits(r):
    return [i for i in range(r.bit_length()) if (r >> i) & 1]

def subm(r):
    out = [0]
    for i in bits(r):
        out = out + [x + (1 << i) for x in out]
    return out

def Q(r):
    return sum(4 ** i for i in bits(r))

def Pj(r, j):
    return sum(2 ** (j * i) for i in bits(r))

bad = 0
for r in range(0, 301):
    N = len(subm(r))
    for j in [1, 2, 3, 4, 5, 6]:
        S = sum(m ** j for m in subm(r))
        # predicted numerator  N * poly / 2^j
        if j == 1:
            pred_num = r
        elif j == 2:
            pred_num = r ** 2 + Q(r)
        elif j == 3:
            pred_num = r ** 3 + 3 * Q(r) * r
        elif j == 4:
            pred_num = r ** 4 + 6 * Q(r) * r ** 2 + 3 * Q(r) ** 2 - 2 * Pj(r, 4)
        elif j == 5:
            # cumulant: mu^5 + 10 mu^3 c2 + 15 mu c2^2 + 5 mu c4
            num = (r ** 5 + 10 * Q(r) * r ** 3 + 15 * Q(r) ** 2 * r - 10 * Pj(r, 4) * r)
            pred_num = num
        else:
            # E[W^6] = mu^6 + 15 mu^4 c2 + 45 mu^2 c2^2 + 15 c2^3 + 15 mu^2 c4 + 15 c2 c4 + c6
            # c6 = sum 16 x^6/45 ... = P64 * 16/45? use: log cosh x = x^2/2 - x^4/12 + x^6/45
            # c6 = 720 * (2^(i-1))^6/45 = P64 / 4
            num = (r ** 6 + 15 * Q(r) * r ** 4 + 45 * Q(r) ** 2 * r ** 2 + 15 * Q(r) ** 3
                   - 30 * Pj(r, 4) * r ** 2 - 30 * Pj(r, 4) * Q(r) + 16 * Pj(r, 6))
            pred_num = num
        if j != 6:
            lhs = S * (2 ** j)
        else:
            lhs = S * (2 ** 6)
        if lhs != N * pred_num:
            print(f"MOMENT FAIL j={j} r={r}: {lhs} vs {N*pred_num}")
            bad += 1
            break
    if bad:
        break
print(f"[1] submask moments j=1..6, r<=300: {'OK' if bad==0 else 'FAILURES'}")

# ---- is P16 needed for j = 4?  (no polynomial in (r,Q) of degree <= 6 fits) --
# A clean witness: the pairs (r, Q) with r <= 20 and their P16.
rows = {(r, Q(r)): Pj(r, 4) for r in range(1, 21)}
print("[2] (r,Q) -> P16 for r<=20:", rows)
print("    distinct Q values:", len({q for (_, q) in rows}), "of", len(rows), "r")
