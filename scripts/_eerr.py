import sys
from collections import Counter
from fractions import Fraction
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from oeisdb.formula import parse, ev, FormulaError, Unsupported, clean_rhs
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, text from formula where text like 'a(n) = %' limit 4000").fetchall()
def bfile(aid, limit=40):
    f = Path(r"C:\Users\ginger\oeisdata\files") / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists(): return None
    d = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: d[int(q[0])]=int(q[1])
            except ValueError: pass
        if len(d)>=limit: break
    return d or None
from pathlib import Path
c = Counter()
for aid, text in rows:
    rhs, lo = clean_rhs(text.split("=",1)[1].strip())
    ast = None
    for cand in [rhs] + [x.strip() for x in rhs.split("=")[:3]]:
        try: ast = parse(cand); break
        except FormulaError: continue
    if ast is None: continue
    d = bfile(aid)
    if not d: continue
    ns = [n for n in sorted(d) if n >= lo][:10]
    for n in ns:
        env = {"n": Fraction(n),
               "__seq__": lambda a,k: Fraction(bfile(a)[k]) if bfile(a) and k in bfile(a) else (_ for _ in ()).throw(FormulaError("missing_A")),
               "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing_a"))}
        try:
            ev(ast, env)
        except Unsupported as e:
            c["UNSUP " + str(e)[:30]] += 1
            break
        except Exception as e:
            m = str(e)
            c[("unbound "+m.split()[1]) if m.startswith("unbound") else m[:30]] += 1
            break
print("errors:", sum(c.values()))
for k, v in c.most_common(15):
    print(f"  {v:>5}  {k}")
