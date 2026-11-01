import sys
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
rows = con.execute("select target, b, c, op, terms from pointwise_decomposition").fetchall()
text = defaultdict(list)
for aid, t in con.execute("select aid, text from stmt"):
    text[aid].append(t)
for aid, t in con.execute("select aid, text from formula"):
    text[aid].append(t)
terms_cache = {}
def tv(aid):
    if aid in terms_cache: return terms_cache[aid]
    r = con.execute("select terms from seq where aid=?", (aid,)).fetchone()
    v = []
    if r and r[0]:
        try: v = [int(x) for x in r[0].split(",")[:200]]
        except ValueError: v = []
    terms_cache[aid] = v
    return v
def okseq(aid):
    v = tv(aid)
    if len(v) < 20: return False
    if len(set(v)) <= 1: return False
    z = sum(1 for x in v if x == 0) / len(v)
    if z > 0.3: return False
    if all(x in (0,1) for x in v): return False
    return True
out = []
for t, b, c, op, n in rows:
    if n < 60: continue
    if not (okseq(t) and okseq(b) and okseq(c)): continue
    blob = " ".join(text.get(t, []))
    if b in blob or c in blob: continue
    out.append((t, b, c, op, n))
print("undocumented, all-substantial, >=60 terms:", len(out))
sym = {"sum":"+","diff":"-","prod":"*"}
for t, b, c, op, n in out[:25]:
    print(f"  {t} = {b} {sym[op]} {c}  n={n}")
    print(f"     T: {names.get(t,'')[:60]}")
    print(f"     B: {names.get(b,'')[:60]}")
    print(f"     C: {names.get(c,'')[:60]}")
