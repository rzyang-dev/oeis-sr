import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
f = DATA/"files"/"A014"/"b014709.txt"
d = {}
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: d[int(q[0])]=int(q[1])
        except ValueError: pass
    if len(d)>=30: break
print("terms:", list(d.items())[:20])
