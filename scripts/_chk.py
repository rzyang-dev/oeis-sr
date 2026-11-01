import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
for aid in ("A011266", "A010892", "A033312"):
    f = Path(r"C:\Users\ginger\oeisdata\files") / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    v = []
    if f.exists():
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line=line.strip()
            if not line or line.startswith("#"): continue
            q=line.split()
            if len(q)>=2:
                try: v.append((int(q[0]), int(q[1])))
                except ValueError: pass
            if len(v)>=10: break
    print(aid, v[:8])
