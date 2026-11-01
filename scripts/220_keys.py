import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
print("records:", len(rows))
print("keys:", list(rows[0].keys()))
import collections
print(collections.Counter(tuple(sorted(r.keys())) for r in rows).most_common(3))
for r in rows[:2]:
    print({k: (v if not isinstance(v, list) else str(v)[:60]) for k, v in r.items()})
