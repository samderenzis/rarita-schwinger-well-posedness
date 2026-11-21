"""CHECK 1: Clifford relations; intertwining Yhat_mu Gamma^{mu nu rho} = Gamma^{mu nu rho} X_mu for a GENERAL 2-form F
(10 independent symbols) and symbolic m, lam. Exact polynomial identity."""
import sympy as sp
from sympy import Rational as Q, sqrt, I, zeros
from bhmap_defs import G, eta, Z, E4, R5, g3
print("Clifford {G^A,G^B} = 2 eta^{AB}:", all(G[a]*G[b]+G[b]*G[a] == 2*(eta[a] if a == b else 0)*E4 for a in R5 for b in R5))
m, lam = sp.symbols('m lam', positive=True); c1 = I*sqrt(Q(3, 128)); fs = sp.symbols('f0:10')
F = zeros(5, 5); k = 0
for a in R5:
    for b in R5:
        if a < b: F[a, b] = fs[k]; F[b, a] = -fs[k]; k += 1
Fs = sum((F[a, b]*G[a]*G[b] for a in R5 for b in R5), Z); Gl = [eta[a]*G[a] for a in R5]
X = [-(m/3)*Gl[a]+lam*c1*(Fs*Gl[a]-Gl[a]*Fs/3) for a in R5]; Y = [-(m/3)*Gl[a]+lam*c1*(Gl[a]*Fs-Fs*Gl[a]/3) for a in R5]
print("intertwining (general F, symbolic m, lam):",
      all(sum((Y[u]*g3(u, n, r)-g3(u, n, r)*X[u] for u in R5), Z).applyfunc(sp.expand) == Z for n in R5 for r in R5))
