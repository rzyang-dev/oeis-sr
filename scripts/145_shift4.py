import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A306559"]; B = m["A039982"]
print("A states", A["states"], "shift", A["shift"], " B states", B["states"], "shift", B["shift"])
def shiftd(delta, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return delta["trans"][s // 2][t % 2] * 2 + (t // 2)
def shiftout(delta, out, s):
    return out[delta["trans"][s // 2][1]] if s % 2 == 1 else out[s // 2]
# build 4-fold shift
deltas = [A]
outs = [A["out"]]
s = 0 * 2 + 1
starts = [s]
for i in range(3):
    prev = deltas[-1]
    newdelta = {"trans": [[shiftd(prev, st, dd) for dd in (0,1)] for st in range(len(prev["trans"])*2+2)]}
    # need proper state space: shift states are unbounded encoding; instead compute BFS on demand
    break
# simpler: represent composed shift as a function on (b, c-stack) - do it iteratively via BFS on states
# State for k-fold shift: tuple of carries? Let's just simulate composed automaton by BFS on encoded states.
def compose_once(delta, outs_fun):
    # returns (new_trans dict, new_out dict, new_start) by BFS from reachable shift states
    trans = {}
    def step(s, d):
        return shiftd(delta, s, d)
    start = 1
    seen = {start}
    q = deque([start])
    while q:
        s = q.popleft()
        for d in (0, 1):
            t = step(s, d)
            if t not in seen:
                seen.add(t); q.append(t)
    return seen, step
# Build the 4-fold shift automaton explicitly by BFS over states (encoded as chain of carries)
# state = (b, c1, c2, c3, c4) where c1..c4 are carries at levels
start_state = (0, 1, 0, 0, 0)
def step4(st, d):
    b, c1, c2, c3, c4 = st
    # level 1: read digit d with carry c1 -> digit d1, carry c1'
    t1 = (1 if d else 0) + c1; d1 = t1 % 2; c1n = t1 // 2
    t2 = d1 + c2; d2 = t2 % 2; c2n = t2 // 2
    t3 = d2 + c3; d3 = t3 % 2; c3n = t3 // 2
    t4 = d3 + c4; d4 = t4 % 2; c4n = t4 // 2
    nb = A["trans"][b][d4]
    return (nb, c1n, c2n, c3n, c4n)
def out4(st):
    b, c1, c2, c3, c4 = st
    # after input exhausted: feed remaining carries
    val = c4
    # remaining bits: c1,c2,c3,c4 propagate with digit 0? Actually feed zeros: total = 0 + c_i
    s = b
    # simulate feeding c4 then c3... order: after the digits, the pending carry structure: need care
    # We'll just compute via nested shiftOut: out4 = shiftOut(delta3, shiftOut(delta2, shiftOut(delta1, oA)))
    return None
print("checking conjecture at data level first")
from pathlib import Path
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=2000):
    f = DATA/"files"/("A"+aid[1:4])/f"b{aid[1:]}.txt"
    d = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: d[int(q[0])]=int(q[1])
            except ValueError: pass
        if len(d)>=limit: break
    return d
a = bfile("A306559"); b = bfile("A039982")
bad = [n for n in range(0, 500) if (n+5) in a and n in b and a[n+5] != b[n]]
print("data mismatches for a(n+5)=b(n):", len(bad), bad[:5])
