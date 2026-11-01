import sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select target, b, c, op, terms from pointwise_decomposition").fetchall()
names = dict(con.execute("select aid, name from seq"))
# text per target
text = defaultdict(list)
for aid, t in con.execute("select aid, text from stmt"):
    text[aid].append(t)
for aid, t in con.execute("select aid, text from formula"):
    text[aid].append(t)
print("relations:", len(rows))
doc = undoc = 0
examples = []
for t, b, c, op, n in rows:
    blob = " ".join(text.get(t, []))
    if b in blob or c in blob:
        doc += 1
    else:
        undoc += 1
        if n >= 60:
            examples.append((t, b, c, op, n))
print("documented (b or c mentioned):", doc, " undocumented:", undoc)
print("undocumented with >=60 terms:", len(examples))
sym = {"sum":"+","diff":"-","prod":"*"}
for t, b, c, op, n in examples[:20]:
    print(f"  {t} = {b} {sym[op]} {c}  n={n}")
    print(f"     T: {names.get(t,'')[:60]}")
    print(f"     B: {names.get(b,'')[:60]}")
    print(f"     C: {names.get(c,'')[:60]}")
