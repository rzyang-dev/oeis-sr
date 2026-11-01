import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
def terms(aid, n=20):
    r = con.execute("select terms, offset1 from seq where aid=?", (aid,)).fetchone()
    return [int(x) for x in r[0].split(",")[:n]], r[1]
t445, o445 = terms("A267445", 22)
print("A267445 offset", o445, ":", t445)
# our closed form: ON count in row t = 2t+1 - 2^{popcount(t)}
def pred_on(t):
    cells = 2*t+1
    zeros = 2**bin(t).count('1')
    return cells - zeros
print("predicted        :", [pred_on(t) for t in range(o445, o445+len(t445))])
# check
ok = all(pred_on(o445+i) == v for i, v in enumerate(t445))
print("A267445 conjecture decided:", ok)
# OFF count
t447, o447 = terms("A267447", 22)
print("A267447 offset", o447, ":", t447)
pred_off = lambda t: 2**bin(t).count('1')
print("predicted OFF    :", [pred_off(t) for t in range(o447, o447+len(t447))])
print("A267447 decided:", all(pred_off(o447+i) == v for i, v in enumerate(t447)))
