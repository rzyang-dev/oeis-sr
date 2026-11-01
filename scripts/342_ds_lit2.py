
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
 '"all neighbours equal" cellular automaton',
 'cellular automaton tree lattice same pattern independence geometry',
 'zero set elementary cellular automaton digit condition closed formula',
 'A267444 middle column Rule 129',
]
for q in qs:
    try:
        j = search(q); res = j.get("results", [])
        print("\n### " + q + "   (" + str(len(res)) + " results)")
        for x in res:
            print("- " + str(x.get("title"))[:88])
            print("   " + str(x.get("url"))[:95])
            print("   " + (x.get("summary") or "").replace("\n"," ")[:160])
    except Exception as e:
        print("\n### " + q + " ERR " + str(e)[:120])
    time.sleep(1)
