import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
f = DATA/"files"/"A267"/"b267442.txt"
d = {}
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: d[int(q[0])]=int(q[1])
        except ValueError: pass
    if len(d)>=40: break
target = [d.get(n) for n in range(32)]
B = 80
state = [0]*(2*B+1)
state[B] = 1
def step(s):
    n = len(s)
    new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        r = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == r) else 0
    return new
mid = []
for t in range(32):
    mid.append(state[B])
    state = step(state)
print("simulated:", mid)
print("target   :", target)
print("match:", mid == target)
