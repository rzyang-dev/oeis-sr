import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
d = json.load(open("reports/long_equal.json", encoding="utf-8"))
print(type(d), len(d))
if isinstance(d, dict):
    print(list(d.keys())[:10])
    for k in list(d.keys())[:3]:
        print(k, str(d[k])[:300])
else:
    print(str(d[:3])[:600])
