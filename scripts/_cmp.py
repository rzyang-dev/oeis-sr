import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
def val(dfa, n):
    s = 0
    for ch in reversed(bin(n)[2:]):
        s = dfa["trans"][s][int(ch)]
        if s < 0: return None
    return dfa["out"][s]
A, B = m["A267442"], m["A043545"]
mism = [(n, val(A,n), val(B,n)) for n in range(0, 5000) if val(A,n) != val(B,n)]
print("mismatches:", len(mism), " first:", mism[:8])
print("A states:", A["states"], "out:", A["out"])
print("B states:", B["states"], "out:", B["out"])
