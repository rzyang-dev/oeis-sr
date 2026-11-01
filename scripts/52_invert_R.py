import sys, itertools
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
hits = defaultdict(set)
for aid, r in con.execute("select aid, r from congruence2 where p=5 and m=5"):
    hits[aid].add(r)
print("sequences with a mod-5 zero class:", len(hits))
P = 5
def sumsets(R, maxr):
    out = [set() for _ in range(maxr + 1)]
    out[0] = {0}
    for r in range(1, maxr + 1):
        out[r] = {(x + y) % P for x in out[r - 1] for y in R}
    return out
zmap = defaultdict(list)
for k in range(1, P + 1):
    for R in itertools.combinations(range(P), k):
        S = sumsets(set(R), P - 1)
        Z = frozenset(r for r in range(1, P) if r not in S[r])
        zmap[Z].append(R)
print("distinct predicted zero-patterns:", len(zmap))
match = Counter()
no_match = 0
for aid, zs in hits.items():
    z = frozenset(zs)
    if z in zmap:
        match[z] += 1
    else:
        no_match += 1
print("matched:", sum(match.values()), " no match:", no_match)
print("\ntop patterns:")
for z, n in match.most_common(12):
    print(f"  Z={sorted(z)} : {n} seqs  R candidates={zmap[z][:3]}")
