"""Script 291 -- the two-step recursion for the whole counting table.

The ARM of time t is   A(t) = { t - 2m : m submask of r t }   (the shell is
A(t) union (A(t) - 1), and A(t) is contained in one parity class).

Claim (this is the new structural statement):

    A(2u)   = 2 * A(u)
    A(2u+1) = (2*A(u) + 1)  union  (2*A(u) - 1)

hence, for ANY level-size function c,

    Z(2u)   = sum_{y in A(u)} [ c(2y) + c(2y-1) ]
    Z(2u+1) = sum_{y in A(u)} [ (c(2y+1)+c(2y)) + (c(2y-1)+c(2y-2)) ]

consequently the "arm moment"  Phi_k(t) = sum_{x in A(t)} x^k  obeys

    Phi_k(2u)   = 2^k Phi_k(u)
    Phi_k(2u+1) = 2 * sum_{i = k mod 2, i <= k} C(k,i) 2^i Phi_i(u)
"""
def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def subm(m):
    out = [0]
    for i in range(m.bit_length()):
        if (m >> i) & 1:
            out = out + [x + (1 << i) for x in out]
    return sorted(out)

def arm(t):
    return sorted(t - 2 * m for m in subm(r(t)))

def shell(t):
    return sorted(set(arm(t)) | {x - 1 for x in arm(t)})

TMAX = 300

# ---- 1. the arm recursions -------------------------------------------------
bad = 0
for u in range(1, TMAX):
    if arm(2 * u) != sorted(2 * y for y in arm(u)):
        print("ARM EVEN FAIL at u =", u); bad += 1
    lhs = arm(2 * u + 1)
    rhs = sorted(set(2 * y + 1 for y in arm(u)) | set(2 * y - 1 for y in arm(u)))
    if lhs != rhs:
        print("ARM ODD FAIL at u =", u, lhs, rhs); bad += 1
    # the two halves of the odd arm are disjoint
    a = set(2 * y + 1 for y in arm(u)); b = set(2 * y - 1 for y in arm(u))
    if a & b:
        print("ARM ODD OVERLAP at u =", u, a & b); bad += 1
print(f"[1] arm recursions u < {TMAX}: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 2. the shell is arm union (arm - 1), disjoint --------------------------
bad = 0
for t in range(1, TMAX):
    A = arm(t)
    if shell(t) != sorted(set(A) | {x - 1 for x in A}):
        print("SHELL FAIL at t =", t); bad += 1
    if set(A) & {x - 1 for x in A}:
        print("SHELL OVERLAP at t =", t); bad += 1
print(f"[2] shell = arm U (arm-1) disjoint, t < {TMAX}: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 3. the count recursions for several c --------------------------------
tests = {
    "c = 1":            lambda d: 1,
    "c = d":            lambda d: d,
    "c = d^2":          lambda d: d * d,
    "c = d^3":          lambda d: d ** 3,
    "c = 2^d":          lambda d: 2 ** d,
    "c = 3^d":          lambda d: 3 ** d,
    "Z^2 vN 4d+eps":    lambda d: 1 if d == 0 else 4 * d,
    "Z^3 vN 4d^2+2":    lambda d: 1 if d == 0 else 4 * d * d + 2,
    "Z^4 Moore":        lambda d: 1 if d == 0 else 64 * d ** 3 + 16 * d,
    "Z^4 vN":           lambda d: 1 if d == 0 else 8 * d * (d * d + 2) // 3,
    "Z^5 Moore":        lambda d: 1 if d == 0 else 160 * d ** 4 + 80 * d * d + 2,
}
bad = 0
for name, c in tests.items():
    for u in range(1, TMAX):
        lhs = sum(c(d) for d in shell(2 * u))
        rhs = sum(c(2 * y) + c(2 * y - 1) for y in arm(u))
        if lhs != rhs:
            print(f"EVEN FAIL {name} u={u}: {lhs} vs {rhs}"); bad += 1; break
        lhs = sum(c(d) for d in shell(2 * u + 1))
        rhs = sum((c(2 * y + 1) + c(2 * y)) + (c(2 * y - 1) + c(2 * y - 2)) for y in arm(u))
        if lhs != rhs:
            print(f"ODD FAIL {name} u={u}: {lhs} vs {rhs}"); bad += 1; break
print(f"[3] count recursions for {len(tests)} weight functions, u < {TMAX}: "
      f"{'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 4. the arm moments and their transfer matrices -----------------------
from math import comb
def phi(k, t):
    return sum(x ** k for x in arm(t))

bad = 0
for k in range(0, 5):
    for u in range(1, TMAX):
        if phi(k, 2 * u) != (2 ** k) * phi(k, u):
            print("PHI EVEN FAIL k,u =", k, u); bad += 1; break
        pred = 2 * sum(comb(k, i) * 2 ** i * phi(i, u) for i in range(k + 1) if i % 2 == k % 2)
        if phi(k, 2 * u + 1) != pred:
            print("PHI ODD FAIL k,u =", k, u, phi(k, 2 * u + 1), pred); bad += 1; break
print(f"[4] arm moments k <= 4, u < {TMAX}: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

print()
print("[5] the odd transfer matrix (rows k = 0..4):  M[k][i] = 2 C(k,i) 2^i [i = k mod 2]")
for k in range(5):
    print("   k=%d:" % k, [2 * comb(k, i) * 2 ** i if i % 2 == k % 2 else 0 for i in range(5)])
print("[6] the even transfer is diagonal: diag(1, 2, 4, 8, 16, ...)")
