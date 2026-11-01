import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("reports/conjecture_unconfirmed.json", encoding="utf-8"))
print("unconfirmed records:", len(d))
from collections import Counter
print("shifts:", Counter(x["shift"] for x in d))
