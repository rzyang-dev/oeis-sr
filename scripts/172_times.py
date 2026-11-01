import sys
sys.stdout.reconfigure(encoding="utf-8")
lo, hi = -600, 600
def step_edges(E):
    newE = set()
    for j in range(lo, hi):
        B0 = (j in E); A = ((j-1) in E); C = ((j+1) in E)
        if (not B0) and (A != C): newE.add(j)
    return newE
E = {-1, 0}
T = []
for t in range(70):
    T.append(set(E))
    E = step_edges(E)
for j in range(0, 9):
    times = [t for t in range(70) if j in T[t]]
    print(f"j={j}: times={times}")
    print(f"     binary={[bin(t) for t in times][:12]}")
