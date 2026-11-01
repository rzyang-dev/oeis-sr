import sys
sys.stdout.reconfigure(encoding="utf-8")
# rule 129: new = 1 iff (l,c,r) all equal
def step(state, width):
    # state: dict pos -> 0/1 on [-width, width]; outside = 0 (background)
    new = {}
    for j in range(-width, width + 1):
        l = state.get(j - 1, 0); c = state.get(j, 0); r = state.get(j + 1, 0)
        new[j] = 1 if (l == c == r) else 0
    return new
# infinite grid: start with single 1 at 0, evolve on a growing window (cells outside = 0)
state = {0: 1}
rows = []
W = 0
mid = []
for t in range(16):
    mid.append(state.get(0, 0))
    rows.append({k: v for k, v in state.items() if v == 0})
    W += 1
    state = step(state, W + 2)
print("middle:", mid)
for t in range(10):
    z = sorted(rows[t].keys())
    print(f"t={t} zeros at: {z}")
