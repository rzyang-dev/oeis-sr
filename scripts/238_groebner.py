import sys
sys.stdout.reconfigure(encoding="utf-8")
try:
    import sympy
    print("sympy", sympy.__version__)
except ImportError:
    print("no sympy"); sys.exit(0)
from sympy import symbols, groebner, Poly, GF
x, f0, f1, f2 = symbols('x f0 f1 f2')
# A036987: d(0,0)=1, d(0,1)=0 ; d(1,0)=1, d(1,1)=2 ; d(2,*)=2
# f_s = f_{d(s,0)}^2 + x*f_{d(s,1)}^2
g0 = f0 + f1**2 + x*f0**2
g1 = f1 + f1**2 + x*f2**2
g2 = f2 + f2**2 + x*f2**2
G = groebner([g0, g1, g2], f1, f2, f0, x, order='lex', modulus=2)
print("groebner computed")
polys = G.polys
for p in polys:
    print("  ", p.as_expr())
