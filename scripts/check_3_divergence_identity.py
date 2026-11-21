"""CHECK 3 (DI): (D+Yhat)_A R^A[psi] = S^rho psi_rho on Model E, for ARBITRARY component functions psi (20 undefined
functions of (t,y)) and SYMBOLIC m, lam, b1, b2. Exact; zero test on the chart V' (see bhmap_defs.vanishes_on_chart)."""
import sympy as sp
from bhmap_defs import symbolic_model, generic_psi, R5, zeros, vanishes_on_chart, no_float, report
M = symbolic_model(); psi = generic_psi(); R = M.R(psi)
res = M.div(R) - sum((M.S[r]*psi[r] for r in R5), zeros(4, 1))
print("no Float atoms:", no_float(*M.S, *M.X, *M.Y, *M.Om))
print("DI on Model E (arbitrary psi, symbolic parameters):", all(vanishes_on_chart(x) for x in res))
report()
