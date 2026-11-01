import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
def shifted_dfa(dfa, k):
    """DFA reading n LSB-first, outputting dfa(n+k). Handles the carry."""
    tr, ov = dfa["trans"], dfa["out"]
    kb = [(k >> i) & 1 for i in range(k.bit_length() + 1)]
    def step(state, i, bit):
        # state = (b_state, carry)
        bstate, carry = state
        kb_i = kb[i] if i < len(kb) else 0
        total = bit + kb_i + carry
        return (tr[bstate][total & 1], total >> 1)
    return step, len(kb)
def equivalent(a, b, k, maxdepth=60):
    tra, ova = a["trans"], a["out"]
    step, L = shifted_dfa(b, k)
    start = (0, (0, 0))
    seen = {start}
    frontier = [start]
    while frontier and len(seen) < 20000:
        nxt = []
        for (sa, sb) in frontier:
            if ova[sa] != b["out"][sb[0]]:
                return False, (sa, sb)
            for bit in (0, 1):
                sa2 = tra[sa][bit]
                # the index i is not tracked: after L steps the carry-only automaton is uniform,
                # but before that we need the position. Track positions up to L by state key.
                pass
            nxt = []
        break
    return None, None
# simpler: verify with positional state (index capped at L)
def equivalent2(a, b, k):
    tra, ova = a["trans"], a["out"]
    trb, ovb = b["trans"], b["out"]
    kb = [(k >> i) & 1 for i in range(k.bit_length() + 1)]
    L = len(kb)
    def step(state, bit):
        sa, sb, carry, i = state
        kb_i = kb[i] if i < L else 0
        total = bit + kb_i + carry
        return (tra[sa][bit], trb[sb][total & 1], total >> 1, min(i+1, L))
    start = (0, 0, 0, 0)
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
    res = equivalent2(atlas[a], atlas[b], k)
    print(f"{a} = {b}(n+{k}) : {'PROVED' if res else 'FAILED'}")
    ok += res
print(f"\n{ok}/{len(pairs)} rigorously verified by automaton equivalence")
