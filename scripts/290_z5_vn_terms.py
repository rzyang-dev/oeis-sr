def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def c5vn(d):
    return 1 if d == 0 else (4 * d ** 4 + 20 * d * d + 6) // 3

print("Z^5 von Neumann zeros t=1..12:", [sum(c5vn(d) for d in shell(t)) for t in range(1, 13)])
