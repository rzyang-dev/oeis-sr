import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
def verify(a, b, k):
    """Check a(n) == b(n+k) for all n, via product BFS of DFAs."""
    tra, ova = a["trans"], a["out"]
    trb, ovb = b["trans"], b["out"]
    kb = [(k >> i) & 1 for i in range(k.bit_length())] or [0]
    L = len(kb)
    sb0 = 0
    for i in range(L):
        sb0 = trb[sb0][kb[i]]
    def step(state, bit):
        sa, sb, carry, i = state
        kb_i = kb[i] if i < L else 0
        total = bit + kb_i + carry
        return (tra[sa][bit], trb[sb][total & 1], total >> 1, min(i+1, L))
    start = (0, sb0, 0, L)
    seen = {start}; frontier = [start]
    while frontier:
        nxt = []
        for st in frontier:
            sa, sb, c, i = st
            if ova[sa] != ovb[sb]:
                return False
            for bit in (0, 1):
                s2 = step(st, bit)
                if s2 not in seen:
                    seen.add(s2); nxt.append(s2)
        frontier = nxt
    return True
pairs = [("A014707","A038189",1),("A030301","A275973",1),("A034947","A112347",1),
         ("A035263","A285383",1),("A035263","A285384",1),("A036577","A316826",1),
         ("A036987","A209229",1),("A036987","A255738",1),("A039982","A306559",4),
         ("A043545","A347523",1),("A092436","A010059",1),("A096268","A284948",1),
         ("A267442","A267579",1)]
ok = 0
for a, b, k in pairs:
    res = verify(atlas[a], atlas[b], k)
    print(f"{a}(n) = {b}(n+{k}) : {'PROVED' if res else 'FAILED'}")
    ok += res
print(f"\n{ok}/{len(pairs)} rigorously verified by DFA product")
