import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
f = DATA/"files"/"A216"/"b216059.txt"
d = {}
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: d[int(q[0])]=int(q[1])
        except ValueError: pass
print("terms:", len(d))
vals = sorted(set(d.values()))
print("values:", vals, "counts:", {v: sum(1 for x in d.values() if x==v) for v in vals})
for m in range(1, 11):
    seen = {}
    ok = True
    for n, v in d.items():
        r = n % (1 << m)
        if r in seen and seen[r] != v:
            ok = False
            break
        seen[r] = v
    print(f"m={m}: depends only on n mod {1<<m}: {ok}")
    if ok: break
# print the residue table
m = 6
tab = {}
for n, v in d.items():
    tab.setdefault(n % (1 << m), set()).add(v)
print("residues mod 64 with multiple values:", {k: v for k, v in tab.items() if len(v) > 1})
