import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A306559"]
def shiftd(trans, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return trans(s // 2, t % 2) * 2 + (t // 2)
def shiftout(trans, out, s):
    return out(trans(s // 2, True)) if s % 2 == 1 else out(s // 2)
def fold(f, s, n):
    while n:
        s = f(s, n % 2 == 1)
        n //= 2
    return s
# level 0: A itself
t0 = lambda b, d: A["trans"][b][1 if d else 0]
o0 = lambda b: A["out"][b]
print("A values:", [o0(fold(t0, 0, n)) for n in range(12)])
# level 1
t1 = lambda s, d: shiftd(t0, s, d)
o1 = lambda s: shiftout(t0, o0, s)
s1 = t0(0, True) * 2 + 1
print("shift1:", [o1(fold(t1, s1, n)) for n in range(12)])
# level 2
t2 = lambda s, d: shiftd(t1, s, d)
o2 = lambda s: shiftout(t1, o1, s)
s2 = t1(s1, True) * 2 + 1
print("shift2:", [o2(fold(t2, s2, n)) for n in range(12)])
t3 = lambda s, d: shiftd(t2, s, d)
o3 = lambda s: shiftout(t2, o2, s)
s3 = t2(s2, True) * 2 + 1
print("shift3:", [o3(fold(t3, s3, n)) for n in range(12)])
t4 = lambda s, d: shiftd(t3, s, d)
o4 = lambda s: shiftout(t3, o3, s)
s4 = t3(s3, True) * 2 + 1
print("shift4:", [o4(fold(t4, s4, n)) for n in range(12)])
