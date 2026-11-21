"""CHECK 4 (CI): with g := M^{-1}(R^a + pi' Gamma^0 Gamma^a R^0) and Ktilde := d_t Phi - g:
 (a) Ktilde contains no time derivative;
 (b) R^0[g] - star R^0[psi] + S^rho psi_rho = 0 for ARBITRARY independent psi_0, Phi and SYMBOLIC m, lam, b1, b2, pi'.
Setting psi_0 = W Phi (det S^0 != 0) kills S^rho psi_rho and gives R^0 (d_t - K') = star R^0."""
import sympy as sp
from bhmap_defs import symbolic_model, generic_psi, R5, SP, zeros, Matrix, vanishes_on_chart, report
M = symbolic_model(); psi = generic_psi(); R = M.R(psi); g = M.g_of(R)
from bhmap_defs import t
Kt = Matrix.vstack(*[psi[k].diff(t) for k in SP]) - g
print("Ktilde free of d/dt:", all(not sp.expand(x).has(sp.Derivative(psi[r][c], t)) for x in Kt for r in R5 for c in range(4)))
gpsi = [zeros(4, 1)] + [g[4*(k-1):4*k, 0] for k in SP]
res = M.R(gpsi)[0] - M.star(R[0]) + sum((M.S[r]*psi[r] for r in R5), zeros(4, 1))
print("CI (arbitrary psi_0, Phi; symbolic parameters):", all(vanishes_on_chart(x) for x in res))
report()
