import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
ver = json.load(open("reports/closed_loop_verified.json", encoding="utf-8"))
z1 = [x["aid"] for x in ver if x["kind"] == "z1"]
def bfile(aid, limit=600):
    f = DATA / "files" / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists(): return None
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
periodic = []
notp = []
for aid in z1:
    v = bfile(aid)
    if not v or len(v) < 100: continue
    ok = all(v[n+5] % 5 == v[n] % 5 for n in range(len(v)-5))
    (periodic if ok else notp).append(aid)
print("Z={1} tested:", len(periodic)+len(notp))
print("mod-5 periodic (period 5):", len(periodic))
print("not periodic:", len(notp))
print("\nperiodic examples:", periodic[:12])
