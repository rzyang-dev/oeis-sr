import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
hits = json.load(open("reports/sqrt_fixed.json", encoding="utf-8"))
print("raw hits:", len(hits))
terms = {}
def tv(aid):
    if aid in terms: return terms[aid]
    r = con.execute("select terms from seq where aid=?", (aid,)).fetchone()
    v = [int(x) for x in r[0].split(",")[:80]] if r and r[0] else []
    terms[aid] = v
    return v
strong = []
for a, b, g in hits:
    vb = tv(b)
    if len(vb) < 20: continue
    z = sum(1 for x in vb if x == 0) / len(vb)
    if z > 0.3: continue
    if len(set(vb)) <= 2: continue
    if g < 30: continue
    strong.append((a, b, g))
print("strong:", len(strong))
for a, b, g in strong[:20]:
    print(f"  {a} = {b} * {b} ok={g}")
    print(f"     A: {names.get(a,'')[:58]}")
    print(f"     B: {names.get(b,'')[:58]}")
