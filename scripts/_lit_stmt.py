import json, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
def search(query, count=6):
    body = json.dumps({"query": query, "count": count, "need_content": False}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())
qs = [
 "partitions into parts not divisible by 49 congruence modulo 7",
 "partitions with no parts multiples of 25 congruence mod 5",
 "2-colored generalized Frobenius partitions congruence",
 "McKay-Thompson series class 3C congruence coefficients mod 7",
 "eta quotient partition congruence modulo 5 zero residue class",
]
for q in qs:
    print("="*78); print("Q:", q)
    try: res = search(q)
    except Exception as e:
        print("ERR", e); continue
    for x in res.get("results", [])[:5]:
        print("-", (x.get("title") or "")[:88])
        print("  ", (x.get("url") or "")[:115])
        print("  ", (x.get("summary") or "").replace("\n"," ")[:180])
