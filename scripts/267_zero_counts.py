"""267_zero_counts.py -- the number of zeros of the all-equal rule.

The universal theorem says the zero set is a union of complete level shells,
    S(t) = { d : 0 <= d <= t, floor((t-d)/2) is a submask of r(t) }.
Hence the zero count in ANY geometry is
    N(t) = sum_{d in S(t)} c_d ,
and for the three verified geometries c_d = 1 (d=0), c*d (d>=1) with
c = 2 (1D), 4 (von Neumann) and 8 (Moore).  So every count is

    N(t) = c * sigma(t) + eps(t),   sigma(t)=sum_{d in S, d>=1} d,  eps=[0 in S].

Two universal integer sequences control all geometries.
"""
def rmask(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def S(t):
    r = rmask(t)
    return [d for d in range(t + 1) if (((t - d) // 2) & r) == ((t - d) // 2)]

T = 40
sigma, eps = [], []
for t in range(1, T + 1):
    s = S(t)
    sigma.append(sum(d for d in s if d >= 1))
    eps.append(1 if 0 in s else 0)

z1 = [2 * a + b for a, b in zip(sigma, eps)]
zv = [4 * a + b for a, b in zip(sigma, eps)]
zm = [8 * a + b for a, b in zip(sigma, eps)]

def show(name, seq):
    print(name)
    print("  " + ", ".join(str(x) for x in seq))

print("t from 1 to %d" % T)
show("sigma (sum of the positive zero shells)", sigma)
show("eps   (is shell 0 zero?)", eps)
show("#zeros 1D (c=2)", z1)
show("#zeros Z^2 von Neumann (c=4)", zv)
show("#zeros Z^2 Moore (c=8)", zm)
print()
print("sigma first 24: " + ",".join(str(x) for x in sigma[:24]))
print("eps   first 24: " + ",".join(str(x) for x in eps[:24]))
print("moore first 24: " + ",".join(str(x) for x in zm[:24]))
print("vN    first 24: " + ",".join(str(x) for x in zv[:24]))
print("1D    first 24: " + ",".join(str(x) for x in z1[:24]))
