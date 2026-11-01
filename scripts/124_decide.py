import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
def decide(A, B):
    # n >= 1: LSB-first strings start with digit 1
    start = (A["trans"][0][1], B["trans"][0][1])
    if start[0] < 0 or start[1] < 0:
        return "undefined"
    seen = {start}
    q = deque([start])
    while q:
        sa, sb = q.popleft()
        if A["out"][sa] != B["out"][sb]:
            return "mismatch"
        for d in (0, 1):
            ta, tb = A["trans"][sa][d], B["trans"][sb][d]
            if ta < 0 or tb < 0:
                continue
            if (ta, tb) not in seen:
                seen.add((ta, tb))
                q.append((ta, tb))
    return "equal for all n>=1"
pairs = [("A267442","A043545"), ("A284948","A096268"), ("A285383","A035263"), ("A217586","A036987")]
for a, b in pairs:
    if a in m and b in m:
        print(f"{a} vs {b}: {decide(m[a], m[b])}")
    else:
        print(f"{a} vs {b}: missing ({a in m}, {b in m})")
