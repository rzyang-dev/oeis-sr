import sys, random, re
from collections import defaultdict
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from oeisdb.formula import parse, FormulaError, clean_rhs
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, text from formula where text like 'a(n) = %'").fetchall()
random.seed(7)
sample = random.sample(rows, 3000)
by = defaultdict(list)
for aid, text in sample:
    rhs, lo = clean_rhs(text.split("=", 1)[1].strip())
    try:
        parse(rhs); continue
    except FormulaError as e:
        msg = str(e)
    allowed = False
    for cand in [x.strip() for x in rhs.split("=")[:3]]:
        try:
            parse(cand); allowed = True; break
        except FormulaError:
            pass
    if not allowed:
        key = "trailing" if "trailing" in msg else ("paren" if "expected )" in msg else ("bar" if "|" in msg else "other"))
        if len(by[key]) < 8:
            by[key].append((aid, msg[:30], rhs[:110]))
for k, v in by.items():
    print("==", k)
    for aid, msg, rhs in v:
        print(f"  {aid} [{msg}] {rhs}")
