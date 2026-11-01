import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, name from seq where name like '%Rule 18%' limit 40").fetchall()
for r in rows: print(r[0], "|", r[1][:130])
print("---")
rows = con.execute("select aid, name from seq where name like '%Rule 129%' limit 20").fetchall()
for r in rows: print(r[0], "|", r[1][:130])
