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
    if len(d)>=24: break
target = [d.get(n) for n in range(20)]
print("target:", target)
def run(rule_num, outside, invert, steps=20):
    rule = lambda l,c,r: ((rule_num >> (4*l+2*c+r)) & 1) ^ invert
    rows = [[1]]
    for n in range(1, steps):
        prev = rows[-1]
        def get(k):
            idx = k + (n-1)
            if 0 <= idx < len(prev): return prev[idx]
            return outside
        rows.append([rule(get(j-1), get(j), get(j+1)) for j in range(-n, n+1)])
    return rows
best = None
for rule_num in (129, 129 ^ 255, 126, 63):
    for outside in (0, 1):
        for invert in (0, 1):
            rows = run(rule_num, outside, invert, 20)
            col = [rows[n][n] for n in range(20)]
            score = sum(1 for i in range(20) if col[i] == target[i])
            if best is None or score > best[0]:
                best = (score, rule_num, outside, invert, col)
            print(f"rule={rule_num} outside={outside} invert={invert} score={score}/20 col={col[:10]}")
print("BEST:", best)
