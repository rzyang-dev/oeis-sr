import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rels = [("A014707","A038189"),("A030301","A275973"),("A034947","A112347"),("A035263","A285383"),
        ("A035263","A285384"),("A036577","A316826"),("A036987","A209229"),("A036987","A255738"),
        ("A039982","A306559"),("A043545","A347523"),("A092436","A010059"),("A096268","A284948"),
        ("A267442","A267579")]
parent = {}
def find(x):
    while parent.get(x, x) != x: x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
for a, b in rels: union(a, b)
comps = {}
for a, b in rels:
    for x in (a, b):
        comps.setdefault(find(x), set()).add(x)
print("shift-equivalence classes (nontrivial):", len(comps))
for c in comps.values():
    print("  ", sorted(c))
print()
# do the entries cross-reference each other?
new_ident = []
for a, b in rels:
    def mentions(x, y):
        rows = con.execute("select text from stmt where aid=?", (x,)).fetchall()
        return any(y in t for (t,) in rows)
    ab = mentions(a, b); ba = mentions(b, a)
    if not ab and not ba:
        new_ident.append((a, b))
print("pairs where NEITHER entry mentions the other:", len(new_ident))
for p in new_ident: print("  ", p)
