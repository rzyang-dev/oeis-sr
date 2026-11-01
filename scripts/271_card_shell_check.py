"""271_card_shell_check.py -- check the Lean statement

    #(shell t) = 2 * #(subm (r t))

where shell t = {d <= t : (t-d)/2 is a submask of r t} and
subm r = {m <= r : m is a submask of r}, against 2^popcount.
"""
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def shell(t):
    r = r_of(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & r == ((t - d) // 2)]

def subm(r):
    return [m for m in range(r + 1) if (m & r) == m]

bad = 0
for t in range(1, 2001):
    r = r_of(t)
    if len(shell(t)) != 2 * len(subm(r)):
        bad += 1
        if bad <= 3:
            print("mismatch t=%d shell=%d subm=%d" % (t, len(shell(t)), len(subm(r))))
    if len(subm(r)) != 2 ** bin(r).count("1"):
        bad += 1
print("t<=2000: %d mismatches" % bad)
print("first values of 2*#subm: " + ",".join(str(2 * len(subm(r_of(t)))) for t in range(1, 17)))
