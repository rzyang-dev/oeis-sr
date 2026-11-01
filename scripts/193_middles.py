import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rules = [0, 8, 32, 40, 64, 72, 96, 104, 126, 128, 129, 136, 151, 159, 160, 161, 168, 183, 191, 192, 200, 215, 222, 223, 224, 232, 247, 253, 254, 255]
N = 80
def middle(rule, T=24):
    W = 2*N+1
    s = [0]*W; s[N] = 1
    out = []
    for t in range(T):
        out.append(s[N])
        ns = [0]*W
        for i in range(W):
            l = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r = s[i+1] if i+1 < W else 0
            ns[i] = (rule >> (4*l+2*c+r)) & 1
        s = ns
    return out
# build prefix index of OEIS terms
pref = {}
rows = con.execute("select aid, terms from seq where terms is not null").fetchall()
for aid, tms in rows:
    parts = tms.split(",")[:20]
    try:
        vals = [int(x) for x in parts]
    except ValueError:
        continue
    if len(vals) < 15: continue
    pref.setdefault(tuple(vals[:15]), []).append(aid)
found = 0
for rule in rules:
    m = middle(rule, 24)
    key = tuple(m[:15])
    hits = pref.get(key, [])
    if hits:
        found += 1
        print(f"rule {rule:3d}: middle={m[:10]}  -> {hits[:3]}")
print(f"\n{found}/{len(rules)} middle columns found in OEIS (first 15 terms exact)")
