import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=40):
    f = DATA / "files" / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    v = []
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: v.append(int(q[1]))
            except ValueError: pass
        if len(v)>=limit: break
    return v
for aid in ("A182386", "A056545"):
    v = bfile(aid)
    print(aid, "first:", v[:10])
    print("  mod5:", [x % 5 for x in v[:12]])
    print("  a(1) mod 5:", v[1] % 5, " all a(5m+1)=0:", all(v[5*m+1] % 5 == 0 for m in range(len(v)//5) if 5*m+1 < len(v)))
