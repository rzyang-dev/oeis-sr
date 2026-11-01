import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 120
lo, hi = -40, 40
def step_edges(E):
    # E: set of j with edge between j and j+1
    newE = set()
    for j in range(lo, hi):
        B0 = (j in E); A = ((j-1) in E); C = ((j+1) in E)
        if (not B0) and (A != C):
            newE.add(j)
    return newE
E = {-1, 0}
for t in range(13):
    xs = sorted(E)
    iv = []
    for z in xs:
        if iv and z == iv[-1][1] + 1: iv[-1][1] = z
        else: iv.append([z, z])
    print(f"t={t:2d} |E|={len(E):3d} E-intervals={iv[:10]}")
    E = step_edges(E)
