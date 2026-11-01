import sys
sys.path.insert(0, ".")
from fractions import Fraction
from oeisdb.formula import parse, ev, FormulaError
for text in ["|n-3|", "Sum_{d|n} d", "n(n+1)/2"]:
    try:
        ast = parse(text)
        vals = []
        for n in range(5):
            v = ev(ast, {"n": Fraction(n)})
            vals.append(int(v) if v.denominator==1 else float(v))
        print("OK", text, vals)
    except Exception as e:
        print("FAIL", text, type(e).__name__, e)
