import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
rec = atlas["A096268"]
print("A096268 dfa: states", rec["states"], "trans", rec["trans"], "out", rec["out"])
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
N = 10000
f = terms_int(rec, N)
print("terms[0..24]:", [(f >> k) & 1 for k in range(24)])
# candidate: (1+x^2) f + (x+x^3) f^2 + x = 0
f2 = mul(f, f, N)
expr = f ^ ((f << 2) & ((1<<N)-1)) ^ ((f2 << 1) & ((1<<N)-1)) ^ ((f2 << 3) & ((1<<N)-1)) ^ (1 << 1)
expr &= (1 << N) - 1
print("quadratic (1+x^2)f + (x+x^3)f^2 + x holds at N=10000:", expr == 0)
# also test the hand-derived quartic: f0 = x/(1+x^2)^2 + x^3 f0^4  -- skip, check quartic simply
f4 = mul(f2, f2, N)
# (1+x^2)^2 f + x + x^3 (1+x^2)^2 f^4 = 0 ?
lhs = f ^ ((f << 2) & ((1<<N)-1)) ^ (f << 4) ^ (1 << 1) ^ ((f4 << 3) & ((1<<N)-1)) ^ ((f4 << 5) & ((1<<N)-1)) ^ ((f4 << 7) & ((1<<N)-1))
lhs &= (1 << N) - 1
print("quartic holds at N=10000:", lhs == 0)
