import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
def dfa_terms(rec, N=18, shift=0):
    tr, ov = rec["trans"], rec["out"]; out = []
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        out.append(ov[s])
    return out
for aid in ("A209229", "A255738", "A268411", "A267442"):
    rec = atlas[aid]
    print(aid, "shift field:", rec["shift"])
    print("   dfa :", dfa_terms(rec))
    print("   out :", rec["out"])
