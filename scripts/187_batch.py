import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
rows = con.execute("select aid, name from seq where name like '%Rule 129%' or name like '%Rule 126%' or name like '%rule 126%' limit 40").fetchall()
print("count:", len(rows))
for aid, name in rows[:30]:
    print(aid, "|", name[:110])
    for (t,) in con.execute("select text from stmt where aid=? and (text like '%onjecture%' or text like '%Conjecture%') limit 2", (aid,)):
        print("     CONJ:", t[:150])
