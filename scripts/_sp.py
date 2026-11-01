import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("reports/formula_suffix_00.json", encoding="utf-8"))
print(len(d))
for x in d:
    print(f"  {x['kind']} {x['aid']} {x.get('at') or x.get('from')} | {x['text'][:110]}")
