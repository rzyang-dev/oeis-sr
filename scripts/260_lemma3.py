import sys
sys.stdout.reconfigure(encoding="utf-8")
# Lemma 3 check: for each neighborhood N and each v with norm d>=1, does v+N contain
# points of norm d-1, d, d+1 ?
def check(N_offsets, norm, name):
    bad = []
    for d in range(1, 12):
        pts = [(i, j) for i in range(-12, 13) for j in range(-12, 13) if norm(i,j) == d]
        if not pts: continue
        for (i,j) in pts:
            levels = set()
            for (a,b) in N_offsets:
                levels.add(norm(i+a, j+b))
            need = {d-1, d, d+1}
            if not need <= levels:
                bad.append(((i,j), d, sorted(levels)))
                break
    print(f"{name}: lemma-3 violations (d<=11): {len(bad)}  e.g. {bad[:2]}")
moore = [(a,b) for a in (-1,0,1) for b in (-1,0,1)]
vn = [(0,0),(1,0),(-1,0),(0,1),(0,-1)]
check(moore, lambda i,j: max(abs(i),abs(j)), "Moore/Chebyshev")
check(vn, lambda i,j: abs(i)+abs(j), "vonNeumann/Manhattan")
check([(a,0) for a in range(-3,4)], lambda i,j: max(1, (abs(i)+2)//3) if i!=0 or j!=0 else 0, "1D r=3 (norm=ceil)")
