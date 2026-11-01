import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
r = con.execute("select terms, offset1 from seq where aid='A267417'").fetchone()
terms = [int(x) for x in r[0].split(",")[:120]]
print("offset1:", r[1])
print("terms:", terms[:60])
# simulate
B = 40
state = [0]*(2*B+1)
state[B] = 1
def step(s):
    n = len(s)
    new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        rr = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == rr) else 0
    return new
rows = []
for t in range(8):
    rows.append([state[i] for i in range(2*B+1)])
    state = step(state)
# try: row t = cells from -t..t
for t in range(6):
    print(f"row {t} [-t..t]:", [rows[t][B+j] for j in range(-t, t+1)])
