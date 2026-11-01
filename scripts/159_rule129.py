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
    if len(d)>=20: break
print("data:", [d.get(n) for n in range(16)])
# rule 129: out[4*l+2*c+r] = (129 >> (4*l+2*c+r)) & 1
rule = lambda l,c,r: (129 >> (4*l+2*c+r)) & 1
# bounded light-cone convention: row n has cells -n..n, outside 0
rows = [[1]]  # row 0: position 0
for n in range(1, 16):
    prev = rows[-1]
    # prev covers -（n-1)..(n-1)
    new = []
    for j in range(-n, n+1):
        def get(k):
            idx = k + (n-1)
            return prev[idx] if 0 <= idx < len(prev) else 0
        new.append(rule(get(j-1), get(j), get(j+1)))
    rows.append(new)
print("row sizes:", [len(r) for r in rows[:6]])
mid = [rows[n][n] for n in range(16)]
print("middle col (bounded):", mid)
# all columns of each row aligned by center
for offset in range(-4, 5):
    col = []
    for n in range(len(rows)):
        j = offset
        idx = j + n
        col.append(rows[n][idx] if 0 <= idx < len(rows[n]) else 0)
    print(f"col offset {offset}:", col[:12])
