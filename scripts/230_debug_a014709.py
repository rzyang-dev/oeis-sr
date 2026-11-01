import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
rec = atlas["A014709"]
print("shift:", rec["shift"], "states:", rec["states"])
print("out:", rec["out"])
def dfa_terms(rec, N=16):
    tr, ov = rec["trans"], rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
t = dfa_terms(rec, 16)
print("dfa terms:", t)
# relation 1 + f + x f == 0 ?
lhs = [1 ^ t[0]] + [t[i] ^ t[i-1] if i >= 1 else 0 for i in range(1, 12)]
print("(1+f+xf) coeffs 0..11:", lhs)
