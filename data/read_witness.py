"""Verify the BHMAP witness relations from data/witness.json using ONLY the Python standard library (fractions).
No sympy, no numpy: an independent check of the published certificate.   Usage:  python read_witness.py"""
import json, os
from fractions import Fraction as F

D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "witness.json"), encoding="utf-8"))
c = lambda e: (F(e[0]), F(e[1]))                                      # [re, im] → Gaussian rational
mul = lambda a, b: (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])
add = lambda a, b: (a[0] + b[0], a[1] + b[1])
def mv(M, x):
    out = []
    for row in M:
        s = (F(0), F(0))
        for a, b in zip(row, x): s = add(s, mul(a, b))
        out.append(s)
    return out
zero = lambda x: all(a == 0 and b == 0 for a, b in x)

P = [[c(e) for e in row] for row in D["P_xi_star"]]; L = [[c(e) for e in row] for row in D["L_xi_star"]]
v = [c(e) for e in D["v"]]; w = [c(e) for e in D["w"]]; r = F(D["r"])
N = [[(P[i][j][0] - (r if i == j else 0), P[i][j][1]) for j in range(16)] for i in range(16)]
checks = {"L v = 0": zero(mv(L, v)), "L w = 0": zero(mv(L, w)), "(P - r) v = 0": zero(mv(N, v)),
          "(P - r) w = v": mv(N, w) == v, "v != 0": not zero(v)}
for k, ok in checks.items(): print(f"{k:14s} {ok}")
print("ALL WITNESS RELATIONS HOLD" if all(checks.values()) else "A RELATION FAILED")
