import sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
from oeisdb.formula import parse, ev, clean_rhs

# triangle A027907 (1+x+x^2)^n, flat rows
flat = [1, 1,1,1, 1,2,3,2,1, 1,3,6,7,6,3,1]
d = {i: v for i, v in enumerate(flat)}
def tri(aid, n, k):
    return Fraction(d[n*(n+1)//2 + k])
for text in ["A027907(n,2)", "A027907(2,1)", "Sum_{k=0..n} A027907(n,k)"]:
    ast = parse(text)
    vals = []
    for n in range(3):
        v = ev(ast, {"n": Fraction(n), "__tri__": tri, "__seq__": lambda a,k: (_ for _ in ()).throw(Exception("no"))})
        vals.append(int(v))
    print("OK", text, vals)
# piecewise cleaning
print(clean_rhs("a(n-1) + a(n-2), a(0)=0, a(1)=1")[0])
