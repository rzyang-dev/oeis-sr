"""Routed solving: predict whether a target is worth attempting, and in what order.

The model is trained by scripts/34_failure_prediction.py and stored in
reports/model.json.  Conditional method priors are estimated from hard_solved.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "reports" / "model.json"

_MODEL = None


def load_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        _MODEL["mu"] = [float(x) for x in _MODEL["mu"]]
        _MODEL["sd"] = [float(x) for x in _MODEL["sd"]]
        _MODEL["w"] = [float(x) for x in _MODEL["w"]]
        _MODEL["b"] = float(_MODEL["b"])
    return _MODEL


def features(growth: str, category: str, degree: float, log2_base: float,
             periodic: int, n_terms: int, zeros: int, signs: int, digits: int):
    m = load_model()
    x = [1.0 if growth == g else 0.0 for g in m["growth"]]
    x += [1.0 if category == c else 0.0 for c in m["constr"]]
    x.append(min(max(degree or 0.0, -5.0), 20.0) / 10.0)
    x.append(min(max(log2_base or 0.0, -5.0), 30.0) / 10.0)
    x.append(1.0 if (periodic or 0) > 0 else 0.0)
    x.append(math.log1p(n_terms or 0) / 5.0)
    x.append(1.0 if (zeros or 0) > 0 else 0.0)
    x.append(1.0 if (signs or 0) > 0 else 0.0)
    x.append(math.log1p(digits or 0) / 5.0)
    return x


def predict(**kw) -> float:
    m = load_model()
    x = features(**kw)
    z = m["b"]
    for xi, mu, sd, w in zip(x, m["mu"], m["sd"], m["w"]):
        z += w * (xi - mu) / sd
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


def conditional_orders(con, min_n: int = 20):
    """P(method | growth, construction) estimated from hard_solved."""
    rows = con.execute("""select s.aid, s.method, f.growth, c.category from hard_solved s
        left join seq_fingerprint f on f.aid = s.aid
        left join construction c on c.aid = s.aid where s.method <> ''""").fetchall()
    glob = Counter(m for _, m, _, _ in rows)
    bucket = defaultdict(Counter)
    for aid, m, g, c in rows:
        if int(aid[1:]) % 10 < 7:          # train split only
            bucket[(g, c)][m] += 1
    global_order = [m for m, _ in glob.most_common()]

    def order_for(growth, category):
        cnt = bucket.get((growth, category))
        if cnt and sum(cnt.values()) >= min_n:
            return sorted(cnt, key=lambda m: (-cnt[m], -glob[m]))
        return global_order

    return order_for, global_order

def fingerprint(v):
    """Cheap structural fingerprint from a term list."""
    import math
    n = len(v)
    if n < 10:
        return None
    nz = [(i, abs(x)) for i, x in enumerate(v) if x != 0]
    zeros = n - len(nz)
    signs = sum(1 for i in range(1, n) if (v[i] > 0) != (v[i-1] > 0) and v[i] and v[i-1])
    digits = max(len(str(abs(x))) for x in v)
    if len(nz) < 8:
        return {"growth": "zero", "degree": 0.0, "log2_base": 0.0, "periodic": 0,
                "zeros": zeros, "sign_changes": signs, "digits": digits}
    tail = nz[-60:]
    xs = [math.log(i + 2) for i, _ in tail]
    ys = [math.log(a) for _, a in tail]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs) or 1.0
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    lr = [math.log2(tail[k + 1][1]) - math.log2(tail[k][1])
          for k in range(len(tail) - 20, len(tail) - 1) if 0 <= k < len(tail) - 1]
    lr_mean = sum(lr) / len(lr) if lr else 0.0
    lr_last = lr[-1] if lr else 0.0
    growth = "other"
    if lr and abs(lr_last) < 0.05 and abs(slope) < 20:
        growth = "polynomial"
    elif lr and 0.05 <= lr_mean < 20 and abs(lr_last - lr_mean) < 0.5:
        growth = "exponential"
    elif lr and lr_last > math.log2(max(2, n)) * 0.5:
        growth = "factorial"
    elif lr and lr_mean >= 20:
        growth = "super"
    per = 0
    m = min(120, n)
    seg = v[-m:]
    for p in range(1, 13):
        if all(seg[i] == seg[i - p] for i in range(p, len(seg))):
            per = p
            break
    return {"growth": growth, "degree": round(slope, 2), "log2_base": round(lr_mean, 3),
            "periodic": per, "zeros": zeros, "sign_changes": signs, "digits": digits}
