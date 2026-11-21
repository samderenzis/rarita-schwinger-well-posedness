"""Exact checks behind the three NEW observations in OUTLOOK.md (2026-11-21).

These are not part of the frozen proof and have not been externally audited.
Requires sympy only. Uses the frozen definitions in witness_min.py (same folder).
Runtime: a few seconds.

  1. Characteristic speeds along each sphere: the "G-sheet" is faster than light along S^2(3)
     and slower than light along S^2(1); exact values from the factored characteristic polynomial.
  2. The faster-than-light eigenspace lies entirely inside ker L (constraint-satisfying modes).
  3. The crossing condition (v1^2 - 1)|xi_a|^2 + (v3^2 - 1)|xi_b|^2 = 0 holds exactly at xi*.
  4. P restricted to ker L(xi*), and the Jordan chain, do not depend on the constraint-addition parameter pi'.
"""
import contextlib, io, os, runpy
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(os.path.join(HERE, "witness_min.py"))
Psym, Lsym, v, w = ns["Psym"], ns["Lsym"], ns["v"], ns["w"]
Q, x = sp.Rational, sp.Symbol("x")


def real_charpoly_factors(P):
    """Factor the characteristic polynomial of the 32x32 real representation (roots doubled)."""
    Re = P.applyfunc(lambda z: sp.re(sp.expand(z)))
    Im = P.applyfunc(lambda z: sp.im(sp.expand(z)))
    R = sp.BlockMatrix([[Re, -Im], [Im, Re]]).as_explicit()
    return sp.factor_list(R.charpoly(x).as_expr())[1]


ok = True
print("1. Characteristic speeds (|xi| = 1, frame components; light speed = 1)")
speeds_sq = {}
for name, xi in [("e1, along S^2(1)", [1, 0, 0, 0]), ("e3, along S^2(3)", [0, 0, 1, 0])]:
    facs = real_charpoly_factors(Psym(xi))
    quad = [f for f, _ in facs if sp.degree(f, x) == 2]
    lin = sorted({sp.solve(f, x)[0] for f, _ in facs if sp.degree(f, x) == 1})
    vsq = sp.solve(quad[0], x)[1] ** 2
    speeds_sq[name] = vsq
    print(f"   {name}: speeds ±{lin[-1]}, ±{lin[-2]}, ±sqrt({vsq}) = ±{sp.sqrt(vsq).evalf(8)}")
v1sq, v3sq = speeds_sq["e1, along S^2(1)"], speeds_sq["e3, along S^2(3)"]
print(f"   v1^2 - 1 = {v1sq - 1} (< 0, slower than light)   v3^2 - 1 = {v3sq - 1} (> 0, faster than light)")
ok &= (v1sq < 1) and (v3sq > 1)

print("2. Faster-than-light eigenspace inside the constraint kernel (along e3)")
P3, L3 = Psym([0, 0, 1, 0]), Lsym([0, 0, 1, 0])
E = sp.Matrix.hstack(*(P3 * P3 - v3sq * sp.eye(16)).nullspace())
inside = (L3 * E).applyfunc(sp.expand).rank() == 0
print(f"   dim eigenspace for speeds ±sqrt(v3^2): {E.shape[1]};  L annihilates all of it: {inside}")
ok &= inside

print("3. Crossing condition at xi* = (20/99, 0, 1, 0)")
cross = (v1sq - 1) * Q(20, 99) ** 2 + (v3sq - 1) * 1
print(f"   (v1^2 - 1)(20/99)^2 + (v3^2 - 1) = {cross}")
ok &= cross == 0

print("4. Independence of the constraint-addition parameter pi'")
xs, r = [Q(20, 99), 0, 1, 0], Q(101, 99)
K = sp.Matrix.hstack(*Lsym(xs).nullspace())
base = None
for p in [Q(0), Q(1, 2), Q(2), Q(-3, 7)]:
    Psym.__globals__["pip"] = p          # pi' is read from the frozen module's namespace
    P = Psym(xs)
    PK = (P * K).applyfunc(sp.expand)
    base = PK if base is None else base
    N = P - r * sp.eye(16)
    chain = (N * v).applyfunc(sp.expand) == sp.zeros(16, 1) and (N * w - v).applyfunc(sp.expand) == sp.zeros(16, 1)
    same = (PK - base).applyfunc(sp.expand) == sp.zeros(16, K.shape[1])
    print(f"   pi' = {p}: P on ker L unchanged: {same}; Jordan chain (P-r)v=0, (P-r)w=v holds: {chain}")
    ok &= same and chain
Psym.__globals__["pip"] = Q(1, 2)

print("ALL OUTLOOK CHECKS HOLD" if ok else "SOME OUTLOOK CHECK FAILED")
