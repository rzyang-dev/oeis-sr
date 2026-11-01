import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def reach(A, B):
    R = {(0,0)}; q = deque([(0,0)])
    while q:
        a,b = q.popleft()
        for d in (0,1):
            na, nb = A["trans"][a][d], B["trans"][b][d]
            if na<0 or nb<0: continue
            if (na,nb) not in R: R.add((na,nb)); q.append((na,nb))
    return R
A,B = m["A267442"], m["A043545"]
R = reach(A,B)
print("R1 =", sorted(R))
X = m["A217586"]; Y = m["A096268"]; Z = m["A036987"]
states = {}
def sid(y,z):
    states.setdefault((y,z), len(states)); return states[(y,z)]
q = deque([(0,0)]); sid(0,0); trans = {}
while q:
    y,z = q.popleft()
    for d in (0,1):
        ny,nz = Y["trans"][y][d], Z["trans"][z][d]
        if ny<0 or nz<0: trans[(sid(y,z),d)] = -1; continue
        if (ny,nz) not in states: states[(ny,nz)] = len(states); q.append((ny,nz))
        trans[(sid(y,z),d)] = sid(ny,nz)
n = len(states)
XOR = {"trans": [[trans.get((i,d),-1) for d in (0,1)] for i in range(n)],
       "out": [Y["out"][y]^Z["out"][z] for (y,z) in sorted(states, key=lambda k: states[k])]}
print("XOR trans =", XOR["trans"], "out =", XOR["out"])
R2 = reach(X, XOR)
print("R2 =", sorted(R2))
