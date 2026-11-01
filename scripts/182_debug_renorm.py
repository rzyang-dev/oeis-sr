import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 400
W = 2*B+1
def step(s):
    n = len(s); new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        r = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == r) else 0
    return new
X = []
s = [0]*W; s[B] = 1
for t in range(200):
    X.append(s[:])
    s = step(s)
def x(t,j):
    if abs(j) > t: return 1 if t >= 1 else 0
    return X[t][B+j]
def e(t,j): return 1 if x(t,j) != x(t,j+1) else 0
# print e(2m,·) and x(m,·) for m=3
m = 3
print("m=3: x(m,·) for i=-4..4:", [x(m,i) for i in range(-4,5)])
print("e(6,·) for j=-8..8:", [e(6,j) for j in range(-8,9)])
print("1-x(3,·) for i=-4..4:", [1-x(m,i) for i in range(-4,5)])
print()
m = 5
print("m=5: x(m,i):", [x(m,i) for i in range(-6,7)])
print("e(10,j):", [e(10,j) for j in range(-12,13)])
print()
m = 2
print("m=2: x(2,i):", [x(2,i) for i in range(-3,4)])
print("e(4,j):", [e(4,j) for j in range(-6,7)])
