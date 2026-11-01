import json, sys, random, re
from collections import Counter
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from oeisdb.formula import parse, FormulaError, Unsupported, clean_rhs

con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, text from formula where text like 'a(n) = %'").fetchall()
random.seed(7)
sample = random.sample(rows, 3000)
ok = 0
errs = Counter()
for aid, text in sample:
    rhs, lo = clean_rhs(text.split("=", 1)[1].strip())
    ast = None
    try:
        ast = parse(rhs)
        ok += 1
        continue
    except FormulaError as e:
        msg = str(e)
    # try equality chain
    for cand in [x.strip() for x in rhs.split("=")[:3]]:
        try:
            parse(cand); ok += 1; ast = True; break
        except FormulaError:
            pass
    if not ast:
        m = re.match(r"(bad char '.*?'|unexpected token .*|expected .*|trailing tokens|unknown function \w+)", msg)
        errs[m.group(1) if m else msg[:40]] += 1
print("sampled:", len(sample), "parsed:", ok, f"{100*ok/len(sample):.1f}%")
for k, n in errs.most_common(20):
    print(f"  {n:>5}  {k}")
