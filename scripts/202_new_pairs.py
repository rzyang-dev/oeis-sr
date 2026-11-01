import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
pairs = [("A014707","A038189"),("A030301","A275973"),("A034947","A112347"),("A035263","A285383"),
         ("A035263","A285384"),("A036577","A316826"),("A036987","A209229"),("A036987","A255738"),
         ("A039982","A306559"),("A043545","A347523"),("A092436","A010059"),("A096268","A284948"),
         ("A267442","A267579")]
seen = set()
for a, b in pairs:
    for aid in (a, b):
        if aid in seen: continue
        seen.add(aid)
        r = con.execute("select name, terms from seq where aid=?", (aid,)).fetchone()
        if r:
            print(f"{aid}: {r[0][:110]}")
            print(f"      terms: {r[1][:60]}")
