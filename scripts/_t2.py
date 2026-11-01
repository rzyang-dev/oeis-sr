import sys
sys.path.insert(0, ".")
from fractions import Fraction
from oeisdb.formula import parse, ev, FormulaError, clean_rhs
cases = [
    ("|n-3|", [3,2,1,0,1]),
    ("2n", [0,2,4,6,8]),
    ("1.5*n", [0,1,3,4,6]),
    ("Sum_{d|n} d", [0,1,3,4,7]),
    ("n(n+1)/2", [0,1,3,6,10]),
]
for text, want in cases:
    try:
        ast = parse(text)
    except FormulaError as e:
        print("PARSE FAIL", text, e); continue
    got = []
    for n in range(5):
        try:
            v = ev(ast, {"n": Fraction(n)})
            got.append(int(v) if v.denominator == 1 else float(v))
        except Exception as e:
            got.append("ERR"); break
    print(("OK " if got == want else "BAD"), text, got, "want", want)
