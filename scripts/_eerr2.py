import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from oeisdb.formula import parse, ev, FormulaError, Unsupported, clean_rhs
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, text from formula where text like 'a(n) = %' limit 600").fetchall()
_cache = {}
def terms(aid, limit=30):
    if aid in _cache: return _cache[aid]
    f = Path(r"C:\Users\ginger\oeisdata\files") / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    d = {}
    if f.exists():
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line=line.strip()
            if not line or line.startswith("#"): continue
            q=line.split()
            if len(q)>=2:
                try: d[int(q[0])]=int(q[1])
                except ValueError: pass
            if len(d)>=limit: break
    _cache[aid] = d or None
    return _cache[aid]
c = Counter()
for aid, text in rows:
    rhs, lo = clean_rhs(text.split("=",1)[1].strip())
    ast = None
    for cand in [rhs] + [x.strip() for x in rhs.split("=")[:3]]:
        try: ast = parse(cand); break
        except FormulaError: continue
    if ast is None: continue
    d = terms(aid)
    if not d: continue
    ns = [n for n in sorted(d) if n >= lo][:8]
    for n in ns:
        env = {"n": Fraction(n),
               "__seq__": lambda a,k: Fraction(terms(a)[k]) if terms(a) and k in terms(a) else (_ for _ in ()).throw(FormulaError("missing_A")),
               "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing_a"))}
        try:
            ev(ast, env)
        except Unsupported as e:
            c["UNSUP " + str(e)[:28]] += 1; break
        except Exception as e:
            m = str(e)
            if m.startswith("unbound"): key = "unbound " + m.split()[1]
            elif m.startswith("missing"): key = m
            else: key = m[:28]
            c[key] += 1; break
print("errors:", sum(c.values()))
for k, v in c.most_common(12): print(f"  {v:>4}  {k}")
