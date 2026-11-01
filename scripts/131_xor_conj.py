import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A, B, C = m["A217586"], m["A096268"], m["A036987"]
# a(n) = b(n-1) xor c(n-1)  <=>  A_autom(x) = B_autom(x) xor C_autom(x), x = n-1 >= 0
st = (0, 0)
seen = {st}; q = deque([st])
mismatch = None
while q:
    sb, sc = q.popleft()
    val = B["out"][sb] ^ C["out"][sc]
    if A["out"][sb] != val and A["out"][sb] is not None:
        pass
    for d in (0, 1):
        tb, tc = B["trans"][sb][d], C["trans"][sc][d]
        if tb < 0 or tc < 0: continue
        if (tb, tc) not in seen:
            seen.add((tb, tc)); q.append((tb, tc))
print("product states:", len(seen))
# now compare with A: need A's state after reading x, and B,C states after x
def step(D, n):
    s = 0
    for ch in reversed(bin(n)[2:]):
        s = D["trans"][s][int(ch)]
        if s < 0: return None
    return s
bad = []
for x in range(0, 5000):
    sa, sb, sc = step(A, x), step(B, x), step(C, x)
    if None in (sa, sb, sc): continue
    if A["out"][sa] != (B["out"][sb] ^ C["out"][sc]):
        bad.append(x)
print("mismatches over x<5000:", len(bad), bad[:5])
# exhaustive check on reachable product states incl. A
st = (0, 0, 0)
seen = {st}; q = deque([st]); ok = True
while q:
    sa, sb, sc = q.popleft()
    if A["out"][sa] != (B["out"][sb] ^ C["out"][sc]):
        ok = False
    for d in (0, 1):
        ta, tb, tc = A["trans"][sa][d], B["trans"][sb][d], C["trans"][sc][d]
        if -1 in (ta, tb, tc): continue
        if (ta, tb, tc) not in seen:
            seen.add((ta, tb, tc)); q.append((ta, tb, tc))
print("all reachable triples satisfy xor:", ok, " triples:", len(seen))
