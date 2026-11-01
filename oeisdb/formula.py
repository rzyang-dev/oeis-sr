"""OEIS formula parser and exact evaluator.

Grammar (a practical subset of %F lines):

    expr   := term (('+'|'-') term)*
    term   := pow (('*'|'/') pow)*
    pow    := unary ('^' pow)?          (right associative)
    unary  := ('-'|'+')* postfix
    postfix:= atom '!'*
    atom   := NUMBER | IDENT | IDENT '(' args ')'
            | '(' expr ')'
            | 'Sum' '_' '{' spec '}' term
            | 'Product' '_' '{' spec '}' term
    spec   := IDENT '=' expr '..' expr

Evaluation is exact (Fraction), with a context that supplies a(k) and A-numbers.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction


FUNC_MAP = {
    "sigma": "A000203", "tau": "A000005", "phi": "A000010", "mu": "A008683",
    "prime": "A000040", "pi": "A000720", "Omega": "A001222", "omega": "A001221",
    "Fibonacci": "A000045", "Lucas": "A000032", "Catalan": "A000108", "Bell": "A000110",
}


def clean_rhs(rhs: str):
    """Strip attributions, range conditions and trailing notes; return (expr, lo)."""
    s = rhs
    lo = 0
    m = re.search(r"(?:for\s+)?n\s*(>=|>)\s*(\d+)", s)
    if m:
        lo = int(m.group(2)) + (1 if m.group(1) == ">" else 0)
    s = s.strip()
    s = re.sub(r"\s*\.\s*$", "", s)
    s = re.sub(r"\s+-\s+_[^_]+_(\s*,.*)?$", "", s)
    s = re.sub(r"\s*\[[^\[\]]*\]", " ", s)
    s = re.sub(r"(\s*,\s*a\(-?\d+\)\s*=\s*-?\d+)+\s*$", "", s)
    s = re.sub(r"\s+with\s+a\(.*$", "", s, flags=re.I)
    s = re.sub(r",\s*(?:if|where|for|when|with|n\s*[<>])\b.*$", "", s, flags=re.I)
    s = re.sub(r"\s*\((Start|End)\)", "", s, flags=re.I)
    s = re.sub(r"\s*\[[^\[\]]*\]\s*$", "", s)
    s = re.sub(r"\s*,?\s*(?:for\s+)?n\s*[<>]=?\s*\d+.*$", "", s)
    s = re.sub(r"\s*\.\s*$", "", s)
    return s.strip(), lo


class FormulaError(Exception):
    pass


class Unsupported(FormulaError):
    """Well-formed but outside the exact-evaluation subset (log, sin, ...)."""
    pass


def tokenize(s: str):
    toks = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            if j + 1 < n and s[j] == "." and s[j + 1].isdigit():
                k = j + 1
                while k < n and s[k].isdigit():
                    k += 1
                toks.append(("num", Fraction(s[i:k])))
                i = k
            else:
                toks.append(("num", int(s[i:j])))
                i = j
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            word = s[i:j]
            toks.append(("id", word))
            i = j
            continue
        if c in "+-*/^!(),{}.=@|":
            toks.append(("op", c))
            i += 1
            continue
        raise FormulaError("bad char " + repr(c))
    return toks


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, kind, value=None):
        k, v = self.take()
        if k != kind or (value is not None and v != value):
            raise FormulaError("expected " + str(value or kind) + " got " + str((k, v)))
        return v

    def parse(self):
        e = self.expr()
        if self.i != len(self.t):
            raise FormulaError("trailing tokens")
        return e

    def expr(self):
        node = self.term()
        while True:
            k, v = self.peek()
            if k == "op" and v in "+-":
                self.take()
                node = (v, node, self.term())
            else:
                return node

    def term(self):
        node = self.pow()
        while True:
            k, v = self.peek()
            if k == "op" and v in "*/":
                self.take()
                node = (v, node, self.pow())
            elif k == "id" and v == "mod":
                self.take()
                node = ("mod", node, self.pow())
            elif k in ("num", "id") or (k == "op" and v == "("):
                node = ("*", node, self.pow())
            else:
                return node

    def pow(self):
        base = self.unary()
        k, v = self.peek()
        if k == "op" and v == "^":
            self.take()
            return ("^", base, self.pow())
        return base

    def unary(self):
        k, v = self.peek()
        if k == "op" and v in "+-":
            self.take()
            inner = self.unary()
            return inner if v == "+" else ("neg", inner)
        return self.postfix()

    def postfix(self):
        node = self.atom()
        while True:
            k, v = self.peek()
            if k == "op" and v == "!":
                self.take()
                node = ("fact", node)
            else:
                return node

    def atom(self):
        k, v = self.take()
        if k == "num":
            return ("num", v)
        if k == "op" and v == "(":
            e = self.expr()
            self.expect("op", ")")
            return e
        if k == "op" and v == "|":
            e = self.expr()
            self.expect("op", "|")
            return ("absnode", e)
        if k == "id":
            name = v
            base = name.rstrip("_")
            if base in ("Sum", "Product"):
                k2, v2 = self.peek()
                if k2 == "op" and v2 == "_":
                    self.take()
                self.expect("op", "{")
                spec = self.spec()
                self.expect("op", "}")
                body = self.term()
                return (base, spec, body)
            k2, v2 = self.peek()
            is_func = (name in ("binomial", "C", "binom", "floor", "ceil", "ceiling", "round", "abs",
                                "sqrt", "gcd", "a", "log", "ln", "sin", "cos", "tan", "cot", "exp",
                                "zeta", "gamma", "Gamma", "BesselJ", "hypergeometric", "LambertW",
                                "multinomial", "Stirling1", "Stirling2", "eulerian")
                       or name in FUNC_MAP
                       or (name.startswith("A") and name[1:].isdigit() and len(name) == 7))
            if k2 == "op" and v2 == "(" and not is_func:
                depth = 0
                j = self.i
                while j < len(self.t):
                    kk, vv = self.t[j]
                    if kk == "op" and vv == "(":
                        depth += 1
                    elif kk == "op" and vv == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    elif kk == "op" and vv == "," and depth == 1:
                        is_func = True
                    j += 1
            if k2 == "op" and v2 == "(" and is_func:
                self.take()
                args = [self.expr()]
                while True:
                    k3, v3 = self.peek()
                    if k3 == "op" and v3 == ",":
                        self.take()
                        args.append(self.expr())
                    else:
                        break
                self.expect("op", ")")
                return ("call", name, args)
            return ("var", name)
        raise FormulaError("unexpected token " + str((k, v)))

    def spec(self):
        var = self.expect("id")
        k2, v2 = self.peek()
        if k2 == "op" and v2 == "|":
            self.take()
            cond = self.expr()
            return ("div", var, cond)
        self.expect("op", "=")
        lo = self.expr()
        self.expect("op", ".")
        self.expect("op", ".")
        hi = self.expr()
        return (var, lo, hi)


def parse(s: str):
    return Parser(tokenize(s)).parse()


_COND = re.compile(r"^\s*n\s*(<=|>=|<|>|==|!=)\s*(-?\d+)\s*$")


def _split_clauses(s):
    parts, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            parts.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def parse_piecewise(text):
    """Return ('piece', [(ast, cond_or_None), ...]) or None."""
    clauses = _split_clauses(text)
    if len(clauses) < 2:
        return None
    parsed = []
    for cl in clauses:
        m = re.match(r"^(.*?),\s*if\s+(.+)$", cl, re.I)
        if m:
            expr, cond = m.group(1), m.group(2)
            cm = _COND.match(cond)
            if not cm:
                return None
            cond = (cm.group(1), int(cm.group(2)))
        else:
            expr, cond = cl, None
        expr = re.sub(r"\s*,\s*otherwise\s*$", "", expr, flags=re.I)
        expr = re.sub(r"^\s*a\([^)]*\)\s*=\s*", "", expr)
        try:
            parsed.append((parse(expr), cond))
        except FormulaError:
            return None
    return ("piece", parsed)


def check_cond(cond, n):
    op, k = cond
    if op == "<=":
        return n <= k
    if op == ">=":
        return n >= k
    if op == "<":
        return n < k
    if op == ">":
        return n > k
    if op == "==":
        return n == k
    return n != k


def parse_full(text):
    pw = parse_piecewise(text)
    if pw is not None:
        return pw
    return parse(text)


def _int(x):
    if isinstance(x, Fraction):
        if x.denominator != 1:
            raise FormulaError("non-integer")
        return x.numerator
    return int(x)


def ev(node, env):
    op = node[0]
    if op == "piece":
        n = env.get("n")
        for ast, cond in node[1]:
            if cond is None or (n is not None and check_cond(cond, n)):
                return ev(ast, env)
        raise FormulaError("no piece matches")
    if op == "num":
        return Fraction(node[1])
    if op == "var":
        name = node[1]
        if name in env:
            return env[name]
        if name in ("Pi", "pi", "e", "i", "I", "if", "for", "iff", "then", "else", "floor"):
            raise Unsupported("symbol " + name)
        raise FormulaError("unbound " + name)
    if op == "absnode":
        return abs(ev(node[1], env))
    if op == "neg":
        return -ev(node[1], env)
    if op == "fact":
        return Fraction(math.factorial(_int(ev(node[1], env))))
    if op == "^":
        b = ev(node[1], env)
        e = _int(ev(node[2], env))
        if abs(e) > 5000:
            raise FormulaError("exponent too large")
        if abs(b.numerator) > 1 and abs(e) * abs(b.numerator).bit_length() > 200000:
            raise FormulaError("power too large")
        if e >= 0:
            return b ** e
        return Fraction(1, 1) / (b ** (-e))
    if op == "mod":
        a, b = ev(node[1], env), ev(node[2], env)
        return a - b * Fraction(math.floor(a / b))
    if op in "+-*/":
        a, b = ev(node[1], env), ev(node[2], env)
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            r = a * b
            if abs(r.numerator).bit_length() > 200000:
                raise FormulaError("product too large")
            return r
        if b == 0:
            raise FormulaError("division by zero")
        return a / b
    if op in ("Sum", "Product"):
        spec = node[1]
        body = node[2]
        if isinstance(spec, tuple) and spec and spec[0] == "div":
            _, dvar, cond = spec
            nval = _int(ev(cond, env))
            if nval <= 0:
                raise FormulaError("divisor sum of non-positive")
            divs = []
            i = 1
            while i * i <= nval:
                if nval % i == 0:
                    divs.append(i)
                    if i != nval // i:
                        divs.append(nval // i)
                i += 1
            acc = Fraction(0) if op == "Sum" else Fraction(1)
            for dv in sorted(divs):
                env[dvar] = Fraction(dv)
                v = ev(body, env)
                acc = acc + v if op == "Sum" else acc * v
            env.pop(dvar, None)
            return acc
        (var, lo, hi) = spec
        a, b = _int(ev(lo, env)), _int(ev(hi, env))
        if b - a > 2000:
            raise FormulaError("range too large")
        acc = Fraction(0) if op == "Sum" else Fraction(1)
        for k in range(a, b + 1):
            env[var] = Fraction(k)
            v = ev(body, env)
            acc = acc + v if op == "Sum" else acc * v
        env.pop(var, None)
        return acc
    if op == "call":
        name, args = node[1], node[2]
        vals = [ev(x, env) for x in args]
        if name in ("binomial", "C", "binom"):
            return Fraction(math.comb(_int(vals[0]), _int(vals[1])))
        if name == "floor":
            return Fraction(math.floor(vals[0]))
        if name == "ceil" or name == "ceiling":
            return Fraction(math.ceil(vals[0]))
        if name == "round":
            return Fraction(math.floor(vals[0] + Fraction(1, 2)))
        if name == "abs":
            return abs(vals[0])
        if name == "sqrt":
            q = _int(vals[0])
            r = math.isqrt(q) if q >= 0 else -1
            if r * r != q:
                raise FormulaError("non-square sqrt")
            return Fraction(r)
        if name == "gcd":
            g = 0
            for v in vals:
                g = math.gcd(g, _int(v))
            return Fraction(g)
        if name.startswith("A") and name[1:].isdigit() and len(name) == 7:
            if len(vals) == 1:
                return env["__seq__"](name, _int(vals[0]))
            if len(vals) == 2 and "__tri__" in env:
                return env["__tri__"](name, _int(vals[0]), _int(vals[1]))
            raise Unsupported("multi-index " + name)
        if name == "a":
            if len(vals) != 1:
                raise Unsupported("multi-index a")
            return env["__self__"](_int(vals[0]))
        if name in FUNC_MAP:
            return env["__seq__"](FUNC_MAP[name], _int(vals[0]))
        if name in ("log", "ln", "sin", "cos", "tan", "cot", "exp", "zeta",
                    "gamma", "Gamma", "BesselJ", "hypergeometric", "LambertW"):
            raise Unsupported("transcendental " + name)
        raise Unsupported("unknown function " + name)
    raise FormulaError("bad node " + op)