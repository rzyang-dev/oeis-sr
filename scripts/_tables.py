import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A306559"]; B = m["A039982"]
print("A306559 out:", A["out"])
print("A306559 trans:", A["trans"])
print("A039982 out:", B["out"])
print("A039982 trans:", B["trans"])
