import sys, re
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, field, text from stmt where text like '%onjectur%'").fetchall()
print("statements mentioning conjecture:", len(rows), "seqs:", len({r[0] for r in rows}))
forms = Counter()
samples = []
for aid, field, t in rows:
    tl = t.lower()
    if "conjecture:" in tl or "conjectured that" in tl or "it appears that" in tl or "empirically" in tl:
        forms["explicit"] += 1
        samples.append((aid, field, t))
    else:
        forms["mention"] += 1
print(dict(forms))
print("\nsample explicit conjectures:")
for aid, field, t in samples[:15]:
    print(f"  {aid} [{field}] {t[:150]}")
