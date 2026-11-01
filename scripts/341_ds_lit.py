
import json, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
KEY = open('APIkey', encoding='utf-8').read().strip()
def search(q, count=6):
    body = json.dumps({"query": q, "count": count}).encode('utf-8')
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)
qs = [
 "unanimity rule cellular automaton",
 "k-regular sequence cellular automaton 2-kernel",
 "cellular automaton closed form submask bitwise",
 "Rule 129 center column powers of two proof",
 "A071051 Rule 126 number of ON cells formula",
 "graph cellular automata consensus dynamics closed form",
 "cellular automaton radial solution tree",
 "Stern's diatomic sequence cellular automaton",
]
out = {}
for q in qs:
    try:
        j = search(q)
        res = j.get("results", [])
        out[q] = [{"t": x.get("title"), "u": x.get("url"), "s": (x.get("summary") or "")[:200]} for x in res]
        print("\n### " + q)
        for x in out[q]:
            print("- " + str(x["t"])[:90])
            print("   " + str(x["u"])[:100])
            print("   " + x["s"].replace("\n"," ")[:180])
    except Exception as e:
        print("\n### " + q + "  ERR " + str(e)[:150])
    time.sleep(1)
json.dump(out, open('reports/ds_search_lit.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
