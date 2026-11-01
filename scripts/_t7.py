import sys
from fractions import Fraction
sys.path.insert(0, ".")
from oeisdb.formula import parse_full, ev
fw = {0:1,1:1,2:2,3:3,4:5,5:8}
ast = parse_full("1, if n <= 2; a(n-1) + a(n-2), if n > 2")
print([int(ev(ast, {"n": Fraction(n), "__self__": lambda k: Fraction(fw[k])})) for n in range(6)])
