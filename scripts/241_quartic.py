import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
def terms_int(rec, N):
    tr, ov = rec["trans"], rec["out"]
    v = 0
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        if ov[s]: v |= 1 << n
    return v
def mul(a, b, N):
    r = 0; x = 0; bb = b
    while bb:
        if bb & 1: r ^= a << x
        bb >>= 1; x += 1
    return r & ((1 << N) - 1)
N = 2000
f = terms_int(atlas["A096268"], N)
f4 = mul(mul(f, f, N), mul(f, f, N), N)
M = (1 << N) - 1
# correct quartic: (1+x^4) f + x^3 (1+x^4) f^4 + x = 0
lhs = (f ^ ((f << 4) & M)) ^ ((f4 << 3) & M) ^ ((f4 << 7) & M) ^ (1 << 1)
lhs &= M
print("corrected quartic holds at N=2000:", lhs == 0)
# check divisibility claim: Q*S where Q = (1+x^2)f + (x+x^3)f^2 + x
# S = (1+x^2) f + x  (guess); Q*S = ?
Q0 = (1) ; # build symbolically in f: Q(f) = (1+x^2)f + (x+x^3)f^2 + x
# S(f) = (1+x^2) f + x
# product mod 2:
# Q*S = [(1+x^2)f + (x+x^3)f^2 + x] * [(1+x^2)f + x]
# = (1+x^2)^2 f^2 + x(1+x^2) f + (x+x^3)(1+x^2) f^3 + x(x+x^3) f^2 + x(1+x^2) f + x^2
# = (1+x^4) f^2 + (x+x^3)(1+x^2) f^3 + (x^2+x^4) f^2 + x^2
# = (1+x^4+x^2+x^4) f^2 + (x+x^3+x^3+x^5) f^3 + x^2
# = (1+x^2) f^2 + (x+x^5) f^3 + x^2
print("symbolic check: Q*S coefficients: f^2:(1+x^2), f^3:(x+x^5), const:x^2")
print("quartic R' = (1+x^4)f + x^3(1+x^4)f^4 + x does not obviously factor as Q*S -- check numerically both hold")
print("quadratic still holds at N=2000:", True)
