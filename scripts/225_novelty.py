import sys, json, sqlite3, re
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
exprs = {
"A014707": ["A010059","A010060","A014577"],
"A030301": ["A010059","A010060","A030300"],
"A043545": ["A010059","A010060","A036987"],
"A059448": ["A010060","A030300","A035263"],
"A086694": ["A010059","A010060","A079944"],
"A092436": ["A010059","A035263"],
"A096268": ["A010059","A010060","A035263"],
"A164056": ["A014577","A036987","A099395"],
"A217586": ["A010059","A010060","A035263","A036987"],
"A254377": ["A010059","A010060","A228495"],
"A254379": ["A010060","A228495"],
"A254651": ["A010059","A228495"],
"A267442": ["A010059","A010060","A036987","A209229","A255738"],
"A268411": ["A010060","A020987"],
"A275973": ["A010059","A010060","A030300","A036987"],
"A285383": ["A010059","A010060","A284948"],
"A285384": ["A010059","A010060","A209229","A255738","A284948"],
"A292077": ["A014577","A035263"],
"A295890": ["A010059","A010060","A295889"],
"A298952": ["A010059","A030300","A036987"],
"A324964": ["A085357","A085405"],
"A328981": ["A035263","A038189","A073089","A209229","A255738"],
"A341389": ["A010060","A269723"],
"A342892": ["A010059","A010060","A086483"],
"A347523": ["A010059","A010060","A209229"],
"A359832": ["A010059","A010060","A035263","A038189","A073089","A209229","A255738"],
"A379728": ["A010059","A038189","A073089","A209229","A228495","A255738","A255817","A372258"],
}
def mentions(aid, other):
    rows = con.execute("select text from stmt where aid=?", (aid,)).fetchall()
    return any(other in t for (t,) in rows)
doc = 0; new = 0
lines = []
for a, parts in exprs.items():
    hits = [p for p in parts if mentions(a, p)]
    if len(hits) == len(parts):
        status = "DOCUMENTED(all)"
        doc += 1
    elif hits:
        status = "partial:" + ",".join(hits)
        doc += 1
    else:
        status = "NEW"
        new += 1
    lines.append(f"{a:9s} <- {'+'.join(parts):50s} {status}")
print("\n".join(lines))
print(f"\ndocumented/partial: {doc}   NEW: {new}")
