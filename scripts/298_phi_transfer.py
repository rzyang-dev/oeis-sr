"""Script 298 -- the arm-moment transfer matrices, verified.

Arm.lean proves (for every k):

    Phi_k(2u)   = 2^k * Phi_k(u)
    Phi_k(2u+1) = sum_{i <= k, i = k mod 2} C(k,i) * 2^(i+1) * Phi_i(u)

with  Phi_k(t) = sum_{m submask of r t} (t - 2m)^k .

This script checks both against the definition for k <= 8, u <= 400, and
prints the two transfer matrices.
"""
from math import comb

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def subm(m):
    out = [0]
    for i in range(m.bit_length()):
        if (m >> i) & 1:
            out = out + [x + (1 << i) for x in out]
    return out

def Phi(k, t):
    return sum((t - 2 * m) ** k for m in subm(r(t)))

KMAX = 8
UMAX = 400

bad = 0
for k in range(KMAX + 1):
    for u in range(1, UMAX + 1):
        if Phi(k, 2 * u) != (2 ** k) * Phi(k, u):
            print(f"EVEN FAIL k={k} u={u}")
            bad += 1
            break
        pred = sum(comb(k, i) * 2 ** (i + 1) * Phi(i, u) for i in range(k + 1) if i % 2 == k % 2)
        if Phi(k, 2 * u + 1) != pred:
            print(f"ODD FAIL k={k} u={u}: {Phi(k, 2*u+1)} vs {pred}")
            bad += 1
            break
print(f"[1] both transfer laws, k <= {KMAX}, u <= {UMAX}: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

print()
print("[2] the odd transfer matrix M[k][i] = 2^(i+1) C(k,i) [i = k mod 2], k <= 6:")
for k in range(7):
    print(f"   k={k}: " + str([2 ** (i + 1) * comb(k, i) if i % 2 == k % 2 else 0 for i in range(7)]))
print("[3] the even transfer is diag(2^k):", [2 ** k for k in range(7)])

print()
print("[4] a sanity check against the closed forms of the shell moments:")
print("    Phi_0(t) = #subm(r t) =", [Phi(0, t) for t in range(1, 8)],
      "vs 2^wt:", [2 ** bin(t).count('1') for t in range(1, 8)])
print("    Phi_1(t) =", [Phi(1, t) for t in range(1, 8)])

print()
print("[5] iteration: applying the matrices along the binary digits of t")
print("    reproduces Phi_k(t) from Phi_k(1) = 0 / Phi_0(1) = 1.")

def transfer(vec, bit):
    """vec[i] = Phi_i(u); return the Phi_i(2u+bit)"""
    deg = len(vec) - 1
    out = [0] * (deg + 1)
    for k in range(deg + 1):
        if bit == 0:
            out[k] = (2 ** k) * vec[k]
        else:
            out[k] = sum(comb(k, i) * 2 ** (i + 1) * vec[i] for i in range(k + 1) if i % 2 == k % 2)
    return out

DEG = 4
bad = 0
for t in range(1, 300):
    digits = bin(t)[3:]           # drop the leading 1
    vec = [Phi(i, 1) for i in range(DEG + 1)]
    for ch in digits:
        vec = transfer(vec, int(ch))
    if vec != [Phi(i, t) for i in range(DEG + 1)]:
        print("ITERATION FAIL", t, vec, [Phi(i, t) for i in range(DEG + 1)])
        bad += 1
        break
print(f"    t < 300, degrees <= {DEG}: {'OK' if bad == 0 else 'FAIL'}")
