import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
r = con.execute("select aid, name, terms, offset1 from seq where aid='A185587'").fetchone()
print("NAME:", r[1])
print("OFFSET:", r[3])
print("TERMS:", r[2][:300])
for (t,) in con.execute("select text from stmt where aid='A185587' order by rowid limit 8", ()):
    print("  -", t[:250])
