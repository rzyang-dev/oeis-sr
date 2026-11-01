import json, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
def search(query, count=5):
    body = json.dumps({"query": query, "count": count, "need_content": True}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())
for q in ["cphi_2(n) 5n+3 congruent 0 mod 5 2-colored Frobenius partitions",
          "Eichhorn Sellers 2-colored Frobenius partitions congruences mod 5 theorem"]:
    print("="*78); print("Q:", q)
    try: res = search(q)
    except Exception as e:
        print("ERR", e); continue
    for x in res.get("results", [])[:4]:
        print("-", (x.get("title") or "")[:90])
        print("  ", (x.get("url") or "")[:110])
        c = (x.get("content") or x.get("summary") or "").replace("\n"," ")
        print("  ", c[:600])
