"""BHMAP GEN13 shared definitions (single source for all GEN13 checks). sympy only, exact arithmetic.
Model E local patch: R_t x S^2(1/b1) x S^2(1/b2), chart y=(th1,ph1,th2,ph2) on
V' = {|th_i - pi/2| < pi/3, |ph_i| < pi/3}; there sin(th_i) >= 1/2, so every denominator below is nonzero.
Unknowns: arbitrary (undefined) sympy Functions p{r}{c}(t,th1,ph1,th2,ph2), r=0..4 (vector index), c=0..3 (spinor index).
"""
import sympy as sp
from sympy import I, Rational as Q, sqrt, Matrix, eye, zeros, kronecker_product as kr

t, th1, ph1, th2, ph2 = sp.symbols('t th1 ph1 th2 ph2', real=True)
COORDS = (t, th1, ph1, th2, ph2)
s0 = eye(2); s1 = Matrix([[0, 1], [1, 0]]); s2 = Matrix([[0, -I], [I, 0]]); s3 = Matrix([[1, 0], [0, -1]])
G = [I * kr(s3, s0), kr(s1, s1), kr(s1, s2), kr(s1, s3), kr(s2, s0)]   # Gamma^A, A = 0..4
eta = [-1, 1, 1, 1, 1]; Z = zeros(4, 4); E4 = eye(4); R5 = range(5); SP = [1, 2, 3, 4]


def g3(a, b, c):
    """Gamma^{abc}, unit-weight antisymmetrised product (= Gamma^a Gamma^b Gamma^c for distinct indices)."""
    return Z if len({a, b, c}) < 3 else G[a] * G[b] * G[c]


def blk(f, nr, nc):
    Mx = zeros(4 * nr, 4 * nc)
    for (i, j), B in f.items():
        Mx[4 * i:4 * i + 4, 4 * j:4 * j + 4] = B
    return Mx


class Model:
    """All objects for given parameters (symbols or exact numbers). kappa = 1."""

    def __init__(self, m, lam, b1, b2, pip):
        self.m, self.lam, self.b1, self.b2, self.pip = m, lam, b1, b2, pip
        self.c1 = I * sqrt(Q(3, 128)); self.q = lam * sqrt(Q(2, 3)) * m           # Pauli slice
        F = zeros(5, 5); F[1, 2], F[2, 1], F[3, 4], F[4, 3] = b1, -b1, b2, -b2      # F_AB (frame), lower indices
        self.F = F
        Fs = sum((F[a, b] * G[a] * G[b] for a in R5 for b in R5), Z)                 # F-slash
        Gl = [eta[a] * G[a] for a in R5]                                             # Gamma_A
        c1 = self.c1
        self.X = [-(m / 3) * Gl[a] + lam * c1 * (Fs * Gl[a] - Gl[a] * Fs / 3) for a in R5]
        self.Y = [-(m / 3) * Gl[a] + lam * c1 * (Gl[a] * Fs - Fs * Gl[a] / 3) for a in R5]
        # Levi-Civita frame connection om[A][B][C] = omega^A_B(e_C); only nonzero components listed
        om = [[[0] * 5 for _ in R5] for _ in R5]
        om[1][2][2] = -b1 * sp.cot(th1); om[2][1][2] = b1 * sp.cot(th1)
        om[3][4][4] = -b2 * sp.cot(th2); om[4][3][4] = b2 * sp.cot(th2)
        self.om = om
        self.Om = [sum((Q(1, 4) * eta[A] * om[A][B][C] * G[A] * G[B] for A in R5 for B in R5), Z) for C in R5]
        self.Ag = [0, 0, -sp.cot(th1), 0, -sp.cot(th2)]                               # A_C frame components (b_i r_i = 1)
        self.Ein = [-(b1**2 + b2**2), -b2**2, -b2**2, -b1**2, -b1**2]                 # G^rho_rho (mixed, diagonal)
        self.S = [(Q(1, 2) * self.Ein[r] * G[r]
                   + sum(((I * self.q / 2) * g3(a, b, r) * F[a, b]
                          + Q(1, 2) * g3(a, b, r) * (self.X[a] * self.X[b] - self.X[b] * self.X[a])
                          for a in R5 for b in R5), Z)).applyfunc(lambda x: sp.radsimp(sp.expand(x))) for r in R5]
        self.Mmat = Matrix(16, 16, lambda i, j: g3(i // 4 + 1, 0, j // 4 + 1)[i % 4, j % 4])   # M^{ak} = Gamma^{a0k}
        self.MMmat = -self.Mmat                                                                # MM^{ak} = Gamma^{0ak}

    # frame vector fields e_0..e_4 acting on scalar functions
    def e(self, B, f):
        b1, b2 = self.b1, self.b2
        return [sp.diff(f, t), b1 * sp.diff(f, th1), b1 / sp.sin(th1) * sp.diff(f, ph1),
                b2 * sp.diff(f, th2), b2 / sp.sin(th2) * sp.diff(f, ph2)][B]

    def em(self, B, Mx):
        return Mx.applyfunc(lambda f: self.e(B, f))

    def D(self, psi, B, C):
        """(D_B psi)_C = e_B(psi_C) - omega^A_C(e_B) psi_A + (Omega_B + i q A_B + X_B) psi_C."""
        return (self.em(B, psi[C]) - sum((self.om[A][C][B] * psi[A] for A in R5), zeros(4, 1))
                + (self.Om[B] + I * self.q * self.Ag[B] * E4 + self.X[B]) * psi[C])

    def R(self, psi):
        """R^rho = Gamma^{rho nu sigma} (D_nu psi)_sigma, rho = 0..4."""
        return [sum((g3(r, n, s) * self.D(psi, n, s) for n in R5 for s in R5), zeros(4, 1)) for r in R5]

    def div(self, V):
        """(D+Yhat)_A V^A = e_A(V^A) + omega^A_B(e_A) V^B + (Omega_A + i q A_A + Yhat_A) V^A."""
        return (sum((self.em(A, V[A]) for A in R5), zeros(4, 1))
                + sum((self.om[A][B][A] * V[B] for A in R5 for B in R5), zeros(4, 1))
                + sum(((self.Om[A] + I * self.q * self.Ag[A] * E4 + self.Y[A]) * V[A] for A in R5), zeros(4, 1)))

    def star(self, rho, pip=None):
        """star rho = (d_t + Yhat_0) rho - pi' (D+Yhat)_A W^A,  W^0 = 0, W^a = Gamma^0 Gamma^a rho."""
        pip = self.pip if pip is None else pip
        return self.em(0, rho) + self.Y[0] * rho - pip * self.div([zeros(4, 1)] + [G[0] * G[a] * rho for a in SP])

    def g_of(self, R):
        """g := M^{-1}(R^a + pi' Gamma^0 Gamma^a R^0)  (so that Ktilde = d_t Phi - g)."""
        return self.Mmat.inv() * Matrix.vstack(*[R[a] + self.pip * G[0] * G[a] * R[0] for a in SP])

    def Psym(self, xi):
        """Frame principal symbol of K' (d_j -> xi_j):
        MM^{-1} sum_j xi_j [Gamma^{ijk} - Gamma^{0ij} (S^0)^{-1} S^k + pi' Gamma^0 Gamma^i Gamma^{0jk}]."""
        S0i = self.S[0].inv()
        return (self.MMmat.inv() * blk({(i - 1, k - 1): sum((xi[j - 1] * (g3(i, j, k) - g3(0, i, j) * S0i * self.S[k]
                                                                          + self.pip * G[0] * G[i] * g3(0, j, k)) for j in SP), Z)
                                         for i in SP for k in SP}, 4, 4)).applyfunc(sp.expand)

    def Lsym(self, xi):
        return blk({(0, k - 1): sum((xi[j - 1] * g3(0, j, k) for j in SP), Z) for k in SP}, 1, 4)


def generic_psi():
    return [Matrix([sp.Function(f'p{r}{c}')(*COORDS) for c in range(4)]) for r in R5]


# ---------- exact zero test on the chart V' ----------
C1, S1, C2, S2 = sp.symbols('C1 S1 C2 S2')
TRIG = (sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc)
DENOMS = set()


def to_poly_trig(expr):
    """Replace cot -> cos/sin, then sin(th_i)->S_i, cos(th_i)->C_i. Asserts no trig atom remains."""
    ex = expr.subs({sp.cot(th1): sp.cos(th1) / sp.sin(th1), sp.cot(th2): sp.cos(th2) / sp.sin(th2)})
    ex = ex.subs({sp.sin(th1): S1, sp.cos(th1): C1, sp.sin(th2): S2, sp.cos(th2): C2})
    assert not ex.atoms(*TRIG), "unexpected trigonometric atom"
    return ex


STATS = {'entries': 0, 'zero_after_expand': 0, 'zero_after_cot_rewrite': 0, 'zero_after_reduction': 0, 'nonzero': 0}
TRIG_ATOMS = set()


def vanishes_on_chart(expr):
    """Exact zero test on the chart V' (where sin th_i >= 1/2).
    Step 0: record the trigonometric atoms present in the raw residual (all are sin, cos, cot of th1, th2).
    Step 1: if sp.expand(expr) == 0 identically (as an expression in independent atoms), it vanishes.
    Step 2: otherwise write expr = num/den after cot -> cos/sin, sin->S_i, cos->C_i; den is recorded in DENOMS
            (it is a product of powers of S1, S2, nonzero on V'); num is reduced modulo C1^2+S1^2-1 (in C1) and
            C2^2+S2^2-1 (in C2). Zero remainder => num = q1*(C1^2+S1^2-1) + q2*(C2^2+S2^2-1), which vanishes when
            C_i = cos th_i, S_i = sin th_i; since den != 0 on V', expr = 0 on V'."""
    STATS['entries'] += 1
    TRIG_ATOMS.update(map(str, expr.atoms(*TRIG)))
    ex0 = sp.expand(expr)
    if ex0 == 0:
        STATS['zero_after_expand'] += 1
        return True
    ex = sp.expand(to_poly_trig(ex0))
    if ex == 0:
        STATS['zero_after_cot_rewrite'] += 1   # zero as a rational expression in independent S_i, C_i (no identity used)
        return True
    num, den = sp.fraction(sp.together(ex))
    for fac in sp.Mul.make_args(sp.factor(den)):
        base = fac.as_base_exp()[0]
        if not base.is_number:
            DENOMS.add(base)
    num = sp.expand(num)
    num = sp.rem(sp.rem(num, C1**2 + S1**2 - 1, C1), C2**2 + S2**2 - 1, C2)
    ok = sp.expand(num) == 0
    STATS['zero_after_reduction' if ok else 'nonzero'] += 1
    return ok


def report():
    print("zero-test statistics:", STATS)
    print("trig atoms in raw residuals:", sorted(TRIG_ATOMS))
    print("denominators cleared in step 2:", sorted(map(str, DENOMS)) or "none (step 2 not needed)")


def no_float(*mats):
    return not any(x.atoms(sp.Float) for Mx in mats for x in Mx)


def symbolic_model():
    m, lam, b1, b2, pip = sp.symbols('m lam b1 b2 pip', positive=True)
    return Model(m, lam, b1, b2, pip)


def witness_model():
    return Model(sqrt(Q(823, 142944)), sqrt(Q(1, 2)), 1, Q(1, 3), Q(1, 2))
