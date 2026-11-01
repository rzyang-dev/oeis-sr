import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A270803"]; B = m["A151666"]
print("A270803:", A["out"], A["trans"])
print("A151666:", B["out"], B["trans"])
def shiftd(trans, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return trans(s // 2, t % 2) * 2 + (t // 2)
def shiftout(trans, out, s):
    return out(trans(s // 2, True)) if s % 2 == 1 else out(s // 2)
def halveD(delta_trans, s, d):
    if s % 2 == 0:
        b = s // 4; c = (s // 2) % 2
        return b * 4 + (1 if d else 0) * 2 + 1
    b = s // 4; c = (s // 2) % 2
    t = shiftd(delta_trans, b * 2 + c, d)
    return (t // 2) * 4 + (t % 2) * 2 + 1
def halveOut(delta_trans, out, s):
    b = s // 4; c = (s // 2) % 2
    if s % 2 == 1:
        return shiftout(delta_trans, out, b * 2 + c)
    return out(b)
t0 = lambda b, d: B["trans"][b][1 if d else 0]
def fold(f, s, n):
    while n:
        s = f(s, n % 2 == 1); n //= 2
    return s
print("halve values:", [halveOut(t0, lambda b: B["out"][b], fold(lambda s,d: halveD(t0,s,d), 0, n)) for n in range(12)])
print("B((n+1)/2):", [B["out"][fold(t0, 0, (n+1)//2)] for n in range(12)])
# product reachable pairs for A270803 x halve
def reach(last1):
    R = {(0,0)}; q = deque([(0,0)])
    while q:
        a, h = q.popleft()
        for d in (0,1):
            na = A["trans"][a][d]; nh = halveD(t0, h, d)
            if (na,nh) not in R:
                R.add((na,nh)); q.append((na,nh))
    if not last1: return R
    R1 = set()
    for (a,h) in R:
        for d in (1,):
            na = A["trans"][a][d]; nh = halveD(t0, h, d)
            R1.add((na,nh))
    return R1
R = reach(False); R1 = reach(True)
print("R size:", len(R), "R1 size:", len(R1))
bad = [(p, A["out"][p[0]], halveOut(t0, lambda b: B["out"][b], p[1])) for p in R1 if A["out"][p[0]] != halveOut(t0, lambda b: B["out"][b], p[1])]
print("bad:", len(bad), bad[:5])
print("R1:", sorted(R1))
