"""CHECK 5: at the witness, the principal symbol of the curved eliminated operator K' (psi_0 = W Phi) at y0 equals
i * Psym(xi*), with Psym exactly as in witness_min.py. Plane wave Phi = c exp(i Lam k.y), c in C^16 symbolic,
k = E(y0)^{-T} xi* = (20/99, 0, 3, 0)."""
import sympy as sp
from sympy import I, Rational as Q, Matrix
from bhmap_defs import witness_model, SP, zeros, th1, ph1, th2, ph2, no_float
W = witness_model(); Lam = sp.Symbol('Lam', real=True)
S0i = W.S[0].inv(); Wm = [-S0i*W.S[k] for k in SP]
cs = sp.symbols('c0:16'); kk = [Q(20, 99), 0, 3, 0]
ph = sp.exp(I*Lam*(kk[0]*th1+kk[1]*ph1+kk[2]*th2+kk[3]*ph2))
Phi = [Matrix(cs[4*j:4*j+4])*ph for j in range(4)]
psi = [sum((Wm[k-1]*Phi[k-1] for k in SP), zeros(4, 1))] + Phi
Kp = (-W.g_of(W.R(psi))/ph).applyfunc(sp.expand)       # K'Phi / phase (Phi static: K'Phi = -g)
y0 = {th1: sp.pi/2, ph1: 0, th2: sp.pi/2, ph2: 0}
lead = Kp.applyfunc(lambda x: x.coeff(Lam, 1).subs(y0))
P = W.Psym([Q(20, 99), 0, 1, 0])
print("no Float atoms:", no_float(lead, P))
print("degree in Lam <= 1:", all(sp.degree(x, Lam) <= 1 for x in Kp))
print("principal symbol of curved K' at y0 == i P(xi*):", all(sp.expand(x) == 0 for x in (lead - I*P*Matrix(cs))))
