import sys
sys.stdout.reconfigure(encoding="utf-8")
lo, hi = -400, 400
def step_edges(E):
    newE = set()
    for j in range(lo, hi):
        B0 = (j in E); A = ((j-1) in E); C = ((j+1) in E)
        if (not B0) and (A != C): newE.add(j)
    return newE
E = {-1, 0}
for t in range(33):
    pos = sorted(j for j in E if j >= 0)
    others = sorted(j for j in E if j < 0)
    print(f"t={t:2d} {bin(t)[2:]:>6} pos={pos} neg={others}")
    E = step_edges(E)
