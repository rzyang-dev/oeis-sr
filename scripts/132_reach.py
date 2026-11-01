import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def bfs(A, B, start_pairs):
    R = set(start_pairs)
    q = deque(start_pairs)
    while q:
        a, b = q.popleft()
        for d in (0, 1):
            na, nb = A["trans"][a][d], B["trans"][b][d]
            if na < 0 or nb < 0: continue
            if (na, nb) not in R:
                R.add((na, nb)); q.append((na, nb))
    return R
def check(name, A, B, sp):
    R = bfs(A, B, sp)
    bad = [(p, A["out"][p[0]], B["out"][p[1]]) for p in R if A["out"][p[0]] != B["out"][p[1]]]
    print(name, "R size", len(R), "bad pairs", len(bad), bad[:5])
# T1: A267442 vs A043545, successors of start (0,0)
A, B = m["A267442"], m["A043545"]
sp = [(A["trans"][0][0], B["trans"][0][0]), (A["trans"][0][1], B["trans"][0][1])]
check("A267442~A043545", A, B, sp)
# T4: A217586 vs XOR(A096268, A036987)
X = m["A217586"]; Y = m["A096268"]; Z = m["A036987"]
# build XOR automaton
states = {}
def sid(y, z):
    if (y, z) not in states: states[(y, z)] = len(states)
    return states[(y, z)]
q = deque([(0, 0)]); sid(0, 0)
trans = {}
while q:
    y, z = q.popleft()
    for d in (0, 1):
        ny, nz = Y["trans"][y][d], Z["trans"][z][d]
        if ny < 0 or nz < 0: trans[(sid(y,z), d)] = -1; continue
        if (ny, nz) not in states:
            states[(ny, nz)] = len(states); q.append((ny, nz))
        trans[(sid(y,z), d)] = sid(ny, nz)
n = len(states)
XOR = {"trans": [[trans.get((i,d), -1) for d in (0,1)] for i in range(n)],
       "out": [Y["out"][y] ^ Z["out"][z] for (y, z) in sorted(states, key=lambda k: states[k])]}
print("XOR automaton states:", n, "out:", XOR["out"])
sp = [(X["trans"][0][0], XOR["trans"][0][0]), (X["trans"][0][1], XOR["trans"][0][1])]
check("A217586~XOR", X, XOR, sp)
