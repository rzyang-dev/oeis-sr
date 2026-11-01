import sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
print(con.execute("select sql from sqlite_master where name='pointwise_decomposition'").fetchone()[0])
print("rows:", con.execute("select count(*) from pointwise_decomposition").fetchone()[0])
print(con.execute("select * from pointwise_decomposition limit 5").fetchall())
print("\nby kind:", con.execute("select kind, count(*) from pointwise_decomposition group by 1").fetchall())
