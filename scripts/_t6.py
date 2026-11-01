import sys
sys.path.insert(0, ".")
from oeisdb.formula import clean_rhs, parse
for t in ["a(n-1)*n*2^(n-1), a(0) = 1.", "a(n-1) - a(n-2), a(0)=1, a(1)=1.", "a(n-1) + a(n-2), a(0)=0, a(1)=1"]:
    r, lo = clean_rhs(t)
    try:
        parse(r); ok = "OK"
    except Exception as e:
        ok = "FAIL " + str(e)[:40]
    print(repr(t), "->", repr(r), ok)
