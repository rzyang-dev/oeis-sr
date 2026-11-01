import sys
sys.stdout.reconfigure(encoding="utf-8")
W = 20
mask = (1 << (2*W+1)) - 1
a = 1 << W
for t in range(1, 5):
    L = (a << 1) & mask; R = a >> 1
    a = ((L & a & R) | (~(L | a | R) & mask)) & mask
    z = (~a) & mask
    win = ((1 << (2*t+1)) - 1) << (W - t)
    print("t=", t, "zeros at", [j for j in range(-W, W+1) if (z >> (j+W)) & 1],
          "outside:", [j for j in range(-W, W+1) if (z >> (j+W)) & 1 and abs(j) > t],
          "z&~win =", z & ~win, " win =", bin(win))
