# Quarter-plane Moore geometry (3x3 truncated at the axes).
#   #zeros in {0..t}^2 = sum_{d in shell t} (2d+1) = 4 * #subm(r t) * (t - r t).
# Rule: x_{t+1}(v) = 1 iff x_t(v) = x_t(w) for every w in nbhd(v).
def r(t):
    return t - (1 << (t.bit_length() - 1)) if t else 0
def subc(n):
    return 1 << bin(n).count('1')
def nmax(a, b):
    return b if a <= b else a
def qnb(p):
    return {(max(p[0]+k1-1,0), max(p[1]+k2-1,0)) for k1 in range(3) for k2 in range(3)}
T = 90
cur = {(a,b): (1 if nmax(a,b)==0 else 0) for a in range(T+1) for b in range(T+1)}
states = [dict(cur)]
for t in range(1, T+1):
    prev = cur
    cur = {}
    for a in range(T+1):
        for b in range(T+1):
            me = prev.get((a,b), 1)
            cur[(a,b)] = 1 if all(prev.get(q,1)==me for q in qnb((a,b))) else 0
    states.append(cur)
bad = 0
for t in range(1, 30):
    z = sum(1 for a in range(t+1) for b in range(t+1) if states[t][(a,b)]==0)
    lv = sum(2*d+1 for d in range(t+1) if ((t-d)//2)&r(t)==(t-d)//2)
    cl = 4*subc(r(t))*(t-r(t))
    if not (z==lv==cl):
        bad += 1
        print('MISMATCH', t, z, lv, cl)
print('t=1..29 checked, mismatches =', bad)
for t in [1,2,3,4,7,8,15,16,29]:
    z = sum(1 for a in range(t+1) for b in range(t+1) if states[t][(a,b)]==0)
    print('  t=', t, ' zeros=', z, ' closed=', 4*subc(r(t))*(t-r(t)))
