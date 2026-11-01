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
trans = lambda b, d: A["trans"][b][1 if d else 0]
out = lambda b: A["out"][b]
start = 1
for level in range(4):
    trans, out, start = (lambda t, o: (lambda s, d: shiftd(t, s, d), lambda s: shiftout(t, o, s), t(start, True) * 2 + 1))(trans, out)
def fold(f, s, n):
    while n:
        s = f(s, n % 2 == 1)
        n //= 2
    return s
vals = [out(fold(trans, start, n)) for n in range(15)]
print("shift4 values:", vals)
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
print("A039982 values:", [b.get(n) for n in range(15)])
print("match:", all(vals[n] == b.get(n) for n in range(15)))
