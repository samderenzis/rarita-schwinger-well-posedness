"""CHECK 2: Model E frame data. Levi-Civita (torsion-free on all frame commutators; omega_AB antisymmetric);
spin connection convention [Omega_C, Gamma^A] = -omega^A_B(e_C) Gamma^B; dA = F; S^rho constant in Q(i) at the witness."""
import sympy as sp
from bhmap_defs import symbolic_model, witness_model, COORDS, G, eta, Z, R5, vanishes_on_chart, no_float, report
M = symbolic_model(); f = sp.Function('f')(*COORDS)
lc = all(vanishes_on_chart(M.e(B, M.e(C, f)) - M.e(C, M.e(B, f)) - sum((M.om[A][C][B]-M.om[A][B][C])*M.e(A, f) for A in R5))
         for B in R5 for C in R5)
anti = all(eta[A]*M.om[A][B][C]+eta[B]*M.om[B][A][C] == 0 for A in R5 for B in R5 for C in R5)
print("Levi-Civita frame connection:", lc and anti)
print("spin connection convention:", all(all(vanishes_on_chart(x) for x in (M.Om[C]*G[A]-G[A]*M.Om[C]+sum((M.om[A][B][C]*G[B] for B in R5), Z)))
                                          for A in R5 for C in R5))
dA12 = M.e(1, M.Ag[2])-M.e(2, M.Ag[1])-sum(M.Ag[A]*(M.om[A][2][1]-M.om[A][1][2]) for A in R5)
dA34 = M.e(3, M.Ag[4])-M.e(4, M.Ag[3])-sum(M.Ag[A]*(M.om[A][4][3]-M.om[A][3][4]) for A in R5)
print("dA = F (frame components 12, 34):", vanishes_on_chart(dA12-M.b1) and vanishes_on_chart(dA34-M.b2))
W = witness_model()
print("witness S^rho in M4(Q(i)), no Float:", all(sp.re(x).is_Rational and sp.im(x).is_Rational for S in W.S for x in S) and no_float(*W.S))
report()
