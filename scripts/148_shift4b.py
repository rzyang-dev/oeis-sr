import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A306559"]; B = m["A039982"]
def shiftd(trans, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return trans(s // 2, t % 2) * 2 + (t // 2)
def shiftout(trans, out, s):
    return out(trans(s // 2, True)) if s % 2 == 1 else out(s // 2)
def fold(f, s, n):
    while n:
        s = f(s, n % 2 == 1)
        n //= 2
    return s
t = lambda b, d: A["trans"][b][1 if d else 0]
o = lambda b: A["out"][b]
start = 1  # enc2(0,1)
print("A:", [o(fold(t, 0, n)) for n in range(12)])
for level in range(4):
    t_new = lambda s, d, t=t: shiftd(t, s, d)
    o_new = lambda s, o=o, t=t: shiftout(t, o, s)
    start_new = start * 2 + 1
    t, o, start = t_new, o_new, start_new
    print(f"shift{level+1} start={start}:", [o(fold(t, start, n)) for n in range(10)])
from pathlib import Path
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=100):
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
b = bfile("A039982")
vals = [o(fold(t, start, n)) for n in range(10)]
print("shift4:", vals)
print("A039982:", [b.get(n) for n in range(10)])
print("match:", all(vals[n] == b.get(n) for n in range(10)))
