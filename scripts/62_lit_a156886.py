import json, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
def search(query, count=5):
    body = json.dumps({"query": query[:128], "count": count, "need_content": True}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())
qs = [
 "sum binomial(n,k) binomial(3n+k,k) closed form",
 "binomial(n,k) binomial(3n+k,k) congruence modulo 5",
 "coefficient of y^{3n} in (1+y)^{3n}(2+y)^n",
]
for q in qs:
    print("="*78); print("Q:", q)
    try: res = search(q)
    except Exception as e:
        print("ERR", e); continue
    for x in res.get("results", [])[:4]:
        print("-", (x.get("title") or "")[:88])
        print("  ", (x.get("url") or "")[:115])
        c = (x.get("content") or x.get("summary") or "").replace("\n"," ")
        print("  ", c[:300])
