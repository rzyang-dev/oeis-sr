import sys
sys.path.insert(0, ".")
from fractions import Fraction
from oeisdb.formula import parse, ev
for text in ["n(n+1)/2", "Sum_{d|n} d", "binomial(n,k)", "A000045(n)"]:
    try:
        ast = parse(text)
        vals = []
        for n in range(1, 6):
            v = ev(ast, {"n": Fraction(n), "__seq__": lambda a,k: Fraction(1)})
            vals.append(int(v) if v.denominator==1 else float(v))
        print("OK", text, vals)
    except Exception as e:
        print("FAIL", text, type(e).__name__, e)
