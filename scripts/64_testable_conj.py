import sys, re
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, text from stmt where text like '%Conjecture%'").fetchall()
print("conjecture statements:", len(rows))

T = {
 "parity_iff": re.compile(r"a\(n\)\s*is\s+(odd|even)\s+iff", re.I),
 "divisible_by": re.compile(r"a\(n\)\s*is\s+(?:always\s+)?divisible\s+by\s+(\d+)", re.I),
 "mod_zero": re.compile(r"a\(n\)\s*(?:==|≡|is congruent to)\s*0\s*\(?\s*mod(?:ulo)?\s*(\d+)", re.I),
 "prime": re.compile(r"a\(n\)\s*is\s+(?:always\s+)?prime", re.I),
 "equals_seq": re.compile(r"a\(n\)\s*=\s*A\d{6}\(", re.I),
 "div_n": re.compile(r"a\(n\)\s*is\s+divisible\s+by\s+n\b", re.I),
 "square": re.compile(r"a\(n\)\s*is\s+a\s+(?:perfect\s+)?square", re.I),
}
cat = Counter()
examples = {}
for aid, t in rows:
    tl = t.lower()
    if "proved" in tl or "this is true" in tl or "has been proved" in tl:
        continue
    for k, rx in T.items():
        if rx.search(t):
            cat[k] += 1
            examples.setdefault(k, []).append((aid, t[:130]))
            break
print("testable-ish conjectures (excluding proved):", sum(cat.values()))
for k, n in cat.most_common():
    print(f"  {k}: {n}")
    for a, t in examples[k][:3]:
        print(f"     {a}: {t}")
