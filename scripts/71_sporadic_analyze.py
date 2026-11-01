import json, glob, sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from oeisdb.formula import parse, ev, FormulaError, Unsupported, clean_rhs
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
_cache = {}
def terms(aid, limit=60):
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
rows = []
for f in glob.glob("reports/consistency_*.json"):
    rows += json.load(open(f, encoding="utf-8")).get("sporadic", [])
print("sporadic entries:", len(rows))
res = []
for x in rows:
    aid, text = x["aid"], x["text"]
    rhs, lo = clean_rhs(text.split("=",1)[1].strip() if "=" in text else text)
    ast = None
    for cand in [rhs] + [x.strip() for x in rhs.split("=")[:3]]:
        try: ast = parse(cand); break
        except FormulaError: continue
    if ast is None: continue
    d = terms(aid)
    if not d: continue
    ns = [n for n in sorted(d) if n >= lo][:40]
    flags = []
    for n in ns:
        env = {"n": Fraction(n),
               "__seq__": lambda a,k: Fraction(terms(a)[k]) if terms(a) and k in terms(a) else (_ for _ in ()).throw(FormulaError("missing_A")),
               "__self__": lambda k: Fraction(d[k]) if k in d else (_ for _ in ()).throw(FormulaError("missing_a"))}
        try:
            v = ev(ast, env)
        except Unsupported:
            flags.append(None); continue
        except FormulaError as e:
            if "missing_" in str(e): flags.append(None); continue
            flags.append(None); continue
        except Exception:
            flags.append(None); continue
        flags.append(v.denominator == 1 and v.numerator == d[n])
    # longest run of True
    best = cur = 0
    for f in flags:
        if f is True: cur += 1; best = max(best, cur)
        else: cur = 0
    res.append((best, aid, text[:100]))
res.sort(reverse=True)
from collections import Counter
print("with run>=10:", sum(1 for r in res if r[0] >= 10), " run>=20:", sum(1 for r in res if r[0] >= 20), " <5:", sum(1 for r in res if r[0] < 5))
print("\nlongest runs:")
for r in res[:10]: print(f"  run={r[0]} {r[1]} | {r[2]}")
print("\nno-run cases (potential real mismatches):")
for r in [x for x in res if x[0] < 3][:15]: print(f"  {r[1]} | {r[2]}")
