import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
B = m["A039982"]
print("out:", B["out"])
print("trans:", B["trans"])
def fold(s, n):
    while n:
        s = B["trans"][s][n % 2]; n //= 2
    return s
def w39(n):
    if n == 0: return 1
    if n % 2 == 1: return 1
    return 1 - w39(n // 2 - 1)
print("w39:", [w39(n) for n in range(16)])
for s in range(7):
    vals = [B["out"][fold(s, n)] for n in range(16)]
    print(f"state {s}: {vals}")
print("w39 shifted:", [1 - w39(n) for n in range(16)])
