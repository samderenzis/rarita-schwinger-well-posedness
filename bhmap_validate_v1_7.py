#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BHMAP comprehensive validation suite  (v1.1, 2026-11-20; written by Claude for the BHMAP owner;
v1.1 implements ChatGPT's review of v1.0 — see BHMAP_VALIDATOR_REVIEW/REVIEW_RESPONSE.md;
v1.2: DOIs taken from pasted URLs are URL-decoded and stripped of URL-only suffixes ("/", "/full", "/abstract", "/pdf"...)
before the exact lookup — the owner's deep run showed 4 such artefacts reported as unresolved;
v1.3: every check runs in its own process with its own time limit (killed → INCOMPLETE, never PASS); live progress with
elapsed time and the previous run's timing; Ctrl-C writes a partial report; checkpoint + --resume reuses PASS/INFO results of an
identical configuration; network pre-flight; arXiv lookups resumable per ID with back-off, batch bisection and an /abs fallback;
dense non-unitary basis changes split out as check B6 so they run in parallel;
v1.4: the per-ID arXiv fallback uses OAI-PMH GetRecord on export.arxiv.org (arXiv's preferred metadata channel) instead of the
main-site /abs page, per https://info.arxiv.org/help/bulk_data.html — no request ever goes to the main arxiv.org site;
v1.5: REPOSITORY MODE (--repo DIR, auto-detected when the script sits next to scripts/ and data/): archive checks verify the public
repository instead of the private archive (A1 repository manifest, A4 personal-file scan, A6 pinned scripts, new A7 data file =
fresh recomputation); private-archive-only checks (A2, A3, A5) report NA ("not applicable", listed, never counted as PASS); G1/G2
scan the repository's own references. A run in either mode can reach COMPLETE_PASS;
v1.6: G1/G2 reference scan (i) skips the validator's OWN source file (bhmap_validate_v*.py): its regular expressions and
test strings are not citations (in repository mode it sits inside the scanned folder and its literal "10.48550/arxiv" was
read as a DOI); every other file, every other .py included, is still scanned; (ii) image addresses built from a DOI
(badge ".../10.5281/zenodo.N.svg") are normalised to the DOI they name, like ".pdf"/".xml" before. No other change;
v1.7: G1/G2 reference scan also skips the validator's OWN OUTPUTS, which quote the DOIs they checked (with JSON escapes and
truncated context) and cache whole Crossref records: the output folder (bhmap_validation_out and the --out folder) and, anywhere,
files recognised by exact content signature (results JSON by its title line, results CSV by its header, checkpoint, online caches,
timing history). Every skipped file is listed in the G1/G2 details. A new H2 self-test checks that outputs are skipped and that an
ordinary document is still scanned. No other change.)
==================================================================================================
One program that re-checks, by several independent methods, every computational and numerically testable
claim of the BHMAP proof chain, checks the integrity of the archive, and (optionally, online) checks every
DOI / arXiv reference cited in the archive against Crossref / arXiv.

Run it like this (Python 3.10+):
    pip install sympy numpy scipy mpmath python-flint requests
    python bhmap_validate.py --pack BHMAP_COMPACT_2026-11-20_GEN25.zip --level standard --online
Options:
    --pack PATH     the private compact archive zip (or folder) — owner's full-archive mode
    --repo DIR      the public repository folder (auto-detected if this script sits next to scripts/ and data/)
    --level         quick | standard | deep   (deep is sized for a 12-core / 24-thread CPU such as a Ryzen 9 9900X)
    --workers N     parallel processes (default min(8, CPUs); for deep start with 4 and watch RAM)
    --online        also verify cited DOIs (Crossref) and arXiv IDs (arXiv API). Needs internet.
    --mailto ADDR   optional contact address for the Crossref polite pool
    --budget SEC    overall time budget (default 6 h deep, 2 h otherwise); unfinished checks are reported INCOMPLETE
    --only IDS      run a subset (the verdict is then at best PARTIAL_PASS)
    --resume        after an interruption/timeout: reuse PASS/INFO results of an identical configuration, re-run the rest
    --check-timeout per-check limit (s); --online-cap: time cap inside each online check (s); --heartbeat: progress interval (s)
Verdicts: COMPLETE_PASS (all 36 checks accounted for; each PASS, INFO, or NA = not applicable in this mode, listed) | PARTIAL_PASS (nothing failed, but something was skipped or not
selected — listed) | FAIL | ERROR (a check crashed, timed out or could not finish).
    --out DIR       output folder (default ./bhmap_validation_out)
    --seed S        random seed (default 20261120); every random test records its seed.
Outputs (send both files back):
    <out>/bhmap_validation_results.json   full detail: environment, every check, every sub-measurement
    <out>/bhmap_validation_results.csv    one row per check
What "PASS" means here: the stated identity / inequality / integrity property held under the stated method.
Exact checks are proofs of the finite identities they test. Numerical checks are falsification attempts:
a PASS means no counterexample was found, not a proof. Toy-model checks illustrate the logic only.
Nothing here is human verification or independent replication; see the provenance notes in the JSON.
"""
import argparse, csv, hashlib, importlib.util, io, json, math, os, platform, random, re, shutil, subprocess
import sys, tempfile, time, traceback, zipfile, contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

SCRIPT_VERSION = "1.7"
# ======================================================================================================
# Embedded copy of GEN13 scripts/bhmap_defs.py (byte-exact; sha256 is checked at start-up)
# ======================================================================================================
BHMAP_DEFS_SHA256 = "3d0fcd3c3a0ed88aef4ec33e1a014d1621e744621541ca0b2ded5ed6dd446bc0"
BHMAP_DEFS_SRC = r'''"""BHMAP GEN13 shared definitions (single source for all GEN13 checks). sympy only, exact arithmetic.
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
'''
WITNESS_MIN_SHA256 = "4c79837ac4d04fd0255ff5b999930c162f69d37b4d2933972ea29a0f7f87bc64"
WITNESS_MIN_SRC = r'''# BHMAP minimal witness (self-contained; sympy only). Builds S^rho from the divergence-identity formula,
# eliminates psi_0, forms the principal symbol P(xi) and constraint symbol L(xi), and checks a Jordan chain.
import sympy as sp
from sympy import I, Rational as Q, sqrt, Matrix, eye, zeros, kronecker_product as kr
s0=eye(2); s1=Matrix([[0,1],[1,0]]); s2=Matrix([[0,-I],[I,0]]); s3=Matrix([[1,0],[0,-1]])
G=[I*kr(s3,s0), kr(s1,s1), kr(s1,s2), kr(s1,s3), kr(s2,s0)]          # Gamma^A, A=0..4
eta=[-1,1,1,1,1]; Z=zeros(4,4); E=eye(4); R5=range(5); SP=[1,2,3,4]
assert all(G[a]*G[b]+G[b]*G[a]==2*(eta[a] if a==b else 0)*E for a in R5 for b in R5)
def g3(a,b,c): return Z if len({a,b,c})<3 else G[a]*G[b]*G[c]          # Gamma^{abc}, unit weight
# parameters (witness)
lam2,m2,beta,pip=Q(1,2),Q(823,142944),Q(1,3),Q(1,2)
lam,m=sqrt(lam2),sqrt(m2); b1,b2=1,beta; c1=I*sqrt(Q(3,128)); kap=1; q=lam*sqrt(Q(2,3))*kap*m
F=zeros(5,5); F[1,2],F[2,1],F[3,4],F[4,3]=b1,-b1,b2,-b2                 # F_AB (frame)
Fs=sum((F[a,b]*G[a]*G[b] for a in R5 for b in R5),Z)                   # F-slash = F_AB G^A G^B
Gl=[eta[a]*G[a] for a in R5]                                           # Gamma_A
X=[-(m/3)*Gl[a]+lam*kap*c1*(Fs*Gl[a]-Gl[a]*Fs/3) for a in R5]          # X_A
Ein=[-(b1**2+b2**2),-b2**2,-b2**2,-b1**2,-b1**2]                       # G^rho_rho (diagonal Einstein tensor, mixed)
S=[]
for r in R5:
    M=Q(1,2)*Ein[r]*G[r]
    for a in R5:
        for b in R5:
            M+= (I*q/2)*g3(a,b,r)*F[a,b] + Q(1,2)*g3(a,b,r)*(X[a]*X[b]-X[b]*X[a])
    S.append(M.applyfunc(lambda e: sp.radsimp(sp.expand(e))))   # exact; no numerical recognition
def blk(f,nr,nc):
    M=zeros(4*nr,4*nc)
    for (i,j),B in f.items(): M[4*i:4*i+4,4*j:4*j+4]=B
    return M
MM=blk({(i-1,k-1):g3(0,i,k) for i in SP for k in SP},4,4); MMi=MM.inv()
S0i=S[0].inv()
def Psym(xi):   # principal symbol of K' (d_j -> xi_j): MM^{-1}[G^{ijk}xi_j - G^{0ij}xi_j S0^{-1}S^k + pi' G^0 G^i G^{0jk}xi_j]
    return (MMi*blk({(i-1,k-1):sum((xi[j-1]*(g3(i,j,k)-g3(0,i,j)*S0i*S[k]+pip*G[0]*G[i]*g3(0,j,k)) for j in SP),Z)
                    for i in SP for k in SP},4,4)).applyfunc(sp.expand)
def Lsym(xi): return blk({(0,k-1):sum((xi[j-1]*g3(0,j,k) for j in SP),Z) for k in SP},1,4)
xi=[Q(20,99),0,1,0]; r=Q(101,99); P=Psym(xi); L=Lsym(xi); N=P-r*eye(16)
print("S^rho entries in Q(i) (sqrt(m), sqrt(lambda) cancelled):", all(sp.re(e).is_Rational and sp.im(e).is_Rational for Sx in S for e in Sx))
print("no Float atoms in G, X, S, P, L:", not any(x.atoms(sp.Float) for Mx in G+X+S+[P,L] for x in Mx))
print("det S0 =", sp.factor(S[0].det()))
print("L L^dag == 3|xi|^2 I:", all(sp.expand(x)==0 for x in (L*L.H-3*sum(x*x for x in xi)*E)))

v=Matrix([11160500,0,-16835940*I,-1495280*I,0,0,0,0,55244475,0,-83337903*I,-7401636*I,0,0,0,0])
w=Matrix([-Q(3327596241179925,5527168),-Q(84691183525,5568),Q(407204312313361225,679841664)*I,Q(11902340395341825,113306944)*I,
          -Q(133046953528127925,226613888)*I,-Q(11666650486523175,113306944)*I,-Q(135032816027184075,226613888),-Q(1166781726825,76096),
          Q(552389505525,19024),Q(20361144375,9512),0,0,0,0,0,0])
zero=lambda X: all(sp.expand(e)==0 for e in X)
print("L v == 0:", zero(L*v), "| L w == 0:", zero(L*w))
print("(P - r) v == 0:", zero(N*v), "| (P - r) w == v:", zero(N*w-v), "| v != 0:", not zero(v))
g=sp.symbols('gamma',positive=True); a=v-I*g*w
print("L a_gamma == 0:", zero(L*a), "| (gamma - i(P-r)) a_gamma == -i gamma^2 w:", zero((g*eye(16)-I*N)*a+I*g**2*w))
print("sympy", sp.__version__)
'''

# Golden stdout of the six GEN13 scripts (Claude's run and ChatGPT's external re-execution agree line for line).
GOLDEN = {
 "check_1_clifford_intertwining.py": ["Clifford {G^A,G^B} = 2 eta^{AB}: True", "intertwining (general F, symbolic m, lam): True"],
 "check_2_geometry.py": ["Levi-Civita frame connection: True", "spin connection convention: True",
    "dA = F (frame components 12, 34): True", "witness S^rho in M4(Q(i)), no Float: True",
    "zero-test statistics: {'entries': 427, 'zero_after_expand': 423, 'zero_after_cot_rewrite': 4, 'zero_after_reduction': 0, 'nonzero': 0}",
    "trig atoms in raw residuals: ['cos(th1)', 'cos(th2)', 'cot(th1)', 'cot(th2)', 'sin(th1)', 'sin(th2)']",
    "denominators cleared in step 2: none (step 2 not needed)"],
 "check_3_divergence_identity.py": ["no Float atoms: True", "DI on Model E (arbitrary psi, symbolic parameters): True",
    "zero-test statistics: {'entries': 4, 'zero_after_expand': 0, 'zero_after_cot_rewrite': 4, 'zero_after_reduction': 0, 'nonzero': 0}",
    "trig atoms in raw residuals: ['cos(th1)', 'cos(th2)', 'cot(th1)', 'cot(th2)', 'sin(th1)', 'sin(th2)']",
    "denominators cleared in step 2: none (step 2 not needed)"],
 "check_4_constraint_intertwining.py": ["Ktilde free of d/dt: True", "CI (arbitrary psi_0, Phi; symbolic parameters): True",
    "zero-test statistics: {'entries': 4, 'zero_after_expand': 0, 'zero_after_cot_rewrite': 4, 'zero_after_reduction': 0, 'nonzero': 0}",
    "trig atoms in raw residuals: ['cos(th1)', 'cos(th2)', 'cot(th1)', 'cot(th2)', 'sin(th1)', 'sin(th2)']",
    "denominators cleared in step 2: none (step 2 not needed)"],
 "check_5_principal_symbol.py": ["no Float atoms: True", "degree in Lam <= 1: True", "principal symbol of curved K' at y0 == i P(xi*): True"],
 "witness_min.py": ["S^rho entries in Q(i) (sqrt(m), sqrt(lambda) cancelled): True", "no Float atoms in G, X, S, P, L: True",
    "det S0 = 3063716808343140625/132101812606622109696", "L L^dag == 3|xi|^2 I: True",
    "L v == 0: True | L w == 0: True", "(P - r) v == 0: True | (P - r) w == v: True | v != 0: True",
    "L a_gamma == 0: True | (gamma - i(P-r)) a_gamma == -i gamma^2 w: True"],
}
DET_S0 = "3063716808343140625/132101812606622109696"

# Expected bibliographic metadata of the core references (checked against Crossref when --online).
CORE_REFS = {
 "10.1103/PhysRev.186.1337": {"who": "Velo–Zwanziger", "year": 1969, "volume": "186", "page": "1337"},
 "10.5802/jep.3": {"who": "Métivier (J. Éc. polytech. Math.)", "year": 2014, "volume": "1", "page": "39"},
 "10.1088/1361-6382/ab954c": {"who": "Abalos–Reula (CQG)", "year": 2020, "volume": "37", "page": "185012"},
 "10.1143/PTP.58.1538": {"who": "Khalil (PTP)", "year": 1977, "volume": "58", "page": "1538"},
 "10.1070/RM1974v029n05ABEH001295": {"who": "Ivrii–Petkov (Russ. Math. Surveys)", "year": 1974, "volume": "29"},
 "10.1088/0305-4470/36/31/306": {"who": "Frauendiener (J. Phys. A)", "year": 2003, "volume": "36", "page": "8433"},
}

# ======================================================================================================
# Infrastructure
# ======================================================================================================
LEVELS = {"quick": 0, "standard": 1, "deep": 2}
def lv(level, q, s, d): return (q, s, d)[LEVELS[level]]
def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(mod)
    return mod

def fresh_defs(ctx, tag="d"):
    """A fresh, private instance of bhmap_defs (so that patching Gammas never leaks between tasks)."""
    name = f"bhmap_defs_{tag}_{os.getpid()}_{random.randrange(1 << 30)}"
    return load_module(os.path.join(ctx["embed_dir"], "bhmap_defs.py"), name)

def witness(ctx):
    """Run witness_min.py in-process and return its namespace (P, L, S, v, w, r, xi, MM, ...)."""
    import runpy
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(os.path.join(ctx["embed_dir"], "witness_min.py"))

def R(status, expected=None, observed=None, details=None, metric=None, threshold=None):
    return {"status": status, "expected": expected, "observed": observed, "details": details or {},
            "metric": metric, "threshold": threshold}

CHECKS = []
def check(cid, group, name, method, independence, claim, kind="exact", needs=()):
    def deco(f):
        CHECKS.append(dict(id=cid, group=group, name=name, method=method, independence=independence, claim=claim,
                           kind=kind, needs=tuple(needs), func=f.__name__))
        return f
    return deco

def _run_one(meta, ctx):
    t0 = time.time(); random.seed(ctx["seed"] + int(hashlib.md5(meta["id"].encode()).hexdigest()[:6], 16))
    try:
        func = meta["func"]
        for dep in meta["needs"]:
            if dep == "online" and not ctx.get("online"): return {**meta, **R("SKIP", details={"reason": "no --online"}), "runtime_s": 0}
            if dep in ("numpy", "scipy", "flint", "requests", "mpmath"):
                try: __import__(dep)
                except Exception as e: return {**meta, **R("SKIP", details={"reason": f"module {dep} not installed: {e}"}), "runtime_s": 0}
        if "pack" in meta["needs"] and not ctx.get("pack_dir"):
            if ctx.get("repo_dir"):
                alt = REPO_MODE.get(meta["id"], "NA")
                if alt == "NA": return {**meta, **R("NA", details={"reason": "private-archive check; not applicable in repository mode (run with --pack for it)"}), "runtime_s": 0}
                func = alt
            else:
                return {**meta, **R("SKIP", details={"reason": "no --pack or --repo given"}), "runtime_s": 0}
        if "repo" in meta["needs"] and not ctx.get("repo_dir"):
            if ctx.get("pack_dir"): return {**meta, **R("NA", details={"reason": "repository check; not applicable in full-archive mode"}), "runtime_s": 0}
            return {**meta, **R("SKIP", details={"reason": "no --repo"}), "runtime_s": 0}
        out = globals()[func](ctx)
    except Exception:
        out = R("ERROR", details={"traceback": traceback.format_exc()[-4000:]})
    out = {**meta, **out}; out["runtime_s"] = round(time.time() - t0, 3); return out

# ======================================================================================================
# Exact-arithmetic helpers (pure Python Gaussian rationals; independent of sympy and FLINT)
# ======================================================================================================
from fractions import Fraction as Fr
def gq(x):
    import sympy as sp
    re_, im_ = sp.re(x), sp.im(x)
    assert re_.is_Rational and im_.is_Rational, f"non-Q(i) entry {x}"
    return (Fr(int(re_.p), int(re_.q)), Fr(int(im_.p), int(im_.q)))
def gmul(a, b): return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])
def gadd(a, b): return (a[0] + b[0], a[1] + b[1])
def gmat(M): return [[gq(M[i, j]) for j in range(M.shape[1])] for i in range(M.shape[0])]
def gvec(v): return [gq(v[i]) for i in range(v.shape[0])]
def gmv(M, x):
    out = []
    for row in M:
        s = (Fr(0), Fr(0))
        for a, b in zip(row, x): s = gadd(s, gmul(a, b))
        out.append(s)
    return out
def gzero(x): return all(a == 0 and b == 0 for a, b in x)

def flint_realrep(M):
    import flint, sympy as sp
    n, m = M.shape; Rm = flint.fmpq_mat(2*n, 2*m)
    for i in range(n):
        for j in range(m):
            a, b = gq(M[i, j]); A = flint.fmpq(a.numerator, a.denominator); B = flint.fmpq(b.numerator, b.denominator)
            Rm[i, j] = A; Rm[i+n, j+m] = A; Rm[i, j+m] = -B; Rm[i+n, j] = B
    return Rm
def flint_eye(n):
    import flint
    I = flint.fmpq_mat(n, n)
    for i in range(n): I[i, i] = 1
    return I

# ======================================================================================================
# GROUP A — archive integrity   (helpers take an explicit root so that H2 can mutate temporary copies)
# ======================================================================================================
SCRIPT_HASHES = {   # all six GEN13 proof-carrying scripts + shared definitions (v1.1: every file pinned)
 "bhmap_defs.py": BHMAP_DEFS_SHA256, "witness_min.py": WITNESS_MIN_SHA256,
 "check_1_clifford_intertwining.py": "2a627df9a3b407c03ce9c4926b1c6d9d7e3ffce3a8623f9166c14606b42a4ddb",
 "check_2_geometry.py": "81470aca217fb276823a59d9778ff17274f6b8cdbd69c2083bafc206fcac0568",
 "check_3_divergence_identity.py": "1cbd75bcadaa8d6d398ca922355a3aa6c2c1cee67bc0bbad28f2c5ec3b75f836",
 "check_4_constraint_intertwining.py": "722c80750f13af2173216a23ef0f8d6d72494408a138c08e85b0f7144d5c703b",
 "check_5_principal_symbol.py": "e1f20c0cce59a79ab4e093cf2d574bfd2e71068f86ce7e894b94fab9dc3cf0e6",
}
LIVING_ROOT_FILES = {"./CLAIM_LEDGER.md", "./CURRENT_STATUS.md", "./PROJECT_ERRATA_REGISTER.md", "./README_AI.md"}
MANIFEST_NAME_RE = re.compile(r"(GEN|G)[0-9_]+_SHA256SUMS")
GEN_DIR_RE = re.compile(r"GEN[0-9]+(_[0-9]+)?(_[A-Z_]+)?")

def _manifest_excluded(rel):
    """Files deliberately NOT listed in INTEGRITY/PACK_SHA256SUMS (explicit, auditable list):
    the pack manifest itself and every file literally named SHA256SUMS (build_compact.py convention)."""
    return rel == "INTEGRITY/PACK_SHA256SUMS" or os.path.basename(rel) == "SHA256SUMS"

def a1_core(root):
    man = os.path.join(root, "INTEGRITY", "PACK_SHA256SUMS"); listed = {}; ok = bad = missing = 0; probs = []
    for line in open(man, encoding="utf-8"):
        h, p = line.rstrip("\n").split("  ", 1); rel = p[2:] if p.startswith("./") else p; listed[rel] = h
        fp = os.path.join(root, rel)
        if not os.path.exists(fp): missing += 1; probs.append(("missing", rel)); continue
        if sha256_file(fp) == h: ok += 1
        else: bad += 1; probs.append(("mismatch", rel))
    actual = set()
    for dp, dn, fn in os.walk(root):
        for f in fn: actual.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    extra = sorted(x for x in actual - set(listed) if not _manifest_excluded(x))
    excluded = sorted(x for x in actual - set(listed) if _manifest_excluded(x))
    st = "PASS" if bad == 0 and missing == 0 and not extra else "FAIL"
    return R(st, "every listed file matches; no unlisted files except the explicit manifest exclusions",
             {"ok": ok, "mismatched": bad, "missing": missing, "unlisted_extra_files": len(extra), "explicitly_excluded": len(excluded)},
             {"problems": probs[:50], "extra_files": extra[:50], "excluded_list": excluded})

def _dedup_removed(root):
    out = {}
    p = os.path.join(root, "INTEGRITY", "DEDUP_MAP.tsv")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8").read().splitlines()[1:]:
            h, sz, keep, rem = line.split("\t"); out[rem.replace(os.sep, "/")] = (h, keep)
    return out

def a2_core(root):
    dedup = _dedup_removed(root); res = {}; fails = []
    for d in sorted(os.listdir(root)):
        dp = os.path.join(root, d)
        if not (os.path.isdir(dp) and GEN_DIR_RE.fullmatch(d)): continue
        cands = [f for f in os.listdir(dp) if MANIFEST_NAME_RE.fullmatch(f)]
        if not cands: res[d] = "NO MANIFEST"; fails.append(d + ": no manifest"); continue
        ok = bad = 0; permitted = []; unexpected = []
        for line in open(os.path.join(dp, cands[0]), encoding="utf-8"):
            if "  " not in line: continue
            h, p = line.rstrip("\n").split("  ", 1); fp = os.path.normpath(os.path.join(dp, p))
            rel = os.path.relpath(fp, root).replace(os.sep, "/")
            if not os.path.exists(fp):
                dd = dedup.get(rel)
                if dd and dd[0] == h and os.path.exists(os.path.join(root, dd[1])) and sha256_file(os.path.join(root, dd[1])) == h:
                    permitted.append(rel)
                else: unexpected.append(rel)
                continue
            if sha256_file(fp) == h: ok += 1
            else: bad += 1; unexpected.append("MISMATCH " + rel)
        res[d] = {"manifest": cands[0], "ok": ok, "mismatch": bad, "permitted_dedup_missing": permitted, "unexpected": unexpected}
        if bad or unexpected: fails.append(d)
    return R("PASS" if not fails else "FAIL", "every GEN folder has a manifest; all files match; any absent file is a registered DEDUP_MAP entry whose kept copy has the same hash",
             f"{len(fails)} problem folders", {"folders": res, "problems": fails})

@check("A1", "integrity", "Pack manifest: every listed file matches, nothing listed is missing, and no unlisted file is present",
       "sha256 of every file + full inventory comparison", "file system only", "GEN25 pack integrity", needs=("pack",))
def a1(ctx): return a1_core(ctx["pack_dir"])

@check("A2", "integrity", "Every GEN folder has its manifest; every listed file matches or is a verified DEDUP_MAP entry",
       "sha256 per GEN manifest; deduplicated files checked against DEDUP_MAP and the kept copy", "file system only",
       "per-generation integrity", needs=("pack",))
def a2(ctx): return a2_core(ctx["pack_dir"])

def a3_core(root, timeout):
    tmp = tempfile.mkdtemp(prefix="bhmap_restore_")
    try:
        dst = os.path.join(tmp, "pack"); shutil.copytree(root, dst)
        p = subprocess.run([sys.executable, os.path.join("INTEGRITY", "restore_full_layout.py")], cwd=dst, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
        out = p.stdout
        m = re.search(r"verified OK: (\d+) \| mismatches: (\d+) \| missing: (\d+)", out)
        mism = set(re.findall(r"MISMATCH (\S+)", out)); gen_bad = {}
        for d, pfx in (("GEN9", "G9"), ("GEN10", "G10"), ("GEN11", "G11")):
            man = os.path.join(dst, d, f"{pfx}_SHA256SUMS"); bad = 0
            for line in open(man, encoding="utf-8"):
                if "  " not in line: continue
                h, q = line.rstrip("\n").split("  ", 1); fp = os.path.join(dst, d, q)
                if not os.path.exists(fp) or sha256_file(fp) != h: bad += 1
            gen_bad[d] = bad
        # restore_full_layout.py exits 1 whenever any mismatch exists; with exactly the 4 living files mismatched, exit 1 is the
        # expected outcome. Any other exit code (crash, signal) or exit 1 with a different mismatch set is a failure.
        conds = {"exit_code_as_expected (1 iff mismatches/missing, else 0)": p.returncode == (1 if (mism or (m and int(m.group(3)))) else 0),
                 "summary_line_found": bool(m),
                 "missing_0": bool(m) and int(m.group(3)) == 0,
                 "reported_mismatch_count_equals_list": bool(m) and int(m.group(2)) == len(mism),
                 "mismatch_set_exactly_the_4_living_files": mism == LIVING_ROOT_FILES,
                 "GEN9_11_complete": all(v == 0 for v in gen_bad.values())}
        return R("PASS" if all(conds.values()) else "FAIL", "all conditions true", conds,
                 {"summary": m.group(0) if m else None, "mismatched": sorted(mism), "gen9_11_failures": gen_bad, "stdout_tail": out[-2000:],
                  "stderr_tail": p.stderr[-1000:], "note": "the 4 living root files are updated every pass by design"})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

@check("A3", "integrity", "Restore script rebuilds the full layout: expected exit code, 0 missing, mismatches exactly the 4 living files, GEN9–11 complete",
       "INTEGRITY/restore_full_layout.py in a temp copy", "file system only", "compact-format design (DEDUP_MAP)", needs=("pack",))
def a3(ctx): return a3_core(ctx["pack_dir"], ctx["budget_sub"])

@check("A4", "integrity", "Personal document excluded (no PDFs; no b748a1e7 file)", "file-name and type scan",
       "file system only", "owner rule: never include the flooring PDF", needs=("pack",))
def a4(ctx):
    pdfs, hits = [], []
    for dp, dn, fn in os.walk(ctx["pack_dir"]):
        for f in fn:
            if f.lower().endswith(".pdf"): pdfs.append(os.path.relpath(os.path.join(dp, f), ctx["pack_dir"]))
            if "b748a1e7" in f.lower(): hits.append(os.path.relpath(os.path.join(dp, f), ctx["pack_dir"]))
    return R("PASS" if not pdfs and not hits else "FAIL", "no PDFs, no b748a1e7 file", {"pdfs": pdfs, "b748a1e7_files": hits})

@check("A5", "integrity", "Claim ledger rows contiguous and unique; errata G-1..G-n contiguous", "parse root ledger and errata register",
       "text only", "record keeping", needs=("pack",))
def a5(ctx):
    root = ctx["pack_dir"]
    rows = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", open(os.path.join(root, "CLAIM_LEDGER.md"), encoding="utf-8").read(), re.M)]
    gs = sorted({int(x) for x in re.findall(r"G-(\d+)", open(os.path.join(root, "PROJECT_ERRATA_REGISTER.md"), encoding="utf-8").read())})
    dup = sorted({r for r in rows if rows.count(r) > 1}); gaps = [i for i in range(1, max(rows) + 1) if i not in rows]
    ggaps = [i for i in range(1, max(gs) + 1) if i not in gs]
    st = "PASS" if not dup and not gaps and not ggaps else "FAIL"
    return R(st, "no gaps/duplicates", {"ledger_rows": f"1..{max(rows)}", "dups": dup, "gaps": gaps, "errata": f"G-1..G-{max(gs)}", "errata_gaps": ggaps})

def a6_core(script_dir, budget):
    res = {}; fails = []
    for f, h in SCRIPT_HASHES.items():
        fp = os.path.join(script_dir, f); hh = sha256_file(fp) if os.path.exists(fp) else None
        res[f + "_sha256"] = {"expected": h, "actual": hh, "match": hh == h}
        if hh != h: fails.append("hash " + f)
    if fails:   # never execute unverified code
        return R("FAIL", "all 7 hashes match before execution", fails, res)
    tmp = tempfile.mkdtemp(prefix="bhmap_g13_")
    try:
        for f in SCRIPT_HASHES: shutil.copy2(os.path.join(script_dir, f), tmp)
        for f, gold in GOLDEN.items():
            t0 = time.time()
            try:
                p = subprocess.run([sys.executable, "-u", f], cwd=tmp, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=budget)
                lines = [l.strip() for l in p.stdout.strip().splitlines() if not l.startswith("sympy ")]
                ok = (lines == gold) and p.returncode == 0
                res[f] = {"exit": p.returncode, "match_golden": ok, "runtime_s": round(time.time() - t0, 1), "stdout": lines, "stderr_tail": p.stderr[-500:]}
            except subprocess.TimeoutExpired:
                ok = False; res[f] = {"timeout_s": budget, "status": "INCOMPLETE (timeout)"}
            if not ok: fails.append(f)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return R("PASS" if not fails else "FAIL", "7 hashes match; 6 scripts exit 0 with stdout identical to golden", fails or "none failed", res)

@check("A6", "integrity", "GEN13 proof-carrying scripts from the pack: all 7 file hashes pinned, then exit code and golden stdout",
       "hash first, then subprocess run of the archived scripts", "archived code, fresh interpreter", "GEN13 checks 1-5 + witness_min (G-65 resolved)",
       needs=("pack",))
def a6(ctx): return a6_core(os.path.join(ctx["pack_dir"], "GEN13", "scripts"), ctx["budget_sub"])

# ---- repository mode (v1.5) ----
REPO_MODE = {"A1": "a1_repo", "A4": "a4_repo", "A6": "a6_repo", "G1": "g1", "G2": "g2"}   # A2, A3, A5 → NA
REPO_IGNORE_DIRS = {".git", "__pycache__", "bhmap_validation_out", ".github"}

def a1_repo_core(root):
    man = os.path.join(root, "SHA256SUMS"); listed = {}; ok = bad = missing = 0; probs = []
    for line in open(man, encoding="utf-8"):
        if "  " not in line: continue
        h, p = line.rstrip("\n").split("  ", 1); rel = p[2:] if p.startswith("./") else p; listed[rel] = h
        fp = os.path.join(root, rel)
        if not os.path.exists(fp): missing += 1; probs.append(("missing", rel)); continue
        if sha256_file(fp) == h: ok += 1
        else: bad += 1; probs.append(("mismatch", rel))
    actual = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in REPO_IGNORE_DIRS]
        for f in fn: actual.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    extra = sorted(actual - set(listed) - {"SHA256SUMS"})
    return R("PASS" if not bad and not missing and not extra else "FAIL", "every file in SHA256SUMS matches; nothing missing; no unlisted files",
             {"ok": ok, "mismatched": bad, "missing": missing, "unlisted_extra_files": len(extra)},
             {"mode": "repository", "problems": probs[:50], "extra_files": extra[:50], "ignored_dirs": sorted(REPO_IGNORE_DIRS)})
def a1_repo(ctx): return a1_repo_core(ctx["repo_dir"])

def a4_repo(ctx):
    pdfs, hits = [], []
    for dp, dn, fn in os.walk(ctx["repo_dir"]):
        dn[:] = [d for d in dn if d not in REPO_IGNORE_DIRS]
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), ctx["repo_dir"]).replace(os.sep, "/")
            if f.lower().endswith(".pdf") and not rel.startswith("paper/"): pdfs.append(rel)
            if "b748a1e7" in f.lower(): hits.append(rel)
    return R("PASS" if not pdfs and not hits else "FAIL", "no b748a1e7 file; PDFs only under paper/", {"pdfs_outside_paper": pdfs, "b748a1e7_files": hits},
             {"mode": "repository"})

def a6_repo(ctx): return a6_core(os.path.join(ctx["repo_dir"], "scripts"), ctx["budget_sub"])

def witness_export(W):
    """Canonical exact text form of the witness objects (used to write data/witness.json and by A7 to compare)."""
    import sympy as sp
    def c(x):
        a, b = gq(x); return [f"{a.numerator}/{a.denominator}", f"{b.numerator}/{b.denominator}"]
    mat = lambda M: [[c(M[i, j]) for j in range(M.shape[1])] for i in range(M.shape[0])]
    return {"format": "each entry [real, imag] as exact rationals 'p/q'; matrices are lists of rows",
            "parameters": {"lambda^2": "1/2", "m^2": "823/142944", "pi_prime": "1/2", "beta": "1/3", "b1": "1", "b2": "1/3",
                           "q": "lambda*sqrt(2/3)*m (Pauli slice)", "c1": "i*sqrt(3/128)"},
            "xi_star": [str(sp.Rational(x)) for x in W["xi"]], "r": str(W["r"]),
            "det_S0": str(sp.factor(W["S"][0].det())),
            "v": [c(x) for x in W["v"]], "w": [c(x) for x in W["w"]],
            "P_xi_star": mat(W["P"]), "L_xi_star": mat(W["L"]), "S": [mat(S) for S in W["S"]]}

@check("A7", "integrity", "Repository data file data/witness.json equals a fresh exact recomputation of the witness (S, P, L, v, w, r, ξ*, det S⁰)",
       "recompute with witness_min.py, compare the canonical exact text form entry by entry", "data file vs code", "published certificate",
       needs=("repo",))
def a7(ctx):
    W = witness(ctx); fresh = witness_export(W)
    stored = json.load(open(os.path.join(ctx["repo_dir"], "data", "witness.json"), encoding="utf-8"))
    diffs = [k for k in fresh if fresh[k] != stored.get(k)]
    return R("PASS" if not diffs else "FAIL", "identical", {"differing_fields": diffs, "fields_compared": len(fresh)})

# ======================================================================================================
# GROUP B — Clifford algebra, intertwining, representation independence
# ======================================================================================================
@check("B1", "algebra", "Clifford relations and unit-weight Γ^{abc} = full antisymmetrisation", "exact matrix algebra",
       "independent re-derivation of g3 by explicit antisymmetrisation", "core §2 conventions")
def b1(ctx):
    import sympy as sp, itertools
    bd = fresh_defs(ctx); G, eta = bd.G, bd.eta
    cl = all(G[a]*G[b] + G[b]*G[a] == 2*(eta[a] if a == b else 0)*sp.eye(4) for a in range(5) for b in range(5))
    bad = 0
    for a, b, c in itertools.product(range(5), repeat=3):
        anti = sp.zeros(4, 4)
        for perm in itertools.permutations(range(3)):
            inv = sum(1 for i in range(3) for j in range(i + 1, 3) if perm[i] > perm[j]); sign = -1 if inv % 2 else 1
            idx = [(a, b, c)[q] for q in perm]
            anti += sign * G[idx[0]] * G[idx[1]] * G[idx[2]]
        if (anti / 6 - bd.g3(a, b, c)).applyfunc(sp.expand) != sp.zeros(4, 4): bad += 1
    vol = (G[0]*G[1]*G[2]*G[3]*G[4]).applyfunc(sp.expand)
    return R("PASS" if cl and bad == 0 else "FAIL", "Clifford holds; g3 equals antisymmetrisation for all 125 triples",
             {"clifford": cl, "g3_mismatches": bad}, {"Gamma0..4 product (irrep label)": str(vol.tolist())})

@check("B2", "algebra", "INT (Ŷ_μΓ^{μνρ} = Γ^{μνρ}X_μ) at random exact rational F, m, λ", "exact rational arithmetic, random trials",
       "independent of the symbolic polynomial identity of check_1", "core §3 INT")
def b2(ctx):
    import sympy as sp
    from sympy import I, Rational as Q, sqrt
    bd = fresh_defs(ctx); G, eta, g3 = bd.G, bd.eta, bd.g3; n = lv(ctx["level"], 5, 25, 100); bad = 0
    for _ in range(n):
        F = sp.zeros(5, 5)
        for a in range(5):
            for b in range(a + 1, 5):
                q = Q(random.randint(-50, 50), random.randint(1, 30)); F[a, b] = q; F[b, a] = -q
        m = Q(random.randint(1, 99), random.randint(1, 99)); lam = Q(random.randint(1, 99), random.randint(1, 99))
        c1 = I*sqrt(Q(3, 128)); Fs = sum((F[a, b]*G[a]*G[b] for a in range(5) for b in range(5)), sp.zeros(4, 4))
        Gl = [eta[a]*G[a] for a in range(5)]
        X = [-(m/3)*Gl[a] + lam*c1*(Fs*Gl[a] - Gl[a]*Fs/3) for a in range(5)]
        Y = [-(m/3)*Gl[a] + lam*c1*(Gl[a]*Fs - Fs*Gl[a]/3) for a in range(5)]
        for nu in range(5):
            for rho in range(5):
                if sum((Y[u]*g3(u, nu, rho) - g3(u, nu, rho)*X[u] for u in range(5)), sp.zeros(4, 4)).applyfunc(sp.expand) != sp.zeros(4, 4): bad += 1
    return R("PASS" if bad == 0 else "FAIL", "0 failures", f"{bad} failures in {n} random trials x 25 (ν,ρ)", {"trials": n})

@check("B3", "algebra", "L(ξ)L(ξ)† = 3|ξ|² I₄ for SYMBOLIC ξ (all ξ, not only ξ*)", "exact symbolic", "general ξ", "core §9(a) symbol identity")
def b3(ctx):
    import sympy as sp
    bd = fresh_defs(ctx); x = sp.symbols('x1:5', real=True)
    Lm = bd.blk({(0, k - 1): sum((x[j - 1]*bd.g3(0, j, k) for j in range(1, 5)), sp.zeros(4, 4)) for k in range(1, 5)}, 1, 4)
    D = (Lm*Lm.H - 3*sum(v**2 for v in x)*sp.eye(4)).applyfunc(sp.expand)
    return R("PASS" if D == sp.zeros(4, 4) else "FAIL", "zero matrix", "zero" if D == sp.zeros(4, 4) else str(D))

def _invariants(bd, ctx):
    """det S^0, det M, and the exact Jordan data of P(ξ*) at r for the Model built on the module's current Gammas."""
    import sympy as sp, flint
    W = bd.witness_model(); S0 = W.S[0]; detS0 = sp.factor(S0.det())
    xi = [sp.Rational(20, 99), 0, 1, 0]; P = W.Psym(xi); r = sp.Rational(101, 99)
    PR = flint_realrep(P); cp = PR.charpoly(); fac = {str(f): e for f, e in cp.factor()[1]}
    I = flint_eye(32); N = PR - flint.fmpq(101, 99)*I; Nk = I; nul = []
    for k in range(1, 4): Nk = Nk*N; nul.append((32 - Nk.rank())//2)
    dM = flint_realrep(W.Mmat).det()
    return {"det_S0": str(detS0), "|det_M|^2": str(dM), "charpoly_factors_realrep": fac, "nullities_(P-r)^k_k=1..3": nul}

@check("B4", "algebra", "Representation independence: Γ' = SΓS⁻¹ for a random exact S leaves det S⁰, det M and the Jordan data unchanged",
       "rebuild the whole model in a conjugated representation", "different Clifford basis", "convention independence of the witness", needs=("flint",))
def b4(ctx):
    import sympy as sp
    from sympy import I
    bd0 = fresh_defs(ctx); base = _invariants(bd0, ctx)
    # quick/standard: random monomial matrices (permutation × phases ±1, ±i) — genuine basis changes with cheap arithmetic;
    # deep: additionally one dense random Gaussian-integer matrix (slow: sympy must expand large complex fractions)
    # v1.1: three families. "monomial" (permutation × phases) is UNITARY; "scaled-shear" (diagonal rational scaling × an
    # elementary shear, Gaussian-rational entries) and "dense" (random Gaussian-integer) are NON-UNITARY (S†S ≠ I is recorded).
    plan = (["monomial"]*lv(ctx["level"], 1, 2, 2) + ["scaled-shear"]*lv(ctx["level"], 2, 3, 6) + ["dense"]*ctx.get("_dense_trials", 0))
    res = []; bad = 0; trials = len(plan)
    for kind in plan:
        while True:
            if kind == "monomial":
                perm = list(range(4)); random.shuffle(perm); ph = [random.choice([1, -1, I, -I]) for _ in range(4)]
                S = sp.zeros(4, 4)
                for i in range(4): S[i, perm[i]] = ph[i]
            elif kind == "scaled-shear":
                D = sp.diag(*[sp.Rational(random.randint(1, 7), random.randint(1, 7)) for _ in range(4)])
                E = sp.eye(4); i, j = random.sample(range(4), 2); E[i, j] = sp.Rational(random.randint(1, 5), random.randint(1, 5)) + I*random.randint(-2, 2)
                S = D*E
            else:
                S = sp.Matrix(4, 4, lambda i, j: random.randint(-2, 2) + I*random.randint(-2, 2))
            if S.det() != 0 and S != sp.eye(4): break
        unitary = (S.H*S - sp.eye(4)).applyfunc(sp.expand) == sp.zeros(4, 4)
        Si = S.inv(); bd = fresh_defs(ctx, "conj")
        newG = [(S*g*Si).applyfunc(sp.expand) for g in bd.G]; bd.G[:] = newG
        inv = _invariants(bd, ctx); same = (inv == base); bad += (not same); res.append({"kind": kind, "unitary": unitary, "S": str(S.tolist()), "same": same, "inv": inv})
    nonunit = sum(1 for t in res if not t["unitary"])
    return R("PASS" if bad == 0 and nonunit >= 1 else "FAIL", base, f"{trials - bad}/{trials} identical ({nonunit} non-unitary S)", {"trials": res,
             "scope": ("ALGEBRAIC similarity invariants only (det, charpoly, nullities, Jordan structure). A non-unitary S does not preserve the "
                       "standard dagger; Hermiticity statements would need the transformed form H' = (S⁻¹)†HS⁻¹ and are NOT tested here.")})

@check("B6", "algebra", "Representation independence under a DENSER non-unitary Γ' = SΓS⁻¹ (multi-shear at quick/standard; fully dense at deep): same invariants",
       "rebuild the whole model in a dense conjugated representation (slow: sympy expands large complex fractions)", "different Clifford basis",
       "convention independence of the witness", needs=("flint",))
def b6(ctx):
    import sympy as sp
    from sympy import I
    bd0 = fresh_defs(ctx); base = _invariants(bd0, ctx); res = []; bad = 0
    # quick/standard: a "multi-shear" S = D·(I + three Gaussian-rational off-diagonal entries) — non-unitary, non-monomial, affordable;
    # deep: one FULLY dense S (every entry ±1 + i·{−1,0,1}) — exact but slow (~tens of minutes; runs in parallel with the rest)
    for _ in range(1):
        while True:
            if ctx["level"] == "deep":
                S = sp.Matrix(4, 4, lambda i, j: random.choice([-1, 1]) + I*random.choice([-1, 0, 1]))
            else:
                S = sp.eye(4)
                for (i, j) in random.sample([(i, j) for i in range(4) for j in range(4) if i != j], 3):
                    S[i, j] = sp.Rational(random.randint(1, 4), random.randint(1, 4)) + I*random.randint(-1, 1)
                S = sp.diag(*[sp.Rational(random.randint(1, 5), random.randint(1, 5)) for _ in range(4)])*S
            if S.det() != 0: break
        unitary = (S.H*S - sp.eye(4)).applyfunc(sp.expand) == sp.zeros(4, 4)
        Si = S.inv(); bd = fresh_defs(ctx, "dense"); bd.G[:] = [(S*g*Si).applyfunc(sp.expand) for g in bd.G]
        t0 = time.time(); inv = _invariants(bd, ctx); same = inv == base; bad += (not same)
        res.append({"unitary": unitary, "S": str(S.tolist()), "same": same, "inv": inv, "seconds": round(time.time() - t0, 1)})
    ok = bad == 0 and all(not t["unitary"] for t in res)
    return R("PASS" if ok else "FAIL", base, f"{len(res) - bad}/{len(res)} identical ({'fully dense' if ctx['level'] == 'deep' else 'multi-shear'}, non-unitary)", {"trials": res})

@check("B5", "algebra", "The other (inequivalent) 5D Clifford irrep Γ⁴ → −Γ⁴: is the witness structure representation-dependent?",
       "rebuild model with Γ⁴ sign flipped", "inequivalent irrep", "robustness information (not a claim of the paper)", kind="info", needs=("flint",))
def b5(ctx):
    import sympy as sp
    bd0 = fresh_defs(ctx); base = _invariants(bd0, ctx)
    bd = fresh_defs(ctx, "flip"); bd.G[4] = -bd.G[4]
    inv = _invariants(bd, ctx)
    return R("INFO", base, inv, {"identical": inv == base,
             "interpretation": ("Γ⁴ → −Γ⁴ is not a similarity: it switches to the other 5D irrep (sign of the Clifford volume element). "
                                "Agreement = evidence the witness structure survives in the second irrep; disagreement = representation "
                                "dependence of the fixed background data. Neither outcome affects the result in the paper's irrep (core §2). "
                                "Not required to agree.")})

# ======================================================================================================
# GROUP C — Model E geometry from scratch (independent of the frame code), and the operator identities
# ======================================================================================================
def _coord_geometry():
    import sympy as sp
    t, th1, ph1, th2, ph2 = sp.symbols('t th1 ph1 th2 ph2', real=True); b1, b2 = sp.symbols('b1 b2', positive=True)
    x = [t, th1, ph1, th2, ph2]; r1, r2 = 1/b1, 1/b2
    g = sp.diag(-1, r1**2, r1**2*sp.sin(th1)**2, r2**2, r2**2*sp.sin(th2)**2); gi = g.inv()
    Gam = [[[sp.simplify(sum(gi[k, l]*(sp.diff(g[l, i], x[j]) + sp.diff(g[l, j], x[i]) - sp.diff(g[i, j], x[l])) for l in range(5))/2)
             for j in range(5)] for i in range(5)] for k in range(5)]
    E = sp.diag(1, b1, b1/sp.sin(th1), b2, b2/sp.sin(th2))       # E[A, mu] : e_A = E_A^mu d_mu
    e = sp.diag(1, r1, r1*sp.sin(th1), r2, r2*sp.sin(th2))       # coframe e^A_mu
    return dict(x=x, b=(b1, b2), g=g, gi=gi, Gam=Gam, E=E, e=e)

@check("C1", "geometry", "Frame connection ω^A_B(e_C) re-derived from Christoffel symbols equals the one used in all scripts",
       "coordinate Christoffels → frame connection, sympy", "independent derivation from the metric", "core §2 connection; check_2")
def c1(ctx):
    import sympy as sp
    cg = _coord_geometry(); x, Gam, E, e = cg["x"], cg["Gam"], cg["E"], cg["e"]; b1, b2 = cg["b"]
    bd = fresh_defs(ctx); M = bd.Model(sp.Symbol('m'), sp.Symbol('lam'), b1, b2, sp.Symbol('pip'))
    sub = {sp.Symbol(str(s), real=True): s for s in x}
    bad = []
    for C in range(5):
        for B in range(5):
            # (∇_{e_C} e_B)^mu = E_C^nu (d_nu E_B^mu + Γ^mu_{nu lam} E_B^lam)
            vec = [sum(E[C, nu]*(sp.diff(E[B, mu], x[nu]) + sum(Gam[mu][nu][l]*E[B, l] for l in range(5))) for nu in range(5)) for mu in range(5)]
            for A in range(5):
                val = sp.simplify(sum(e[A, mu]*vec[mu] for mu in range(5)))
                ref = sp.sympify(M.om[A][B][C]).subs({bd.th1: x[1], bd.th2: x[3]})
                if sp.simplify(val - ref) != 0: bad.append((A, B, C, str(val), str(ref)))
    return R("PASS" if not bad else "FAIL", "all 125 components agree", f"{len(bad)} disagreements", {"disagreements": bad[:20]})

@check("C2", "geometry", "Einstein tensor G^A_B from the coordinate Riemann tensor equals diag(−(b₁²+b₂²), −b₂², −b₂², −b₁², −b₁²)",
       "coordinate Riemann/Ricci, sympy", "independent derivation", "core §4 (DI on Model E: G^ρ_σ)")
def c2(ctx):
    import sympy as sp
    cg = _coord_geometry(); x, Gam, g, gi, E, e = cg["x"], cg["Gam"], cg["g"], cg["gi"], cg["E"], cg["e"]; b1, b2 = cg["b"]
    def Riem(r, s, m, n):  # R^r_{s m n}
        return (sp.diff(Gam[r][n][s], x[m]) - sp.diff(Gam[r][m][s], x[n])
                + sum(Gam[r][m][l]*Gam[l][n][s] - Gam[r][n][l]*Gam[l][m][s] for l in range(5)))
    Ric = sp.Matrix(5, 5, lambda s, n: sp.simplify(sum(Riem(r, s, r, n) for r in range(5))))
    Rs = sp.simplify(sum(gi[i, j]*Ric[i, j] for i in range(5) for j in range(5)))
    Gmix = sp.Matrix(5, 5, lambda a, b: sp.simplify(sum(gi[a, c]*Ric[c, b] for c in range(5)) - (Rs/2 if a == b else 0)))
    Gframe = sp.Matrix(5, 5, lambda A, B: sp.simplify(sum(e[A, mu]*E[B, nu]*Gmix[mu, nu] for mu in range(5) for nu in range(5))))
    expect = sp.diag(-(b1**2 + b2**2), -b2**2, -b2**2, -b1**2, -b1**2)
    D = (Gframe - expect).applyfunc(sp.simplify)
    # parallel F: ∇_λ F_{μν} = 0 with F = b1 e1∧e2 + b2 e3∧e4
    F = sp.zeros(5, 5); F[1, 2] = b1*e[1, 1]*e[2, 2]; F[2, 1] = -F[1, 2]; F[3, 4] = b2*e[3, 3]*e[4, 4]; F[4, 3] = -F[3, 4]
    nabF = [sp.simplify(sp.diff(F[m, n], x[l]) - sum(Gam[k][l][m]*F[k, n] + Gam[k][l][n]*F[m, k] for k in range(5)))
            for l in range(5) for m in range(5) for n in range(5)]
    # dA = F with A = -r1 cos th1 dph1 - r2 cos th2 dph2 (frame components A_2 = -cot th1, A_4 = -cot th2)
    r1, r2 = 1/b1, 1/b2; Acoord = [0, 0, -r1*sp.cos(x[1]), 0, -r2*sp.cos(x[3])]
    dA = sp.Matrix(5, 5, lambda m, n: sp.simplify(sp.diff(Acoord[n], x[m]) - sp.diff(Acoord[m], x[n])))
    ok = D == sp.zeros(5, 5) and all(v == 0 for v in nabF) and (dA - F).applyfunc(sp.simplify) == sp.zeros(5, 5)
    return R("PASS" if ok else "FAIL", "G^A_B as stated; ∇F = 0; dA = F",
             {"G_frame_minus_expected_zero": D == sp.zeros(5, 5), "nablaF_zero": all(v == 0 for v in nabF),
              "dA_equals_F": (dA - F).applyfunc(sp.simplify) == sp.zeros(5, 5), "scalar_curvature": str(Rs)})

def _concrete_psi(bd, rng):
    import sympy as sp
    t, a1, p1, a2, p2 = bd.COORDS; out = []
    for r in range(5):
        col = []
        for c in range(4):
            q = lambda: sp.Rational(rng.randint(-9, 9), rng.randint(1, 7))
            col.append(q() + q()*t + q()*a1*p2 + q()*sp.sin(p1)*a2 + q()*sp.exp(q()*t)*sp.cos(a1 + q()*p2)
                       + sp.I*(q()*a2**2 + q()*t*p1))
        out.append(sp.Matrix(col))
    return out

def _sample_points(rng, npts):
    """Random interior points plus points within 1% of every θ-boundary of V′ (|θ_i − π/2| → π/3)."""
    pts = []
    for k in range(npts):
        t1 = math.pi/2 + rng.uniform(-1.0, 1.0); t2 = math.pi/2 + rng.uniform(-1.0, 1.0)
        if k % 3 == 1: t1 = math.pi/2 + rng.choice([-1, 1])*(math.pi/3)*rng.uniform(0.99, 0.9999)
        if k % 3 == 2: t2 = math.pi/2 + rng.choice([-1, 1])*(math.pi/3)*rng.uniform(0.99, 0.9999)
        pts.append([rng.uniform(-0.5, 0.5), t1, rng.uniform(-1.0, 1.0), t2, rng.uniform(-1.0, 1.0)])
    return pts

def _mp_eval_residual(exprs, syms, rng, npts, dps, terms=None):
    """Max |residual| and max NORMALISED residual |res| / max(|term_i|) over random + boundary-near points (mpmath, dps digits).
    `terms` = list of lists: for each residual component, the separate pieces whose difference it is (used for scaling)."""
    import sympy as sp, mpmath
    mpmath.mp.dps = dps
    f_res = sp.lambdify(syms, list(exprs), modules="mpmath", cse=True)
    f_terms = [sp.lambdify(syms, list(tl), modules="mpmath", cse=True) for tl in terms] if terms else None
    worst_abs = mpmath.mpf(0); worst_rel = mpmath.mpf(0); worst_scale = mpmath.mpf(0)
    for pt in _sample_points(rng, npts):
        pt = [mpmath.mpf(x) for x in pt]; vals = f_res(*pt)
        for i, v in enumerate(vals):
            a = abs(v); worst_abs = max(worst_abs, a)
            if f_terms:
                sc = max(abs(x) for x in f_terms[i](*pt)); worst_scale = max(worst_scale, sc)
                worst_rel = max(worst_rel, a/sc if sc > 0 else (mpmath.mpf(0) if a == 0 else mpmath.inf))
    return (worst_abs, worst_rel, worst_scale) if terms else worst_abs

@check("C3", "operator", "DI at random points, random concrete fields, random parameters: residual = 0 to 60 digits",
       "high-precision numerical evaluation (mpmath, 60 digits) of the DI residual", "different zero test from check_3 (pointwise, not symbolic)",
       "core §4 DI", kind="numeric", needs=("mpmath",))
def c3(ctx):
    import sympy as sp
    rng = random.Random(ctx["seed"] + 3); bd = fresh_defs(ctx); trials = lv(ctx["level"], 1, 3, 8); worst_all = 0; rows = []
    for k in range(trials):
        if k == 0: M = bd.witness_model(); label = "witness"
        else:
            M = bd.Model(sp.Rational(rng.randint(1, 50), rng.randint(1, 50)), sp.Rational(rng.randint(1, 30), rng.randint(1, 30)),
                         sp.Rational(rng.randint(1, 9), rng.randint(1, 9)), sp.Rational(rng.randint(1, 9), rng.randint(1, 9)), 0); label = "random"
        psi = _concrete_psi(bd, rng); Rr = M.R(psi); lhs = M.div(Rr); rhs = sum((M.S[r]*psi[r] for r in range(5)), sp.zeros(4, 1))
        res = lhs - rhs
        wa, wr, sc = _mp_eval_residual(list(res), bd.COORDS, rng, lv(ctx["level"], 3, 6, 12), 60, terms=[[lhs[i], rhs[i]] for i in range(4)])
        worst_all = max(worst_all, float(wr)); rows.append({"params": label, "max_abs_residual": float(wa), "max_normalised_residual": float(wr), "term_scale": float(sc)})
    return R("PASS" if worst_all < 1e-40 else "FAIL", "normalised residual < 1e-40", f"{worst_all:.3e}", {"trials": rows,
             "scope": "pointwise high-precision falsification test (random + boundary-near points); not a universal zero proof — check_3 (A6) is the symbolic proof; same Model code builds the residual"},
             metric=worst_all, threshold=1e-40)

@check("C4", "operator", "CI at random points, random concrete independent ψ₀, Φ, random parameters (incl. π′): residual = 0 to 60 digits",
       "high-precision numerical evaluation of R⁰[g] − ★R⁰[ψ] + S^ρψ_ρ", "different zero test from check_4", "core §6 CI (B₀)", kind="numeric", needs=("mpmath",))
def c4(ctx):
    import sympy as sp
    rng = random.Random(ctx["seed"] + 4); bd = fresh_defs(ctx); trials = lv(ctx["level"], 1, 2, 6); worst_all = 0; rows = []
    for k in range(trials):
        if k == 0: M = bd.witness_model(); label = "witness"
        else:
            M = bd.Model(sp.Rational(rng.randint(1, 50), rng.randint(1, 50)), sp.Rational(rng.randint(1, 30), rng.randint(1, 30)),
                         sp.Rational(rng.randint(1, 9), rng.randint(1, 9)), sp.Rational(rng.randint(1, 9), rng.randint(1, 9)),
                         sp.Rational(rng.randint(-9, 9), rng.randint(1, 9))); label = "random"
        psi = _concrete_psi(bd, rng); Rr = M.R(psi); g = M.g_of(Rr)
        gpsi = [sp.zeros(4, 1)] + [g[4*(j - 1):4*j, 0] for j in range(1, 5)]
        A = M.R(gpsi)[0]; B = M.star(Rr[0]); C = sum((M.S[r]*psi[r] for r in range(5)), sp.zeros(4, 1)); res = A - B + C
        wa, wr, sc = _mp_eval_residual(list(res), bd.COORDS, rng, lv(ctx["level"], 3, 6, 12), 60, terms=[[A[i], B[i], C[i]] for i in range(4)])
        worst_all = max(worst_all, float(wr)); rows.append({"params": label, "max_abs_residual": float(wa), "max_normalised_residual": float(wr), "term_scale": float(sc)})
    return R("PASS" if worst_all < 1e-40 else "FAIL", "normalised residual < 1e-40", f"{worst_all:.3e}", {"trials": rows,
             "scope": "pointwise high-precision falsification test; check_4 (A6) is the symbolic proof; same Model code builds the residual"},
             metric=worst_all, threshold=1e-40)

@check("C5", "operator", "Curved principal symbol of K′ equals i·Psym(E(y)ᵀk) at OTHER points y and generic covectors (not only y₀, ξ*)",
       "plane-wave extraction, exact rational trig values (sin, cos from Pythagorean triples)", "extends check_5 to y ≠ y₀",
       "core §10 symbols; check_5", kind="exact")
def c5(ctx):
    import sympy as sp
    from sympy import I, Rational as Q
    bd = fresh_defs(ctx); W = bd.witness_model(); Lam = sp.Symbol('Lam', real=True)
    S0i = W.S[0].inv(); Wm = [-S0i*W.S[k] for k in range(1, 5)]; cs = sp.symbols('c0:16')
    triples = [(Q(3, 5), Q(4, 5)), (Q(4, 5), Q(3, 5)), (Q(12, 13), Q(5, 13)), (Q(5, 13), Q(12, 13)), (Q(24, 25), Q(7, 25))]
    npts = lv(ctx["level"], 1, 3, 5); rows = []; bad = 0
    for n in range(npts):
        (s1, c1), (s2, c2) = triples[n % 5], triples[(n + 2) % 5]
        if s1 < sp.Rational(1, 2) or s2 < sp.Rational(1, 2): continue
        xi = [Q(random.randint(-9, 9), random.randint(1, 9)) for _ in range(4)]
        if all(v == 0 for v in xi): xi[0] = 1
        kk = [xi[0]/W.b1, xi[1]*s1/W.b1, xi[2]/W.b2, xi[3]*s2/W.b2]       # ξ = E(y)^T k  with E diag(b1, b1/s1, b2, b2/s2)
        ph = sp.exp(I*Lam*(kk[0]*bd.th1 + kk[1]*bd.ph1 + kk[2]*bd.th2 + kk[3]*bd.ph2))
        Phi = [sp.Matrix(cs[4*j:4*j + 4])*ph for j in range(4)]
        psi = [sum((Wm[k - 1]*Phi[k - 1] for k in range(1, 5)), sp.zeros(4, 1))] + Phi
        Kp = (-W.g_of(W.R(psi))/ph).applyfunc(sp.expand)
        lead = Kp.applyfunc(lambda e: bd.to_poly_trig(e.coeff(Lam, 1)).subs({bd.S1: s1, bd.C1: c1, bd.S2: s2, bd.C2: c2}))
        P = W.Psym(xi); D = (lead - I*P*sp.Matrix(cs)).applyfunc(sp.expand)
        ok = all(v == 0 for v in D); bad += (not ok); rows.append({"sin_th1": str(s1), "sin_th2": str(s2), "xi": [str(v) for v in xi], "ok": ok})
    return R("PASS" if bad == 0 and rows else "FAIL", "lead coefficient == i P(ξ) at every tested point", f"{len(rows) - bad}/{len(rows)}", {"points": rows})

# ======================================================================================================
# GROUP D — the witness, recomputed with three arithmetic engines
# ======================================================================================================
@check("D1", "witness", "Jordan chain Lv = Lw = 0, (P−r)v = 0, (P−r)w = v, v ≠ 0 in pure-Python Gaussian rationals",
       "fractions.Fraction arithmetic (no sympy, no FLINT in the check)", "third arithmetic engine", "core §10 witness chain")
def d1(ctx):
    W = witness(ctx); import sympy as sp
    N = gmat(W['P'] - W['r']*sp.eye(16)); L = gmat(W['L']); v = gvec(W['v']); w = gvec(W['w'])
    Nw = gmv(N, w)
    res = {"L v = 0": gzero(gmv(L, v)), "L w = 0": gzero(gmv(L, w)), "(P-r) v = 0": gzero(gmv(N, v)),
           "(P-r) w = v": all(a == b for a, b in zip(Nw, v)), "v != 0": not gzero(v)}
    return R("PASS" if all(res.values()) else "FAIL", "all True", res)

@check("D2", "witness", "Exact Jordan structure of P(ξ*) at r = 101/99 (FLINT): algebraic multiplicity 6, two J₂ blocks; full spectrum",
       "FLINT exact charpoly, factorisation and ranks of (P−r)^k in the real representation", "independent engine (FLINT)",
       "GEN14 Direction A / G-66 multiplicity pattern; core §10", needs=("flint",))
def d2(ctx):
    import flint, sympy as sp
    W = witness(ctx); PR = flint_realrep(W['P']); cp = PR.charpoly(); fac = {str(f): e for f, e in cp.factor()[1]}
    I = flint_eye(32); N = PR - flint.fmpq(101, 99)*I; Nk = I; nul = []
    for k in range(1, 5): Nk = Nk*N; nul.append((32 - Nk.rank())//2)
    mult = fac.get("99*x + (-101)", 0)//2
    blocks = {f"size>={k}": nul[k - 1] - (nul[k - 2] if k > 1 else 0) for k in range(1, 5)}
    ok = mult == 6 and nul[:3] == [4, 6, 6]
    LR = flint_realrep(W['L']); rankL = LR.rank()//2
    return R("PASS" if ok and rankL == 4 else "FAIL", {"alg_mult": 6, "nullities": [4, 6, 6, 6], "rank_L": 4},
             {"alg_mult": mult, "nullities": nul, "rank_L": rankL}, {"charpoly_factors_realrep": fac, "blocks": blocks,
              "reading": "nullities 4,6 => 2 blocks of size 2 and 2 of size 1 at r"})

@check("D3", "witness", "det S⁰ and det M recomputed by FLINT (|det|² in the real representation) and by sympy",
       "two engines", "independent engine", "core §5 ELIM (det S⁰ ≠ 0), det M = 81", needs=("flint",))
def d3(ctx):
    import flint, sympy as sp
    W = witness(ctx); S0 = W['S'][0]; d_sym = sp.factor(S0.det()); ok1 = str(d_sym) == DET_S0
    d_fl = flint_realrep(S0).det(); mod2 = sp.Rational(int(d_fl.p), int(d_fl.q)); ok2 = mod2 == sp.Rational(DET_S0)**2 * 1  # real det for real d
    dM = flint_realrep(W['MM']).det(); okM = sp.Rational(int(dM.p), int(dM.q)) == 81**2
    return R("PASS" if ok1 and ok2 and okM else "FAIL", {"det_S0": DET_S0, "det_M": 81},
             {"det_S0_sympy": str(d_sym), "|det_S0|^2_flint": str(mod2), "|det_MM|^2_flint": str(sp.Rational(int(dM.p), int(dM.q)))})

@check("D4", "witness", "a_γ identity (γ − i(P−r))a_γ = −iγ²w at many random exact rational γ (pure Python)",
       "exact rational γ, Fraction arithmetic", "consistency (follows from D1)", "core §10 contradiction step")
def d4(ctx):
    import sympy as sp
    W = witness(ctx); N = gmat(W['P'] - W['r']*sp.eye(16)); L = gmat(W['L']); v = gvec(W['v']); w = gvec(W['w'])
    n = lv(ctx["level"], 10, 50, 200); bad = 0
    for _ in range(n):
        g = Fr(random.randint(1, 10**6), random.randint(1, 10**6))
        a = [gadd(vi, gmul((Fr(0), -g), wi)) for vi, wi in zip(v, w)]
        Na = gmv(N, a); lhs = [gadd(gmul((g, Fr(0)), ai), gmul((Fr(0), Fr(-1)), nai)) for ai, nai in zip(a, Na)]
        rhs = [gmul((Fr(0), -g*g), wi) for wi in w]
        if not (lhs == rhs and gzero(gmv(L, a))): bad += 1
    return R("PASS" if bad == 0 else "FAIL", "0 failures", f"{bad} failures / {n} random γ")

WITNESS_HASH_CODE = r"""
import runpy, io, contextlib, json, hashlib, sys, sympy as sp
with contextlib.redirect_stdout(io.StringIO()):
    W = runpy.run_path(sys.argv[1])
obj = {k: str(W[k].tolist()) for k in ("P", "L", "v", "w")}
obj.update({"r": str(W["r"]), "xi": str(W["xi"]), "S": [str(x.tolist()) for x in W["S"]], "det_S0": str(sp.factor(W["S"][0].det()))})
print(hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest())
"""

@check("D5", "witness", "Determinism: full witness objects (S, P, L, v, w, r, ξ, det S⁰) hash identically in this process and in a fresh subprocess; P agrees across the two codebases",
       "sha256 of the serialised objects, computed twice (second in a new interpreter)", "fresh process", "reproducibility")
def d5(ctx):
    import sympy as sp
    wm = os.path.join(ctx["embed_dir"], "witness_min.py")
    buf = io.StringIO(); old = sys.argv
    try:
        sys.argv = ["x", wm]
        with contextlib.redirect_stdout(buf): exec(compile(WITNESS_HASH_CODE, "witness_hash", "exec"), {"__name__": "__wh__"})
    finally:
        sys.argv = old
    h1 = buf.getvalue().strip()
    p = subprocess.run([sys.executable, "-c", WITNESS_HASH_CODE, wm], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=ctx["budget_sub"])
    h2 = p.stdout.strip()
    bd = fresh_defs(ctx); P2 = bd.witness_model().Psym([sp.Rational(20, 99), 0, 1, 0]); W = witness(ctx)
    same_P = (P2 - W['P']).applyfunc(sp.expand) == sp.zeros(16, 16)
    conds = {"hash_run1_equals_run2_fresh_process": bool(h1) and h1 == h2, "subprocess_exit_0": p.returncode == 0,
             "P_equal_across_codebases (witness_min.py vs bhmap_defs.py)": same_P}
    return R("PASS" if all(conds.values()) else "FAIL", "all true", conds, {"hash_run1": h1, "hash_run2": h2, "stderr": p.stderr[-500:]})

# ======================================================================================================
# GROUP E — analytic lemmas: numerical falsification attempts
# ======================================================================================================
def _bump_field(np, grid, rng, R0, kind, h):
    """Smooth, well-resolved test function: Gaussian envelope (width R0 ≥ 3h) times a modulation whose
    frequencies stay below 25% of the grid Nyquist frequency (so the discrete norms are accurate)."""
    X = np.stack(np.meshgrid(*grid, indexing="ij"), 0); r2 = (X**2).sum(0); fmax = 0.25*np.pi/h
    env = np.exp(-r2/(2*R0**2))
    if kind == 0: mod = 1.0 + sum(rng.normal()*X[i] for i in range(X.shape[0]))
    elif kind == 1: mod = np.exp(1j*sum(rng.uniform(-1, 1)*fmax*X[i] for i in range(X.shape[0])))
    else: mod = sum(rng.normal()*np.cos(rng.uniform(0, fmax)*X[i] + rng.uniform(0, 6)) for i in range(X.shape[0]))
    return env*mod

def _compact_field(np, grid, rng, R0, kind, h):
    """Genuinely compactly supported C^∞ test function: exp(−1/(1−|x|²/R0²)) on |x| < R0, 0 outside, times a modulation
    below 25% of Nyquist. Requires R0 well inside the box (zero at the periodic boundary)."""
    X = np.stack(np.meshgrid(*grid, indexing="ij"), 0); r2 = (X**2).sum(0); fmax = 0.25*np.pi/h
    inside = r2 < R0**2; bump = np.zeros_like(r2); bump[inside] = np.exp(-1.0/(1.0 - r2[inside]/R0**2))
    if kind == 0: mod = 1.0 + sum(rng.normal()*X[i]/R0 for i in range(X.shape[0]))
    elif kind == 1: mod = np.exp(1j*sum(rng.uniform(-1, 1)*fmax*X[i] for i in range(X.shape[0])))
    else: mod = sum(rng.normal()*np.cos(rng.uniform(0, fmax)*X[i] + rng.uniform(0, 6)) for i in range(X.shape[0]))
    return bump*mod

def _lemma41_ratio(np, g, h, Lk_vec, weight=None):
    d = g.ndim; n = g.shape[0]; f = g if weight is None else weight*g
    gh = np.fft.fftn(g)*h**d; fh = np.fft.fftn(f)*h**d
    z = [2*np.pi*np.fft.fftfreq(n, d=h)]*d; Z = np.stack(np.meshgrid(*z, indexing="ij"), 0); dz = (2*np.pi/(n*h))**d/(2*np.pi)**d
    z2 = (Z**2).sum(0); Zs = sum((Z[i] + Lk_vec[i])**2 for i in range(d))
    # f e^{iΛk·y}: Fourier transform shifted by Λk; evaluate the H^-1 weight at ζ+Λk (exact shift, no grid alignment needed)
    Hm1 = math.sqrt(float((np.abs(fh)**2/(1 + Zs)).sum()*dz))
    L2 = math.sqrt(float((np.abs(gh)**2).sum()*dz)); D2 = math.sqrt(float((z2**2*np.abs(gh)**2).sum()*dz))
    a = float(np.sqrt(sum(v*v for v in Lk_vec)))
    return Hm1, L2, D2, a

@check("E1", "analysis", "Lemma 4.1 (oscillatory H⁻¹ bound, m = 1): ‖e^{iΛk·y}g‖_{H⁻¹} ≤ 2(Λ|k|)⁻¹‖g‖ + 4(Λ|k|)⁻²‖D²g‖, d = 1,2,4; compact C^∞ and Gaussian families; grid-refinement record",
       "FFT on periodic boxes; compactly supported bumps (primary) and Gaussians (supplementary); many Λ, k; refinement n → 2n",
       "numerical falsification attempt", "R1 v2 Lemma 4.1 (the R1 crux)", kind="numeric", needs=("numpy",))
def e1(ctx):
    import numpy as np
    rng = np.random.default_rng(ctx["seed"] + 41); worst = {"compact": 0.0, "gaussian": 0.0}; rows = []
    cfg = {1: (40.0, lv(ctx["level"], 2048, 8192, 32768)), 2: (40.0, lv(ctx["level"], 128, 384, 768)), 4: (12.0, lv(ctx["level"], 24, 32, 48))}
    trials = lv(ctx["level"], 6, 30, 120)
    for d, (Lbox, n) in cfg.items():
        h = Lbox/n; grid = [(np.arange(n) - n//2)*h]*d
        for t in range(trials if d < 4 else max(4, trials//6)):
            fam = "compact" if t % 2 == 0 else "gaussian"
            if fam == "compact": g = _compact_field(np, grid, rng, R0=rng.uniform(0.25, 0.38)*Lbox, kind=(t//2) % 3, h=h)
            else: g = _bump_field(np, grid, rng, R0=rng.uniform(max(1.0, 3*h), 3.0), kind=(t//2) % 3, h=h)
            k = rng.normal(size=d); k /= np.linalg.norm(k); Lam = float(10**rng.uniform(-1, 2.5))
            Hm1, L2, D2, a = _lemma41_ratio(np, g, h, Lam*k)
            ratio = Hm1/(2*L2/a + 4*D2/a**2); worst[fam] = max(worst[fam], ratio)
            rows.append({"d": d, "n": n, "family": fam, "Lambda|k|": a, "ratio_LHS_over_RHS": ratio})
    # grid refinement: the same compact function on n and 2n points (same box) — norms must agree
    refine = {}
    for d, (Lbox, n) in ((1, (40.0, 2048)), (2, (40.0, 128))):
        vals = []
        for nn in (n, 2*n):
            hh = Lbox/nn; gr = [(np.arange(nn) - nn//2)*hh]*d; rr = np.random.default_rng(99)
            g = _compact_field(np, gr, rr, R0=10.0, kind=0, h=Lbox/n); kk = np.zeros(d); kk[0] = 7.0
            vals.append(_lemma41_ratio(np, g, hh, kk))
        rel = [abs(vals[1][i] - vals[0][i])/abs(vals[1][i]) for i in range(3)]
        refine[f"d={d}: n={n} vs {2*n}"] = {"rel_change_[H-1, L2, D2]": rel}
    ref_ok = all(max(v["rel_change_[H-1, L2, D2]"]) < 1e-3 for v in refine.values())
    w = max(worst.values())
    return R("PASS" if w <= 1.0 and ref_ok else "FAIL", "max ratio ≤ 1 in both families; refinement change < 1e-3",
             {"max_ratio_compact": worst["compact"], "max_ratio_gaussian": worst["gaussian"], "refinement_ok": ref_ok},
             {"refinement": refine, "samples": rows[:400], "count": len(rows),
              "norm_note": ("H¹ = L² + ‖∇‖² (R1 v2 convention); H⁻¹ weight (1+|ζ+Λk|²)⁻¹ applied with an exact shift; ‖D²g‖² = ∫|ζ|⁴|ĝ|². "
                            "This is the FULL-SPACE H⁻¹(ℝ^d) norm of the zero extension, which is ≥ the local H⁻¹(B′) norm "
                            "(more test functions), so a full-space pass is the stronger statement. Not an equality with the local norm.")},
             metric=w, threshold=1.0)

@check("E2", "analysis", "Lemma 4.1 adversarial: optimiser tries to MAXIMISE LHS/RHS over g (Gaussian mixtures with modulations), d = 1, 2",
       "scipy Nelder–Mead / differential evolution on the ratio", "active search for a counterexample", "R1 v2 Lemma 4.1",
       kind="numeric", needs=("numpy", "scipy"))
def e2(ctx):
    import numpy as np
    from scipy.optimize import differential_evolution
    rng = np.random.default_rng(ctx["seed"] + 42); results = []; worst = 0.0
    for d, n in ((1, lv(ctx["level"], 2048, 4096, 16384)), (2, lv(ctx["level"], 128, 256, 512))):
        Lbox = 40.0 if d == 1 else 20.0; h = Lbox/n; grid = [(np.arange(n) - n//2)*h]*d; wmin = 0.05 if d == 1 else 3*h
        X = np.stack(np.meshgrid(*grid, indexing="ij"), 0); r2 = (X**2).sum(0)
        cut = np.where(r2 < 64, np.exp(-1.0/np.maximum(1e-300, 1 - r2/64)), 0.0)
        Lam = float(lv(ctx["level"], 5.0, 5.0, 5.0)); k = np.zeros(d); k[0] = 1.0
        def neg(p):
            c = p.reshape(-1, 2 + d)[:3]; g = np.zeros_like(r2, dtype=complex)
            for row in c:
                amp, wid, *fr = row; g = g + amp*np.exp(-r2/(wmin + abs(wid))**2)*np.exp(1j*sum(fr[i]*X[i] for i in range(d)))
            g = g*cut
            Hm1, L2, D2, a = _lemma41_ratio(np, g, h, Lam*k)
            return -(Hm1/(2*L2/a + 4*D2/a**2 + 1e-300))
        fm = min(2*Lam, 0.25*np.pi/h); bounds = [(-1, 1), (0.0, 4)] + [(-fm, fm)]*d
        res = differential_evolution(neg, bounds*3, maxiter=lv(ctx["level"], 15, 60, 200), seed=int(rng.integers(1 << 30)),
                                     polish=True, tol=1e-10, workers=1)
        results.append({"d": d, "n": n, "Lambda|k|": Lam, "max_ratio_found": -res.fun, "nfev": int(res.nfev)}); worst = max(worst, -res.fun)
    return R("PASS" if worst <= 1.0 else "FAIL", "optimiser cannot exceed 1", f"best ratio found {worst:.6f}", {"runs": results}, metric=worst, threshold=1.0)

@check("E3", "analysis", "Lemma 4.1 weighted form ‖m·e^{iΛk·y}g‖_{H⁻¹} ≤ C_m(…): synthetic densities in d = 1, 2 AND the actual Model E density μ = 9 sinθ₁ sinθ₂ in d = 4 with the analytic C_m",
       "FFT; compactly supported g inside V′; analytic C_m = 9 + 9√3/2 for μ on V′ (sampled value also recorded)", "numerical falsification attempt",
       "R1 v2 Lemma 4.1 (C_m)", kind="numeric", needs=("numpy",))
def e3(ctx):
    import numpy as np
    rng = np.random.default_rng(ctx["seed"] + 43); worst = 0.0; rows = []
    for d, n in ((1, lv(ctx["level"], 2048, 8192, 16384)), (2, lv(ctx["level"], 128, 256, 512))):
        Lbox = 40.0; h = Lbox/n; grid = [(np.arange(n) - n//2)*h]*d; X = np.stack(np.meshgrid(*grid, indexing="ij"), 0)
        for t in range(lv(ctx["level"], 6, 24, 80)):
            sc = rng.uniform(0.2, 1.0)
            m = 9*np.prod([np.sin(np.pi/2 + (np.pi/3)*np.tanh(sc*X[i])) for i in range(d)], axis=0)
            grads = np.gradient(m, h); gn = np.sqrt(sum(gi**2 for gi in (grads if d > 1 else [grads])))
            Cm = float(m.max() + gn.max())*1.001   # finite-difference estimate of the sup, +0.1% margin (synthetic densities only)
            g = _compact_field(np, grid, rng, R0=rng.uniform(4, 14), kind=t % 3, h=h)
            k = rng.normal(size=d); k /= np.linalg.norm(k); Lam = float(10**rng.uniform(-0.5, 2.5))
            Hm1, L2, D2, a = _lemma41_ratio(np, g, h, Lam*k, weight=m)
            ratio = Hm1/(Cm*(2*L2/a + 4*D2/a**2)); worst = max(worst, ratio); rows.append({"d": d, "density": "synthetic", "Lambda|k|": a, "C_m": Cm, "ratio": ratio})
    # actual Model E density in the 4D chart (x = y − y₀; θ₁ = π/2 + x₀, θ₂ = π/2 + x₂): μ = 9 cos x₀ cos x₂
    n4 = lv(ctx["level"], 20, 28, 40); Lb = 2.4; h4 = Lb/n4; grid4 = [(np.arange(n4) - n4//2)*h4]*4
    X4 = np.stack(np.meshgrid(*grid4, indexing="ij"), 0); mu = 9*np.cos(X4[0])*np.cos(X4[2])
    Cm_analytic = 9 + 9*math.sqrt(3)/2       # sup μ = 9; sup|∇μ| = 9·max√(sin²a cos²b + cos²a sin²b) = 9·√(3/4) on |a|,|b| ≤ π/3
    gx = 9*np.sqrt((np.sin(X4[0])*np.cos(X4[2]))**2 + (np.cos(X4[0])*np.sin(X4[2]))**2); inside = (X4**2).sum(0) < 1.0
    Cm_sampled = float(mu[inside].max() + gx[inside].max())
    for t in range(lv(ctx["level"], 3, 8, 20)):
        g = _compact_field(np, grid4, rng, R0=1.0, kind=t % 3, h=h4)
        k = rng.normal(size=4); k /= np.linalg.norm(k); Lam = float(10**rng.uniform(0, 2.5))
        Hm1, L2, D2, a = _lemma41_ratio(np, g, h4, Lam*k, weight=mu)
        ratio = Hm1/(Cm_analytic*(2*L2/a + 4*D2/a**2)); worst = max(worst, ratio); rows.append({"d": 4, "density": "Model E μ", "Lambda|k|": a, "C_m": Cm_analytic, "ratio": ratio})
    ok = worst <= 1.0 and Cm_sampled <= Cm_analytic + 1e-9
    return R("PASS" if ok else "FAIL", "max ratio ≤ 1; sampled C_m ≤ analytic C_m", {"max_ratio": worst, "Cm_analytic_ModelE": Cm_analytic, "Cm_sampled_ModelE": Cm_sampled},
             {"samples": rows, "norm_note": "‖f‖_{H⁻¹_μ} = ‖m f‖ in the antidual of H¹₀ under (f,φ)_μ; computed as the full-space norm of the zero extension (≥ local norm)."},
             metric=worst, threshold=1.0)

def _L_chart(np, th1, th2, k, Lj_frame):
    b1, b2 = 1.0, 1/3; xi = np.array([b1*k[0], b1*k[1]/np.sin(th1), b2*k[2], b2*k[3]/np.sin(th2)])
    return sum(xi[j]*Lj_frame[j] for j in range(4)), xi

@check("E4", "analysis", "COER constants: EXACT sub-checks (B_aB_a† = 3I so ‖[Γ^{0ak}]_k‖ = √3; |d/dθ(1/sinθ)| ≤ 2√3 on V′) plus randomized sampling of V′ incl. boundary points: σ_min(L(y,k)†) ≥ |k|/√3, freezing ≤ ℓ₁|y−y₀|",
       "sympy exact facts behind core §9(a),(c) + numpy randomized sampling (interior and within 1e-9 of the θ-boundaries)",
       "independent check of core §9(a),(c)", "core §9 COER constants",
       kind="numeric", needs=("numpy",))
def e4(ctx):
    import numpy as np, sympy as sp
    bd = fresh_defs(ctx)
    Lf = [np.array(sp.N(bd.blk({(0, kk - 1): bd.g3(0, j, kk) for kk in range(1, 5)}, 1, 4)).tolist(), dtype=complex) for j in range(1, 5)]
    rng = np.random.default_rng(ctx["seed"] + 44); n = lv(ctx["level"], 2000, 40000, 400000)
    th1 = np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, n); th2 = np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, n)
    worst_sig = np.inf; worst_id = 0.0
    for i in range(n):
        k = rng.normal(size=4); Lm, xi = _L_chart(np, th1[i], th2[i], k, Lf)
        s = np.linalg.svd(Lm.conj().T, compute_uv=False).min() / np.linalg.norm(k); worst_sig = min(worst_sig, s)
        worst_id = max(worst_id, np.abs(Lm @ Lm.conj().T - 3*np.dot(xi, xi)*np.eye(4)).max()/max(1e-300, np.dot(xi, xi)))
    # freezing: (Σ_j ||L_j(y) − L_j(y0)||²)^{1/2} ≤ ℓ1 |y − y0|,  L_j(y) = chart coefficient of ∂_j
    ell1 = 6*math.sqrt(1 + 1/9); worst_fr = 0.0
    def Lj(t1, t2): return [1.0*Lf[0], Lf[1]/np.sin(t1), (1/3)*Lf[2], (1/3)*Lf[3]/np.sin(t2)]
    L0 = Lj(np.pi/2, np.pi/2)
    for i in range(min(n, 50000)):
        y = np.array([th1[i] - np.pi/2, rng.uniform(-np.pi/3, np.pi/3), th2[i] - np.pi/2, rng.uniform(-np.pi/3, np.pi/3)])
        Ly = Lj(th1[i], th2[i]); num = math.sqrt(sum(np.linalg.norm(a - b, 2)**2 for a, b in zip(Ly, L0)))
        dist = np.linalg.norm(y); worst_fr = max(worst_fr, num/dist if dist > 1e-12 else 0)
    # boundary points: θ_i at π/2 ± (π/3)(1 − 1e-9), all sign combinations, random covectors
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            t1 = np.pi/2 + s1*(np.pi/3)*(1 - 1e-9); t2 = np.pi/2 + s2*(np.pi/3)*(1 - 1e-9)
            for _ in range(200):
                k = rng.normal(size=4); Lm, xi = _L_chart(np, t1, t2, k, Lf)
                worst_sig = min(worst_sig, np.linalg.svd(Lm.conj().T, compute_uv=False).min()/np.linalg.norm(k))
                y = np.array([t1 - np.pi/2, rng.uniform(-np.pi/3, np.pi/3), t2 - np.pi/2, rng.uniform(-np.pi/3, np.pi/3)])
                num = math.sqrt(sum(np.linalg.norm(a - b, 2)**2 for a, b in zip(Lj(t1, t2), L0))); worst_fr = max(worst_fr, num/np.linalg.norm(y))
    # exact facts: (1) each block row B_a = [Γ^{0ak}]_k satisfies B_a B_a† = 3 I  ⇒ ‖B_a‖ = √3 exactly;
    # (2) d/dθ(cos θ / sin²θ) = −(1 + cos²θ)/sin³θ < 0 on (0, π) ⇒ |d/dθ(1/sinθ)| = |cosθ|/sin²θ is maximal at the V′ endpoints, = 2√3.
    th = sp.Symbol('th'); ex_ok = True; facts = {}
    for a_ in range(1, 5):
        B = bd.blk({(0, kk - 1): bd.g3(0, a_, kk) for kk in range(1, 5)}, 1, 4)
        facts[f"B_{a_} B_{a_}^dag == 3I"] = (B*B.H - 3*sp.eye(4)).applyfunc(sp.expand) == sp.zeros(4, 4); ex_ok &= facts[f"B_{a_} B_{a_}^dag == 3I"]
    dg = sp.simplify(sp.diff(sp.cos(th)/sp.sin(th)**2, th) + (1 + sp.cos(th)**2)/sp.sin(th)**3)
    facts["d/dθ(cosθ/sin²θ) == −(1+cos²θ)/sin³θ"] = dg == 0
    facts["|cosθ|/sin²θ at θ = π/6 equals 2√3"] = sp.simplify(sp.cos(sp.pi/6)/sp.sin(sp.pi/6)**2 - 2*sp.sqrt(3)) == 0
    ex_ok &= facts["d/dθ(cosθ/sin²θ) == −(1+cos²θ)/sin³θ"] and facts["|cosθ|/sin²θ at θ = π/6 equals 2√3"]
    sig = 1/math.sqrt(3)
    ok = worst_sig >= sig*(1 - 1e-12) and worst_id < 1e-12 and worst_fr <= ell1 and ex_ok
    return R("PASS" if ok else "FAIL", {"sigma_min/|k| >=": sig, "LLdag identity err <": 1e-12, "freezing ratio <= ell1": ell1},
             {"min sigma/|k|": worst_sig, "max identity err": worst_id, "max freezing ratio": worst_fr, "exact_facts_all_true": bool(ex_ok)},
             {"samples": int(n), "exact_facts": facts, "scope": "randomized sampling is a falsification test; the exact facts are the proof ingredients of core §9(a),(c)"},
             metric=worst_sig, threshold=sig)

def _geo_dist(np, y, z):
    def ang(t1, p1, t2, p2):
        c = np.sin(t1)*np.sin(t2)*np.cos(p1 - p2) + np.cos(t1)*np.cos(t2); return np.arccos(np.clip(c, -1, 1))
    return np.sqrt(ang(y[0], y[1], z[0], z[1])**2 + (3*ang(y[2], y[3], z[2], z[3]))**2)

@check("E5", "geometry", "Ball geometry: B_d(y₀,ρ) ⊂ B_e(y₀,2ρ) ⊂ V′ and B_e(y₀,ρ/3) ⊂ B_d(y₀,ρ) for ρ ≤ π/6; d(y,y₁) ≤ 3|y−y₁| on V′; 9/4 ≤ μ ≤ 9; ¼I ≤ g ≤ 9I",
       "exact closed-form geodesic distance on S²(1)×S²(3), random sampling", "independent of all proof text", "core §9(f), §10 BT3, COER weight bounds",
       kind="numeric", needs=("numpy",))
def e5(ctx):
    import numpy as np
    rng = np.random.default_rng(ctx["seed"] + 45); n = lv(ctx["level"], 20000, 400000, 4000000); y0 = np.array([np.pi/2, 0, np.pi/2, 0])
    viol = {"Bd_in_Be2rho": 0, "Be2rho_in_V": 0, "Be_rho3_in_Bd": 0, "d_le_3euclid": 0, "mu_bounds": 0, "metric_bounds": 0}
    for _ in range(max(1, n//100000) if n > 100000 else 1):
        m = min(n, 100000)
        Y = np.stack([np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m),
                      np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m)])
        d0 = _geo_dist(np, Y, y0[:, None]); e0 = np.linalg.norm(Y - y0[:, None], axis=0)
        for rho in (np.pi/6, np.pi/12, 0.1, 0.01):
            inBd = d0 < rho; viol["Bd_in_Be2rho"] += int(np.sum(inBd & ~(e0 < 2*rho)))
            viol["Be_rho3_in_Bd"] += int(np.sum((e0 < rho/3) & ~inBd))
        Z = np.stack([np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m),
                      np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m)])
        viol["d_le_3euclid"] += int(np.sum(_geo_dist(np, Y, Z) > 3*np.linalg.norm(Y - Z, axis=0)*(1 + 1e-12)))
        mu = 9*np.sin(Y[0])*np.sin(Y[2]); viol["mu_bounds"] += int(np.sum((mu < 9/4 - 1e-12) | (mu > 9 + 1e-12)))
        gdiag = np.stack([np.ones(m), np.sin(Y[0])**2, 9*np.ones(m), 9*np.sin(Y[2])**2])
        viol["metric_bounds"] += int(np.sum((gdiag < 0.25 - 1e-12) | (gdiag > 9 + 1e-12)))
    # B_e(y0, 2ρ) ⊂ V′ for ρ ≤ π/6 holds iff 2ρ ≤ π/3 = half-width of V′ in every coordinate (open box): check the worst case exactly
    viol["Be2rho_in_V"] = 0 if 2*(np.pi/6) <= np.pi/3 + 1e-15 else 1
    import sympy as sp
    facts = {   # exact ingredients of the analytic proof (core §9(f), §10 BT3)
        "sin² on [π/6, 5π/6] has min 1/4 (endpoints) and max 1": sp.sin(sp.pi/6)**2 == sp.Rational(1, 4) and sp.sin(sp.pi/2)**2 == 1,
        "g = diag(1, sin²θ₁, 9, 9 sin²θ₂): min entry over V′ = 1/4, max = 9": (min(1, sp.Rational(1, 4), 9, 9*sp.Rational(1, 4)) == sp.Rational(1, 4)
                                                                              and max(1, 1, 9, 9) == 9),
        "μ = √det g = 9 sinθ₁ sinθ₂: 9·(1/2)(1/2) = 9/4 and 9·1·1 = 9": 9*sp.Rational(1, 2)**2 == sp.Rational(9, 4),
        "chart containment: 2ρ ≤ π/3 for ρ ≤ π/6 (exact)": sp.simplify(2*sp.pi/6 - sp.pi/3) == 0,
        "argument": ("g ≥ ¼I ⇒ a curve leaving V′ from y₀ has Euclidean length ≥ π/3 hence g-length ≥ π/6, so for ρ ≤ π/6 every point of "
                     "B_d(y₀,ρ) is reached inside V′ by a curve of Euclidean length < 2ρ ⇒ B_d ⊂ B_e(2ρ) ⊂ V′; g ≤ 9I and convexity of V′ ⇒ "
                     "d(y,y₁) ≤ 3|y−y₁| (straight segment) ⇒ B_e(ρ/3) ⊂ B_d(ρ). The sampling above tests the implementation of these facts."),
    }
    return R("PASS" if all(v == 0 for v in viol.values()) else "FAIL", "0 violations", viol, {"samples": int(n), "analytic": facts,
             "scope": "random sampling detects implementation errors; it does not prove the inclusions — the analytic argument does"})

@check("E6", "geometry", "BT2 + density: exact vol_μ(B_d(y₀,ρ)) is continuous, strictly increasing; Monte-Carlo with μ = 9 sinθ₁ sinθ₂ matches it",
       "closed-form volume on S²(1)×S²(3) vs Monte-Carlo in the chart", "two independent computations", "core §10 BT2; μ = Riemannian density",
       kind="numeric", needs=("numpy", "scipy"))
def e6(ctx):
    import numpy as np
    from scipy.integrate import quad
    def vexact(rho):   # ∫∫_{α1²+9α2²<ρ²} (2π sin α1)(2π·9 sin α2) dα1 dα2, inner integral done in closed form
        return quad(lambda a1: 2*np.pi*np.sin(a1)*18*np.pi*(1 - np.cos(np.sqrt(max(rho**2 - a1**2, 0))/3)), 0, rho, epsabs=0, epsrel=1e-13)[0]
    rhos = np.linspace(0.02, np.pi/6, 60); V = np.array([vexact(r) for r in rhos]); inc = np.diff(V); mono = bool(np.all(inc > 0))
    dV = [abs(vexact(r + 1e-9) - vexact(r)) for r in rhos]
    rng = np.random.default_rng(ctx["seed"] + 46); n = lv(ctx["level"], 400000, 4000000, 40000000); y0 = np.array([np.pi/2, 0, np.pi/2, 0])
    test = [np.pi/6, np.pi/8, 0.3]; acc = {r: [0.0, 0.0] for r in test}; tot = 0
    for _ in range(max(1, n//1000000)):
        m = min(n, 1000000); Y = np.stack([np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m),
                                           np.pi/2 + rng.uniform(-np.pi/3, np.pi/3, m), rng.uniform(-np.pi/3, np.pi/3, m)])
        d0 = _geo_dist(np, Y, y0[:, None]); w = 9*np.sin(Y[0])*np.sin(Y[2])
        for r in test: x = w*(d0 < r); acc[r][0] += float(x.sum()); acc[r][1] += float((x*x).sum())
        tot += m
    box = (2*np.pi/3)**4; z = {}
    for r in test:
        mean = acc[r][0]/tot; var = acc[r][1]/tot - mean**2; est = mean*box; se = box*np.sqrt(var/tot)
        z[str(round(r, 4))] = {"exact": vexact(r), "monte_carlo": est, "std_err": se, "z": (est - vexact(r))/se}
    def dV_exact(rho):   # V'(ρ) by differentiating under the integral (the boundary term vanishes since 1 − cos 0 = 0)
        f = lambda a1: 2*np.pi*np.sin(a1)*18*np.pi*np.sin(np.sqrt(max(rho**2 - a1**2, 1e-300))/3)*rho/(3*np.sqrt(max(rho**2 - a1**2, 1e-300)))
        return quad(f, 0, rho, epsabs=0, epsrel=1e-11, limit=200)[0]
    dvs = [dV_exact(r) for r in rhos]; fd = [(vexact(r + 1e-6) - vexact(r - 1e-6))/2e-6 for r in rhos]
    deriv_ok = all(x > 0 for x in dvs) and max(abs(a - b)/b for a, b in zip(dvs, fd)) < 1e-5
    ok = mono and max(dV) < 1e-6 and all(abs(v["z"]) < 5 for v in z.values()) and deriv_ok
    return R("PASS" if ok else "FAIL", "strictly increasing, continuous; |z| < 5 for MC vs exact",
             {"monotone": mono, "max |ΔV| for Δρ=1e-9": max(dV), "mc_vs_exact": z, "V'(ρ) > 0 and matches finite differences": deriv_ok},
             {"rho": rhos.tolist(), "vol_exact": V.tolist(), "dV": dvs,
              "argument": ("V′(ρ) = ∫₀^ρ 36π² sinα₁ · sin(√(ρ²−α₁²)/3) · ρ/(3√(ρ²−α₁²)) dα₁ has a positive integrand on (0, ρ) for 0 < ρ ≤ π/6, "
                           "so V is C¹ (hence continuous) and strictly increasing; the sampled values illustrate this.")})

# ======================================================================================================
# GROUP F — finite-dimensional models of the abstract logic (illustrations of WH*, the Jordan obstruction)
# ======================================================================================================
@check("F1", "logic", "WH* logic in finite dimension: constrained Duhamel estimate holds with the semigroup's own K, α; telescoping remainder ~ 1/n",
       "random matrices with an invariant constraint subspace (RK′ = CR), quadrature", "toy model (illustration, not proof)", "core §8 WH*",
       kind="toy", needs=("numpy", "scipy"))
def f1(ctx):
    import numpy as np
    from scipy.linalg import expm
    rng = np.random.default_rng(ctx["seed"] + 51); trials = lv(ctx["level"], 5, 30, 100); worst = -np.inf; slopes = []
    for _ in range(trials):
        n, p = 8, 5; Q, _ = np.linalg.qr(rng.normal(size=(n, n)) + 1j*rng.normal(size=(n, n))); Qv, Qc = Q[:, :p], Q[:, p:]
        A = rng.normal(size=(p, p)) + 1j*rng.normal(size=(p, p)); Bm = rng.normal(size=(p, n - p)); Dm = rng.normal(size=(n - p, n - p))
        Kp = Q @ np.block([[A, Bm], [np.zeros((n - p, p)), Dm]]) @ Q.conj().T; Rc = Qc.conj().T
        assert np.allclose(Rc @ Kp, Dm @ Rc)
        alpha = float(np.linalg.eigvalsh((A + A.conj().T)/2).max()); K = 1.0          # ||e^{tA}|| ≤ e^{t μ(A)} on V = ker R
        T = 1.0; ts = np.linspace(0, T, 801); c = [rng.normal(size=p) + 1j*rng.normal(size=p) for _ in range(4)]
        u = lambda t: Qv @ (c[0] + c[1]*np.sin(3*t) + c[2]*t**2 + c[3]*np.cos(5*t))
        du = lambda t: Qv @ (3*c[1]*np.cos(3*t) + 2*c[2]*t - 5*c[3]*np.sin(5*t))
        f = np.array([np.linalg.norm(du(t) - Kp @ u(t)) for t in ts])
        for j in range(50, 801, 50):
            t = ts[j]; trap = getattr(np, "trapezoid", None) or np.trapz
            integ = trap(np.exp(alpha*(t - ts[:j + 1]))*f[:j + 1], ts[:j + 1])
            rhs = K*np.exp(alpha*t)*np.linalg.norm(u(0)) + K*integ
            gap = (np.linalg.norm(u(t)) - rhs)/rhs; worst = max(worst, gap)
        errs = []
        for nn in (8, 16, 32, 64):
            s = np.linspace(0, T, nn + 1); tot = np.zeros(n, complex)
            for i in range(nn):
                h = s[i + 1] - s[i]; di = u(s[i + 1]) - expm(h*Kp) @ u(s[i])
                lin = h*(du(s[i]) - Kp @ u(s[i])); tot += expm((T - s[i + 1])*Kp) @ (di - lin)
            errs.append(np.linalg.norm(tot))
        slopes.append(float(np.polyfit(np.log([8, 16, 32, 64]), np.log(errs), 1)[0]))
    ok = worst <= 1e-6 and np.median(slopes) < -0.8
    return R("PASS" if ok else "FAIL", "estimate never violated; remainder slope ≈ −1", {"max_violation": float(worst), "median_slope": float(np.median(slopes))},
             {"slopes": slopes[:50]})

@check("F2", "logic", "Jordan obstruction: for a 2×2 Jordan pair no K works (ratio → 0 as γ → 0); for a diagonalisable pair K = 1 works",
       "closed form + numerics", "toy model of the core §10 contradiction", "core §10, R1 corollary", kind="toy", needs=("numpy",))
def f2(ctx):
    import numpy as np
    N = np.array([[0, 1], [0, 0]], complex); v = np.array([1, 0], complex); w = np.array([0, 1], complex); rows = []
    for g in np.logspace(-8, 1, 40):
        a = v - 1j*g*w; ratio = np.linalg.norm((g*np.eye(2) - 1j*N) @ a)/(g*np.linalg.norm(a)); rows.append((float(g), float(ratio)))
    Kneeded = [1/r for g, r in rows]; diag_ok = True
    D = np.diag([0.3, -1.2]).astype(complex)
    for g in np.logspace(-8, 1, 40):
        for _ in range(20):
            a = np.random.normal(size=2) + 1j*np.random.normal(size=2)
            if g*np.linalg.norm(a) > np.linalg.norm((g*np.eye(2) - 1j*D) @ a)*(1 + 1e-12): diag_ok = False
    ok = Kneeded[0] > 1e7 and diag_ok
    return R("PASS" if ok else "FAIL", "K needed → ∞ as γ → 0 (Jordan); K = 1 suffices (diagonalisable)",
             {"K_needed_at_gamma=1e-8": Kneeded[0], "diagonalisable_K1_holds": diag_ok}, {"gamma_vs_ratio": rows})

@check("F3", "logic", "Toy ill-posedness: ∂_t u = A∂_x u with a real Jordan block has ‖e^{ikAt}‖ growing linearly in |k| (no loss-free L² bound)",
       "matrix exponential of Fourier symbols", "toy model of the mechanism", "background intuition for the theorem", kind="toy", needs=("numpy", "scipy"))
def f3(ctx):
    import numpy as np
    from scipy.linalg import expm
    A = np.array([[101/99, 1], [0, 101/99]]); ks = np.logspace(0, 6, 25); norms = [float(np.linalg.norm(expm(1j*k*A*1.0), 2)) for k in ks]
    slope = float(np.polyfit(np.log(ks), np.log(norms), 1)[0])
    return R("PASS" if 0.95 < slope < 1.05 else "FAIL", "growth exponent ≈ 1", f"slope {slope:.4f}", {"k": ks.tolist(), "norm": norms})

@check("H1", "meta", "Validator has teeth: deliberately corrupted inputs are detected (must all FAIL)",
       "mutation tests of the validator itself", "guards against tests that cannot fail", "methodology", kind="exact", needs=("numpy",))
def h1(ctx):
    import sympy as sp, numpy as np
    out = {}
    W = witness(ctx); N = gmat(W['P'] - W['r']*sp.eye(16)); v = gvec(W['v']); w = gvec(W['w'])
    v_bad = list(v); v_bad[0] = (v_bad[0][0] + 1, v_bad[0][1])
    out["corrupted v detected by chain check"] = not (gzero(gmv(N, v_bad)) and all(a == b for a, b in zip(gmv(N, w), v_bad)))
    P_bad = W['P'].copy(); P_bad[0, 1] += sp.Rational(1, 10**9)
    out["perturbed P (1e-9) detected"] = not gzero(gmv(gmat(P_bad - W['r']*sp.eye(16)), v)) or \
        not all(a == b for a, b in zip(gmv(gmat(P_bad - W['r']*sp.eye(16)), w), v))
    bd = fresh_defs(ctx); M = bd.witness_model(); M.S[0] = M.S[0] + sp.eye(4)/1000
    rng = random.Random(7); psi = _concrete_psi(bd, rng); Rr = M.R(psi)
    res = M.div(Rr) - sum((M.S[r]*psi[r] for r in range(5)), sp.zeros(4, 1))
    out["DI with S^0 + I/1000 detected (residual > 1e-10)"] = float(_mp_eval_residual(list(res), bd.COORDS, rng, 3, 30)) > 1e-10
    rngn = np.random.default_rng(1); n = 4096; h = 40.0/n; grid = [(np.arange(n) - n//2)*h]; worst = 0
    for t in range(10):
        g = _bump_field(np, grid, rngn, R0=2.0, kind=t % 3, h=h); Hm1, L2, D2, a = _lemma41_ratio(np, g, h, np.array([3.0]))
        worst = max(worst, Hm1/((2*L2/a + 4*D2/a**2)/10))
    out["Lemma 4.1 with constants /10 is violated (so E1 can fail)"] = worst > 1
    Lf = [np.array(sp.N(bd.blk({(0, kk - 1): bd.g3(0, j, kk) for kk in range(1, 5)}, 1, 4)).tolist(), dtype=complex) for j in range(1, 5)]
    th = np.pi/2 + np.pi/3*0.999; Lm, xi = _L_chart(np, th, th, np.array([0, 0, 1.0, 0]), Lf)
    out["COER with too-strong σ = 1 is violated (so E4 can fail)"] = bool(np.linalg.svd(Lm.conj().T, compute_uv=False).min() < 1.0)
    return R("PASS" if all(out.values()) else "FAIL", "every corruption detected", out)

@check("H2", "meta", "Validator has teeth (archive, driver, literature, representation): mutated copies and inputs must be detected",
       "temporary mutated copies of the pack; unit tests of the verdict, DOI-verdict and arXiv-syntax logic; a wrong 'similarity'",
       "guards against tests that cannot fail", "methodology (ChatGPT review finding 26)", kind="exact")
def h2(ctx):
    out = {}
    allids = [c["id"] for c in CHECKS]
    sk = [{"id": i, "status": "SKIP"} for i in allids]
    out["driver: all SKIP → not COMPLETE_PASS"] = compute_verdict(sk, allids, allids)["verdict"] == "PARTIAL_PASS"
    out["driver: --only subset all PASS → PARTIAL_PASS"] = compute_verdict([{"id": "D1", "status": "PASS"}], allids, ["D1"])["verdict"] == "PARTIAL_PASS"
    out["driver: one ERROR → ERROR"] = compute_verdict([{"id": i, "status": "PASS"} for i in allids[:-1]] + [{"id": allids[-1], "status": "ERROR"}], allids, allids)["verdict"] == "ERROR"
    out["driver: one INCOMPLETE → ERROR"] = compute_verdict([{"id": i, "status": "PASS"} for i in allids[:-1]] + [{"id": allids[-1], "status": "INCOMPLETE"}], allids, allids)["verdict"] == "ERROR"
    out["G1: parent DOI resolves, exact DOI does not → not success"] = doi_verdict("10.1/x/y", {"status": 404}, 404, True) == "UNRESOLVED_POSSIBLE_PARENT_DOI"
    with tempfile.TemporaryDirectory() as td16:   # v1.6: reference scan — own source skipped, other .py kept, badge image normalised
        open(os.path.join(td16, "bhmap_validate_v9_9.py"), "w").write('x = "10.48550/arxiv"  # 10.9999/own.source\n')
        open(os.path.join(td16, "other_script.py"), "w").write('# cites 10.1103/PhysRev.186.1337\n')
        open(os.path.join(td16, "README.md"), "w").write('[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1.svg)](https://doi.org/10.5281/zenodo.1)\n')
        d16, _ = _collect_refs(td16)
    out["G1: v1.6 scan skips validator source, keeps other scripts, normalises badge .svg"] = sorted(d16) == ["10.1103/PhysRev.186.1337", "10.5281/zenodo.1"]
    with tempfile.TemporaryDirectory() as td17:   # v1.7: validator outputs skipped (folder + signatures), ordinary files still scanned
        os.makedirs(os.path.join(td17, "results")); os.makedirs(os.path.join(td17, "bhmap_validation_out"))
        open(os.path.join(td17, "results", "run.json"), "w").write('{\n "title": "BHMAP comprehensive validation results",\n "x": "cites 10.1103/PhysRev.186.1337\\\\" 10.5281/zenodo.2"\n}\n')
        open(os.path.join(td17, "results", "run.csv"), "w").write(RESULTS_CSV_HEADER + "x\nG1,literature,online,PASS,10.9999/csv.junk\n")
        open(os.path.join(td17, "bhmap_validation_out", "notes.md"), "w").write("10.9999/outdir.junk\n")
        open(os.path.join(td17, "results", "other.json"), "w").write('{"title": "something else", "doi": "10.5802/jep.3"}\n')
        sk17 = []; d17, _ = _collect_refs(td17, sk17)
    out["G1: v1.7 scan skips validator outputs (results JSON/CSV, output folder), keeps other JSON"] = (
        sorted(d17) == ["10.5802/jep.3"] and sorted(sk17) == ["bhmap_validation_out/", "results/run.csv", "results/run.json"])
    out["G1: network failure → LOOKUP_ERROR, not success"] = doi_verdict("10.1/x", {"status": None}, "error", False) == "LOOKUP_ERROR"
    syn = {"2601.12345": True, "0704.0001": True, "hep-th/9901001": True, "math.AP/0601001": True,
           "2613.12345": False, "hep-th/9913001": False, "foo-bar/9901001": False, "1401.12345": False}
    out["G2: arXiv syntax validator (valid and invalid IDs)"] = all(valid_arxiv_id(k) == v for k, v in syn.items())
    root = ctx.get("pack_dir")
    if root:
        def mutated(fn):
            tmp = tempfile.mkdtemp(prefix="bhmap_mut_")
            try:
                dst = os.path.join(tmp, "p"); shutil.copytree(root, dst); fn(dst); return dst, tmp
            except Exception:
                shutil.rmtree(tmp, ignore_errors=True); raise
        def run(fn, check):
            dst, tmp = mutated(fn)
            try: return check(dst)
            finally: shutil.rmtree(tmp, ignore_errors=True)
        out["A1: unlisted extra file detected"] = run(lambda d: open(os.path.join(d, "GEN13", "EXTRA.txt"), "w").write("x"),
                                                    lambda d: a1_core(d)["status"] == "FAIL")
        out["A2: missing GEN manifest detected"] = run(lambda d: os.remove(os.path.join(d, "GEN13", "GEN13_SHA256SUMS")),
                                                     lambda d: a2_core(d)["status"] == "FAIL")
        out["A2: missing non-deduplicated listed file detected"] = run(lambda d: os.remove(os.path.join(d, "GEN13", "G13_REPORT.md")),
                                                                     lambda d: a2_core(d)["status"] == "FAIL")
        out["A2: altered file content detected"] = run(lambda d: open(os.path.join(d, "GEN13", "G13_REPORT.md"), "a").write(" "),
                                                     lambda d: a2_core(d)["status"] == "FAIL" and a1_core(d)["status"] == "FAIL")
        out["A3: unexpected restore mismatch detected"] = run(lambda d: open(os.path.join(d, "README_MASTER.md"), "a").write(" "),
                                                            lambda d: a3_core(d, ctx["budget_sub"])["status"] == "FAIL")
        def fake(d):
            sp_ = os.path.join(d, "GEN13", "scripts", "check_1_clifford_intertwining.py")
            open(sp_, "w").write("print('Clifford {G^A,G^B} = 2 eta^{AB}: True')\nprint('intertwining (general F, symbolic m, lam): True')\n")
        out["A6: golden-printing fake script rejected by hash before execution"] = run(fake, lambda d: a6_core(os.path.join(d, "GEN13", "scripts"), 60)["status"] == "FAIL")
    elif ctx.get("repo_dir"):
        rroot = ctx["repo_dir"]
        def rrun(fn, check):
            tmp = tempfile.mkdtemp(prefix="bhmap_rmut_")
            try:
                dst = os.path.join(tmp, "r"); shutil.copytree(rroot, dst, ignore=shutil.ignore_patterns(*REPO_IGNORE_DIRS)); fn(dst); return check(dst)
            finally: shutil.rmtree(tmp, ignore_errors=True)
        out["A1 (repo): unlisted extra file detected"] = rrun(lambda d: open(os.path.join(d, "EXTRA.txt"), "w").write("x"), lambda d: a1_repo_core(d)["status"] == "FAIL")
        out["A1 (repo): altered data file detected"] = rrun(lambda d: open(os.path.join(d, "data", "witness.json"), "a").write(" "), lambda d: a1_repo_core(d)["status"] == "FAIL")
        def rfake(d):
            open(os.path.join(d, "scripts", "check_1_clifford_intertwining.py"), "w").write("print('Clifford {G^A,G^B} = 2 eta^{AB}: True')\n")
        out["A6 (repo): golden-printing fake script rejected by hash"] = rrun(rfake, lambda d: a6_core(os.path.join(d, "scripts"), 60)["status"] == "FAIL")
    else:
        out["archive mutations"] = "SKIPPED (no --pack or --repo)"
    try:
        import flint, sympy as sp  # noqa
        from sympy import I
        bd = fresh_defs(ctx, "wrong"); S = sp.diag(2, 1, 1, 1) * (sp.eye(4) + sp.Matrix(4, 4, lambda i, j: (1 + I) if (i, j) == (0, 1) else 0))
        Si = S.inv(); newG = [(S*g*Si).applyfunc(sp.expand) for g in bd.G[:4]] + [bd.G[4]]   # Γ⁴ deliberately NOT conjugated
        cliff = all((newG[a]*newG[b] + newG[b]*newG[a] - 2*(bd.eta[a] if a == b else 0)*sp.eye(4)).applyfunc(sp.expand) == sp.zeros(4, 4)
                    for a in range(5) for b in range(5))
        if cliff:
            bd.G[:] = newG; detected = _invariants(bd, ctx) != _invariants(fresh_defs(ctx), ctx)
        else: detected = True
        out["B4: a wrong 'similarity' (Γ⁴ left unconjugated) is detected"] = detected
    except ImportError:
        out["B4 wrong-similarity test"] = "SKIPPED (python-flint missing)"
    bools = [v for v in out.values() if isinstance(v, bool)]; skipped = [k for k, v in out.items() if isinstance(v, str)]
    st = "FAIL" if not all(bools) else ("PASS" if not skipped else "SKIP")
    return R(st, "every mutation detected", {"detected": sum(bools), "of": len(bools), "skipped_parts": skipped}, out)

# ======================================================================================================
# GROUP G — literature: every DOI and arXiv ID cited anywhere in the archive (online)
# ======================================================================================================
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>\]\[\|`*,;{}']+")
ARXIV_NEW_RE = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(v\d+)?(?![\d])")
ARXIV_OLD_RE = re.compile(r"\b([a-z][a-z\-]*(?:\.[A-Z]{2})?/\d{7})(v\d+)?\b")
ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z][a-z\-]*(?:\.[A-Z]{2})?/\d{7})(v\d+)?", re.I)
ARXIV_DOI_RE = re.compile(r"10\.48550/arXiv\.([0-9]{4}\.[0-9]{4,5})", re.I)
ARXIV_ARCHIVES = {"math-ph", "hep-th", "hep-ph", "hep-lat", "hep-ex", "gr-qc", "quant-ph", "nucl-th", "nucl-ex", "cond-mat", "astro-ph",
                  "physics", "math", "cs", "nlin", "q-bio", "q-alg", "alg-geom", "dg-ga", "funct-an", "solv-int", "chao-dyn", "patt-sol",
                  "adap-org", "comp-gas", "supr-con", "mtrl-th", "chem-ph", "atom-ph", "plasm-ph", "acc-phys", "ao-sci", "bayes-an", "stat"}
REF_EXTS = (".md", ".txt", ".tex", ".bib", ".csv", ".py", ".json", ".yaml", ".yml", ".xml")

def _clean_doi(d):
    d = d.rstrip(".:)'’”")
    while d.count("(") < d.count(")"): d = d[:-1]
    return d

def valid_arxiv_id(x):
    """Syntax check: new style YYMM.NNNN(N) with month 01–12; old style archive[.SC]/YYMMNNN with a known archive and month 01–12."""
    m = re.fullmatch(r"(\d{2})(\d{2})\.(\d{4,5})", x)
    if m: return 1 <= int(m.group(2)) <= 12 and (len(m.group(3)) == 4 or int(m.group(1)) >= 15)
    m = re.fullmatch(r"([a-z][a-z\-]*)(?:\.[A-Z]{2})?/(\d{2})(\d{2})\d{3}", x)
    return bool(m) and m.group(1) in ARXIV_ARCHIVES and 1 <= int(m.group(3)) <= 12

def _classify(rel, ext):
    top = rel.split("/")[0]
    if ext == ".py": return "CODE_CONSTANT_OR_SCRIPT"
    if top in ("HISTORY_EXPANDED", "BHMAP_MASTER_BACKUP_GEN6_COMPACT", "PHASE1", "ARCHIVAL_REPORTS") or re.fullmatch(r"GEN([7-9]|1[0-2])(_.*)?", top):
        return "HISTORICAL_CITATION"
    return "ACTIVE_CITATION"

VALIDATOR_SOURCE_RE = re.compile(r"bhmap_validate_v\d+_\d+\.py")

def _is_validator_source(fname):
    """v1.6: True only for the validator's own source file name (bhmap_validate_vX_Y.py)."""
    return bool(VALIDATOR_SOURCE_RE.fullmatch(fname))

VALIDATOR_OUTPUT_DIRS = {"bhmap_validation_out"}
VALIDATOR_OUTPUT_NAMES = {"checkpoint.json", "timing_history.json", "online_cache_crossref.json", "online_cache_arxiv_ids.json"}
RESULTS_CSV_HEADER = "id,group,kind,status,name,method,independence,claim,"

def _is_validator_output(path):
    """v1.7: True for files this validator writes. Recognised by EXACT content signature, not by name alone."""
    f = os.path.basename(path)
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh: head = fh.read(400)
    except Exception:
        return False
    h = head.lstrip("\ufeff")
    if f.lower().endswith(".json"):
        if re.match(r'\{\s*"title":\s*"BHMAP comprehensive validation results"', h): return True
        if f in VALIDATOR_OUTPUT_NAMES:
            if f == "checkpoint.json": return h.startswith('{"fingerprint": {"script_sha256"')
            if f.startswith("online_cache_"): return h.startswith("{}") or h.startswith('{"https://api.crossref.org/') or h.startswith('{"https://export.arxiv.org/')
            if f == "timing_history.json": return bool(re.match(r'\{("(quick|standard|deep)": \{|\})', h))
    if f.lower().endswith(".csv"): return h.startswith(RESULTS_CSV_HEADER)
    return False

def _collect_refs(root, skipped=None, extra_skip_dirs=()):
    """Every DOI / arXiv candidate in the archive with file, line number, context and a class label.
    v1.6/v1.7: the validator's own source and its own outputs are not citation sources; skipped files are appended to `skipped`."""
    dois, arx = {}, {}
    skip_abs = {os.path.normcase(os.path.abspath(d)) for d in extra_skip_dirs if d}
    for dp, dn, fn in os.walk(root):
        keep = []
        for d in dn:
            full = os.path.join(dp, d)
            if d in VALIDATOR_OUTPUT_DIRS or os.path.normcase(os.path.abspath(full)) in skip_abs:
                if skipped is not None: skipped.append(os.path.relpath(full, root).replace(os.sep, "/") + "/")
            else: keep.append(d)
        dn[:] = keep
        for f in fn:
            ext = os.path.splitext(f)[1].lower()
            if ext not in REF_EXTS: continue
            if _is_validator_source(f) or _is_validator_output(os.path.join(dp, f)):   # v1.6 / v1.7
                if skipped is not None: skipped.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
                continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, root).replace(os.sep, "/"); cls = _classify(rel, ext)
            try: lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
            except Exception: continue
            for ln, line in enumerate(lines, 1):
                ctxt = line.strip()[:160]
                for m in DOI_RE.findall(line):
                    d = _clean_doi(m)
                    if d.lower().startswith("10.48550/arxiv."): continue
                    # file names built from DOIs ("10.5802/jep.3.pdf", ".../123/xxx.scoap.xml") are normalised to the DOI they name;
                    # the original string is kept in the record and the normalised DOI is then checked EXACTLY like any other
                    d2 = re.sub(r"/[^/]*\.(xml|html?|json)$", "", d, flags=re.I); d2 = re.sub(r"\.(pdf|xml|html?|json|svg|png|jpe?g|gif)$", "", d2, flags=re.I)
                    if "http" in line.lower() or "%2" in d2:   # DOI copied out of a web address: decode %XX, drop URL-only suffixes
                        from urllib.parse import unquote
                        d2 = unquote(d2)
                        d2 = re.sub(r"/(full|abstract|pdf|epdf|meta|fulltext|summary|references|figures)/?$", "", d2, flags=re.I).rstrip("/")
                    rec = {"file": rel, "line": ln, "class": cls, "context": ctxt}
                    if d2 != d: rec["normalised_from"] = d
                    dois.setdefault(d2, []).append(rec)
                hits = set()
                for m in ARXIV_URL_RE.finditer(line): hits.add(m.group(1))
                for m in ARXIV_DOI_RE.finditer(line): hits.add(m.group(1))
                if "arxiv" in line.lower():
                    for m in ARXIV_NEW_RE.finditer(line): hits.add(m.group(1))
                    for m in ARXIV_OLD_RE.finditer(line):
                        if m.group(1).split("/")[0].split(".")[0] in ARXIV_ARCHIVES: hits.add(m.group(1))
                for h in hits: arx.setdefault(h, []).append({"file": rel, "line": ln, "class": cls, "context": ctxt, "syntax_ok": valid_arxiv_id(h)})
    return dois, arx

class _Polite:
    """Crossref etiquette: identify (optional mailto → polite pool), ≤ 2 concurrent requests (3 with mailto), respect 429/Retry-After,
    exponential back-off, on-disk cache."""
    def __init__(self, cache_path, mailto):
        import requests, threading
        self.requests = requests; self.local = threading.local(); self.mailto = mailto; self.cache_path = cache_path
        self.cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}; self.lock = threading.Lock()
        self.ua = "BHMAP-validator/1.1 (owner-run reference check" + (f"; mailto:{mailto}" if mailto else "") + ")"
    def sess(self):
        if not hasattr(self.local, "s"):
            self.local.s = self.requests.Session(); self.local.s.headers["User-Agent"] = self.ua
        return self.local.s
    def get(self, url, params=None, timeout=30, attempts=6, deadline=None):
        """GET with cache, per-request timeout, back-off on timeouts/429/5xx (Retry-After honoured), and an optional absolute deadline."""
        key = url + "?" + json.dumps(params, sort_keys=True)
        with self.lock:
            if key in self.cache: return {**self.cache[key], "_cached": True}
        delay = 2.0; last = None
        for attempt in range(attempts):
            if deadline and time.time() > deadline: return {"status": None, "error": f"deadline reached ({last})"}
            try:
                r = self.sess().get(url, params=params, timeout=timeout)
                if r.status_code == 429 or 500 <= r.status_code < 600:
                    ra = r.headers.get("Retry-After"); wait = float(ra) if ra and ra.replace(".", "").isdigit() else delay
                    last = f"http {r.status_code}"; time.sleep(min(wait, 120)); delay = min(delay*2, 120); continue
                out = {"status": r.status_code, "json": (r.json() if r.status_code == 200 and "json" in r.headers.get("content-type", "") else None),
                       "text": (r.text if r.status_code == 200 and "json" not in r.headers.get("content-type", "") else None)}
                if r.status_code in (200, 404):
                    with self.lock: self.cache[key] = out
                return out
            except Exception as e:
                last = f"{type(e).__name__}: {str(e)[:200]}"; time.sleep(delay); delay = min(delay*2, 120)
        return {"status": None, "error": last}
    def head_doi(self, d):
        try:
            r = self.sess().head("https://doi.org/" + self.requests.utils.quote(d, safe="/():;"), allow_redirects=False, timeout=40)
            return r.status_code
        except Exception as e:
            return f"error: {e}"
    def save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f: json.dump(self.cache, f)

def doi_verdict(d, crossref, doi_org_status, parent_ok):
    """Exact-identifier verdict (v1.1): only the EXACT DOI counts. A resolving parent DOI is recorded as POSSIBLE_PARENT_DOI and never as success."""
    if crossref.get("status") == 200: return "RESOLVED_CROSSREF"
    if isinstance(doi_org_status, int) and doi_org_status in (301, 302, 303, 307, 308): return "RESOLVED_DOI_ORG_ONLY"
    if crossref.get("status") is None: return "LOOKUP_ERROR"
    return "UNRESOLVED_POSSIBLE_PARENT_DOI" if parent_ok else "UNRESOLVED"

@check("G1", "literature", "Every DOI cited in the archive resolves EXACTLY (Crossref, else doi.org); core references match year, volume and first page",
       "Crossref REST API (polite, cached) + doi.org handle check; file/line/context/class recorded", "external bibliographic database",
       "references used in the manuscript and literature maps", kind="online", needs=("pack", "online", "requests"))
def g1(ctx):
    if ctx.get("net", {}).get("crossref") is False:
        return R("ERROR", "network reachable", "api.crossref.org unreachable at start (pre-flight)", {"preflight": ctx.get("net")})
    g1_skipped = []; dois, _ = _collect_refs(ctx.get("pack_dir") or ctx["repo_dir"], g1_skipped, (ctx.get("out_dir"),)); pol = _Polite(os.path.join(ctx["out_dir"], "online_cache_crossref.json"), ctx.get("mailto"))
    g1_deadline = time.time() + ctx.get("online_cap", 1200)
    def one(d):
        cr = pol.get("https://api.crossref.org/works/" + pol.requests.utils.quote(d, safe=""), deadline=g1_deadline)
        info = {"cited": dois.get(d, [])[:5], "n_citations": len(dois.get(d, [])), "classes": sorted({c["class"] for c in dois.get(d, [])})}
        doi_org = None; parent_ok = False; parent = None
        if cr.get("status") != 200:
            doi_org = pol.head_doi(d)
            if not (isinstance(doi_org, int) and doi_org in (301, 302, 303, 307, 308)):
                parts = d.split("/")
                for k in range(len(parts) - 1, 1, -1):
                    cand = "/".join(parts[:k]); c2 = pol.get("https://api.crossref.org/works/" + pol.requests.utils.quote(cand, safe=""))
                    if c2.get("status") == 200: parent_ok, parent = True, cand; break
        v = doi_verdict(d, cr, doi_org, parent_ok); info.update({"verdict": v, "doi_org_status": doi_org, "possible_parent": parent})
        if cr.get("status") == 200:
            m = cr["json"]["message"]
            info.update({"title": (m.get("title") or [""])[0], "container": (m.get("container-title") or [""])[0],
                         "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0], "volume": m.get("volume"),
                         "page": m.get("page") or m.get("article-number"), "authors": [a.get("family", "") for a in m.get("author", [])][:8]})
        return d, info
    allids = sorted(set(dois) | set(CORE_REFS)); out = {}
    with ThreadPoolExecutor(max_workers=3 if ctx.get("mailto") else 2) as ex:
        for d, info in ex.map(one, allids): out[d] = info
    pol.save()
    core = {}
    for d, exp in CORE_REFS.items():
        got = out[d]; fields = {}
        for k in ("year", "volume", "page"):
            if k not in exp: continue
            have = got.get(k)
            if have is None: fields[k] = {"expected": exp[k], "found": None, "status": "UNKNOWN"}
            else:
                hv = str(have).split("-")[0].strip()
                fields[k] = {"expected": exp[k], "found": have, "status": "MATCH" if hv == str(exp[k]) else "MISMATCH"}
        core[d] = {"who": exp["who"], "verdict": got["verdict"], "title": got.get("title"), "fields": fields}
    nondoi = set()   # v1.1: nothing is excluded; file-name artefacts are normalised to their DOI in _collect_refs and checked exactly
    unresolved = {d: i["verdict"] for d, i in out.items() if d not in nondoi and i["verdict"] not in ("RESOLVED_CROSSREF", "RESOLVED_DOI_ORG_ONLY")}
    core_bad = [d for d, c in core.items() if c["verdict"] != "RESOLVED_CROSSREF" or any(f["status"] != "MATCH" for f in c["fields"].values())]
    by_class = {}
    for d, i in out.items():
        for c in i["classes"] or ["CORE_REF_ONLY"]: by_class.setdefault(c, [0, 0])[0 if d not in unresolved else 1] += 1
    errors = [d for d, v in unresolved.items() if v == "LOOKUP_ERROR"]
    st = "PASS" if not unresolved and not core_bad else ("ERROR" if errors and len(errors) == len(unresolved) and not core_bad else "FAIL")
    return R(st, "every exact DOI resolves; every core field MATCH (UNKNOWN counts as a problem)",
             {"dois": len(out), "unresolved": unresolved, "core_problems": core_bad, "resolved/unresolved by class": by_class,
              "excluded_not_a_doi": {d: out[d]["verdict"] for d in sorted(nondoi)}},
             {"core_references": core, "all": out, "scope": "parent-DOI resolution is NEVER counted as success (v1.1)",
              "skipped_validator_files": g1_skipped})

def _oai_exists(pol, aid, deadline):
    """Second, independent existence check: OAI-PMH GetRecord on the export mirror.
    Returns (True|False|None, detail). idDoesNotExist → False; a returned record → True; anything else → None (lookup error)."""
    r = pol.get("https://export.arxiv.org/oai2", params={"verb": "GetRecord", "identifier": f"oai:arXiv.org:{aid}", "metadataPrefix": "oai_dc"},
                timeout=45, attempts=4, deadline=deadline)
    time.sleep(1.0)
    txt = r.get("text") or ""
    if r.get("status") == 200 and "<GetRecord>" in txt:
        m = re.search(r"<dc:title>(.*?)</dc:title>", txt, re.S)
        return True, {"via": "OAI-PMH GetRecord", "title": " ".join(m.group(1).split()) if m else None}
    if r.get("status") == 200 and 'code="idDoesNotExist"' in txt:
        return False, {"via": "OAI-PMH GetRecord", "oai_error": "idDoesNotExist"}
    return None, {"via": "OAI-PMH GetRecord", "http": r.get("status"), "error": r.get("error") or (txt[:200] if txt else None)}

def _arxiv_query(pol, ids, deadline):
    """Query a batch; returns ({id: (exists, title)}, error or None)."""
    import xml.etree.ElementTree as ET
    r = pol.get("https://export.arxiv.org/api/query", params={"id_list": ",".join(ids), "max_results": len(ids) + 5},
                timeout=45, attempts=4, deadline=deadline)
    if r.get("status") != 200 or not r.get("text"): return {}, f"http {r.get('status')} {r.get('error') or ''}".strip()
    try:
        root = ET.fromstring(r["text"]); ns = {"a": "http://www.w3.org/2005/Atom"}; found = {}
        for e in root.findall("a:entry", ns):
            eid = (e.findtext("a:id", default="", namespaces=ns) or "").split("/abs/")[-1]; base = re.sub(r"v\d+$", "", eid)
            title = " ".join((e.findtext("a:title", default="", namespaces=ns) or "").split())
            if title and title.lower() != "error": found[base] = title
        return {i: (i in found, found.get(i)) for i in ids}, None
    except ET.ParseError as ex:
        return {}, f"malformed response: {ex}"

@check("G2", "literature", "Every arXiv identifier cited in the archive is syntactically valid and exists (arXiv API; resumable per ID)",
       "arXiv export API (https, sequential, ≥ 3.1 s spacing, back-off on timeouts/429/5xx, batch bisection) + OAI-PMH GetRecord fallback on export.arxiv.org",
       "external database", "arXiv references in literature maps", kind="online", needs=("pack", "online", "requests"))
def g2(ctx):
    if ctx.get("net", {}).get("arxiv") is False:
        return R("ERROR", "network reachable", "export.arxiv.org unreachable at start (pre-flight)", {"preflight": ctx.get("net")})
    g2_skipped = []; _, arx = _collect_refs(ctx.get("pack_dir") or ctx["repo_dir"], g2_skipped, (ctx.get("out_dir"),)); pol = _Polite(os.path.join(ctx["out_dir"], "online_cache_arxiv_ids.json"), ctx.get("mailto"))
    deadline = time.time() + ctx.get("online_cap", 1200); ids = sorted(arx); out = {}; log = []
    for i in ids:
        if not valid_arxiv_id(i): out[i] = {"exists": False, "verdict": "INVALID_SYNTAX", "cited": arx[i][:5]}
    todo = [i for i in ids if i not in out and ("id:" + i) not in pol.cache]
    for i in ids:
        if ("id:" + i) in pol.cache: c = pol.cache["id:" + i]; out[i] = {**c, "cited": arx[i][:5], "from_cache": True}
    queue = [todo[j:j + 20] for j in range(0, len(todo), 20)]
    while queue:
        if time.time() > deadline: break
        chunk = queue.pop(0); got, err = _arxiv_query(pol, chunk, deadline); time.sleep(3.1)
        if err is None:
            for i, (ex, title) in got.items():
                rec = {"exists": ex, "verdict": "EXISTS" if ex else "NOT_FOUND_IN_API", "title": title}
                if not ex and time.time() < deadline:     # confirm a negative through OAI-PMH before calling it missing
                    ok, det = _oai_exists(pol, i, deadline)
                    rec.update({"oai": det, "exists": ok,
                                "verdict": "EXISTS (OAI-PMH)" if ok else ("NOT_FOUND (API and OAI-PMH)" if ok is False else "LOOKUP_ERROR (OAI-PMH)")})
                if rec["exists"] is not None: pol.cache["id:" + i] = rec
                out[i] = {**rec, "cited": arx[i][:5]}
            pol.save()
        else:
            log.append({"batch": len(chunk), "error": err})
            if len(chunk) > 1: queue = [chunk[:len(chunk)//2], chunk[len(chunk)//2:]] + queue      # bisect and retry smaller
            else:
                i = chunk[0]; ok, det = _oai_exists(pol, i, deadline)
                rec = {"exists": ok, "oai": det, "verdict": "EXISTS (OAI-PMH)" if ok else ("NOT_FOUND (OAI-PMH)" if ok is False else "LOOKUP_ERROR (API and OAI-PMH)")}
                if ok is not None: pol.cache["id:" + i] = rec
                out[i] = {**rec, "cited": arx[i][:5]}; pol.save()
    for i in ids:
        if i not in out: out[i] = {"exists": None, "verdict": "NOT_ATTEMPTED (time cap reached)", "cited": arx[i][:5]}
    pol.save()
    missing = [c for c, v in out.items() if v["exists"] is False]; errors = [c for c, v in out.items() if v["exists"] is None]
    st = "PASS" if not missing and not errors else ("FAIL" if missing else "ERROR")
    note = "re-run with --resume (or --only G2): IDs already confirmed are cached and skipped" if errors else ""
    return R(st, "all syntactically valid and found", {"arxiv_ids": len(out), "not_found_or_invalid": missing, "lookup_errors": len(errors),
             "confirmed_from_cache": sum(1 for v in out.values() if v.get("from_cache"))}, {"all": out, "network_log": log[:50], "note": note, "skipped_validator_files": g2_skipped})

def compute_verdict(results, all_ids, selected_ids):
    """v1.1 verdict (never 'success' merely because nothing failed):
    FAIL       — any FAIL;   ERROR — any ERROR/INCOMPLETE (and no FAIL);
    COMPLETE_PASS — every registered check was selected and ran, and every one is PASS or INFO;
    PARTIAL_PASS  — no FAIL/ERROR/INCOMPLETE, but some checks were skipped or not selected (listed)."""
    st = {r["id"]: r["status"] for r in results}
    if any(v == "FAIL" for v in st.values()): v = "FAIL"
    elif any(v in ("ERROR", "INCOMPLETE") for v in st.values()): v = "ERROR"
    elif set(selected_ids) == set(all_ids) and all(st.get(i) in ("PASS", "INFO", "NA") for i in all_ids): v = "COMPLETE_PASS"
    else: v = "PARTIAL_PASS"
    not_run = sorted(set(all_ids) - set(selected_ids)); skipped = sorted(i for i, x in st.items() if x == "SKIP")
    missing = sorted(set(selected_ids) - set(st))
    na = sorted(i for i, x in st.items() if x == "NA")
    return {"verdict": v, "not_selected": not_run, "skipped": skipped, "not_applicable_in_this_mode": na, "unaccounted": missing,
            "accounted": f"{len(st)} results for {len(selected_ids)} selected of {len(all_ids)} registered checks"}

def environment():
    env = {"script_version": SCRIPT_VERSION, "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
           "processor": platform.processor(), "logical_cpus": os.cpu_count(), "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for m in ("sympy", "numpy", "scipy", "mpmath", "flint", "requests"):
        try: env[m] = __import__(m).__version__
        except Exception as e: env[m] = f"not available ({type(e).__name__})"
    try: env["script_sha256"] = sha256_file(os.path.abspath(__file__))
    except Exception: env["script_sha256"] = None
    return env

# ---- v1.3 scheduler: one process per check, individual time limits, heartbeat, Ctrl-C safety, checkpoint/resume ----
def _child_entry(meta, ctx, q):
    try: q.put(_run_one(meta, ctx))
    except BaseException as e: q.put({**meta, **R("ERROR", details={"child_exception": repr(e)}), "runtime_s": None})

DEFAULT_TIMEOUT = {"online": 2400, "quick": 1800, "standard": 3600, "deep": 3*3600}
def _check_timeout(meta, level, override):
    if override: return override
    return DEFAULT_TIMEOUT["online"] if meta["kind"] == "online" else DEFAULT_TIMEOUT[level]

def _fingerprint(a, pack_dir):
    pk = None
    if pack_dir and os.path.exists(os.path.join(pack_dir, "INTEGRITY", "PACK_SHA256SUMS")):
        pk = sha256_file(os.path.join(pack_dir, "INTEGRITY", "PACK_SHA256SUMS"))
    try: sh = sha256_file(os.path.abspath(__file__))
    except Exception: sh = None
    rp = os.path.join(os.path.abspath(a.repo), "SHA256SUMS") if getattr(a, "repo", None) else None
    return {"script_sha256": sh, "level": a.level, "seed": a.seed, "online": a.online, "pack_manifest_sha256": pk,
            "repo_manifest_sha256": sha256_file(rp) if rp and os.path.exists(rp) else None}

def _preflight():
    out = {}
    try:
        import requests
        for name, url in (("crossref", "https://api.crossref.org/works?rows=0"), ("arxiv", "https://export.arxiv.org/api/query?id_list=0704.0001")):
            try: out[name] = requests.get(url, timeout=20, headers={"User-Agent": "BHMAP-validator/1.3 preflight"}).status_code < 500
            except Exception as e: out[name] = False; out[name + "_error"] = f"{type(e).__name__}"
    except ImportError:
        out["requests"] = False
    return out

def _fmt(sec):
    sec = int(sec or 0); return f"{sec//3600}h{(sec%3600)//60:02d}m" if sec >= 3600 else f"{sec//60}m{sec%60:02d}s"

def _write_reports(a, doc_extra, results, t0, pack_dir, ctx, vd):
    counts = {}
    for r in results: counts[r["status"]] = counts.get(r["status"], 0) + 1
    env = environment(); deps = {m: env.get(m) for m in ("numpy", "scipy", "mpmath", "flint", "requests")}
    doc = {"title": "BHMAP comprehensive validation results", "verdict": vd["verdict"], "verdict_detail": vd, "counts": counts,
           "missing_dependencies": {k: v for k, v in deps.items() if str(v).startswith("not available")}, "level": a.level, "seed": a.seed,
           "environment": env, "pack": {"path": a.pack, "dir": pack_dir}, "network_preflight": ctx.get("net"),
           "wall_time_s": round(time.time() - t0, 1), **doc_extra,
           "provenance_note": ("Exact checks prove the finite identities they test. Numeric checks are falsification attempts (no counterexample "
                               "found, not a proof). Toy checks illustrate the abstract logic. Online checks compare citations with Crossref/arXiv. "
                               "This is machine re-checking of the supplied construction, not human verification or independent replication."),
           "results": sorted(results, key=lambda r: (r["group"], r["id"]))}
    jp = os.path.join(a.out, "bhmap_validation_results.json"); cp = os.path.join(a.out, "bhmap_validation_results.csv")
    with open(jp + ".tmp", "w", encoding="utf-8") as f: json.dump(doc, f, indent=1, default=str, ensure_ascii=False)
    os.replace(jp + ".tmp", jp)
    cols = ["id", "group", "kind", "status", "name", "method", "independence", "claim", "expected", "observed", "metric", "threshold", "runtime_s",
            "resumed_from_checkpoint"]
    with open(cp + ".tmp", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(cols)
        for r in doc["results"]: wr.writerow([json.dumps(r.get(c), default=str, ensure_ascii=False) if isinstance(r.get(c), (dict, list)) else r.get(c) for c in cols])
    os.replace(cp + ".tmp", cp)
    return jp, cp, counts, doc

def main():
    import multiprocessing as mp
    ap = argparse.ArgumentParser(description="BHMAP comprehensive validation suite")
    ap.add_argument("--pack"); ap.add_argument("--repo"); ap.add_argument("--level", default="standard", choices=list(LEVELS))
    ap.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 4)),
                    help="parallel checks (default min(8, CPUs); for --level deep start with 4 and watch RAM)")
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--mailto", help="contact e-mail for the Crossref polite pool (optional)")
    ap.add_argument("--budget", type=float, default=None, help="overall wall-clock budget in seconds (default 6 h deep, 2 h otherwise)")
    ap.add_argument("--check-timeout", type=float, default=None, help="per-check limit in seconds (default: 3 h deep / 1 h standard / 30 min quick; online 40 min)")
    ap.add_argument("--online-cap", type=float, default=1200, help="time cap inside each online check before it stops and reports what is left (default 1200 s)")
    ap.add_argument("--resume", action="store_true", help="reuse PASS/INFO results from the checkpoint of an IDENTICAL configuration")
    ap.add_argument("--heartbeat", type=float, default=60, help="seconds between progress lines (default 60)")
    ap.add_argument("--out", default="bhmap_validation_out"); ap.add_argument("--seed", type=int, default=20261120)
    ap.add_argument("--only", help="comma-separated check ids (e.g. D1,E1)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(errors="replace")
        except Exception: pass
    embed = os.path.join(os.path.abspath(a.out), "_embedded"); os.makedirs(embed, exist_ok=True)
    for name, src, h in (("bhmap_defs.py", BHMAP_DEFS_SRC, BHMAP_DEFS_SHA256), ("witness_min.py", WITNESS_MIN_SRC, WITNESS_MIN_SHA256)):
        with open(os.path.join(embed, name), "w", encoding="utf-8", newline="\n") as f: f.write(src)
        if sha256_file(os.path.join(embed, name)) != h: sys.exit(f"embedded {name} hash mismatch — the script was altered")
    pack_dir = None
    if a.pack:
        if os.path.isdir(a.pack): pack_dir = os.path.abspath(a.pack)
        else:
            dst = os.path.join(os.path.abspath(a.out), "_pack"); marker = os.path.join(dst, ".zip_sha256"); zsha = sha256_file(a.pack)
            if not (os.path.exists(marker) and open(marker).read().strip() == zsha):     # re-extract only if the zip changed
                shutil.rmtree(dst, ignore_errors=True)
                with zipfile.ZipFile(a.pack) as z: z.extractall(dst)
                open(marker, "w").write(zsha)
            subs = [d for d in os.listdir(dst) if os.path.isdir(os.path.join(dst, d))]; pack_dir = os.path.join(dst, subs[0]) if len(subs) == 1 else dst
    repo_dir = os.path.abspath(a.repo) if a.repo else None
    here = os.path.dirname(os.path.abspath(__file__))
    if not pack_dir and not repo_dir and os.path.exists(os.path.join(here, "scripts", "witness_min.py")) and os.path.exists(os.path.join(here, "data", "witness.json")):
        repo_dir = here; print(f"repository mode (auto-detected): {repo_dir}")
    budget = a.budget or (6*3600 if a.level == "deep" else 7200)
    ctx = {"level": a.level, "seed": a.seed, "online": a.online, "pack_dir": pack_dir, "repo_dir": repo_dir, "embed_dir": embed, "out_dir": os.path.abspath(a.out),
           "mailto": a.mailto, "budget_sub": 1800, "online_cap": a.online_cap}
    if a.online:
        ctx["net"] = _preflight(); print(f"network pre-flight: {ctx['net']}")
    todo = [c for c in CHECKS if not a.only or c["id"] in a.only.split(",")]
    fp = _fingerprint(a, pack_dir); ck_path = os.path.join(a.out, "checkpoint.json"); hist_path = os.path.join(a.out, "timing_history.json")
    ck = json.load(open(ck_path, encoding="utf-8")) if os.path.exists(ck_path) else {}
    hist = json.load(open(hist_path, encoding="utf-8")) if os.path.exists(hist_path) else {}
    results = []
    if a.resume and ck.get("fingerprint") == fp:
        for c in list(todo):
            r = ck.get("results", {}).get(c["id"])
            if r and r["status"] in ("PASS", "INFO"):
                results.append({**r, "resumed_from_checkpoint": True}); todo.remove(c)
        print(f"resume: reusing {len(results)} PASS/INFO results from the checkpoint (identical script, level, seed, pack, online flag)")
    elif a.resume:
        print("resume: checkpoint missing or configuration differs — running everything")
    if ck.get("fingerprint") != fp: ck = {"fingerprint": fp, "results": {}}
    print(f"BHMAP validation v{SCRIPT_VERSION}: {len(todo)} checks to run, level={a.level}, workers={a.workers}, mode={'full archive' if pack_dir else ('repository' if repo_dir else 'none')}, "
          f"online={a.online}, budget={_fmt(budget)}")
    order = sorted(todo, key=lambda c: -(hist.get(a.level, {}).get(c["id"], 0) or (1e6 if c["id"] in ("B6", "B4", "E2", "C4") else 0)))
    mpc = mp.get_context("spawn"); running = {}; pending = list(order); last_beat = time.time(); interrupted = False

    def finish(c, r):
        results.append(r); ck["results"][c["id"]] = r
        if r.get("runtime_s"): hist.setdefault(a.level, {})[c["id"]] = r["runtime_s"]
        try:
            json.dump(ck, open(ck_path, "w", encoding="utf-8"), default=str); json.dump(hist, open(hist_path, "w", encoding="utf-8"))
        except Exception: pass
        prev = hist.get(a.level, {}).get(c["id"])
        print(f"  [{r['status']:10}] {c['id']:3} {c['name'][:88]}  ({r.get('runtime_s')} s)", flush=True)
    try:
        while pending or running:
            while pending and len(running) < max(1, a.workers) and time.time() - t0 < budget:
                c = pending.pop(0); q = mpc.Queue(); pr = mpc.Process(target=_child_entry, args=(c, ctx, q), daemon=True); pr.start()
                running[c["id"]] = (c, pr, q, time.time(), _check_timeout(c, a.level, a.check_timeout))
            if pending and time.time() - t0 >= budget:
                for c in pending: finish(c, {**c, **R("INCOMPLETE", details={"reason": f"overall budget {_fmt(budget)} reached before start"}), "runtime_s": None})
                pending = []
            for cid, (c, pr, q, ts, lim) in list(running.items()):
                r = None
                try: r = q.get(timeout=0.05)
                except Exception: pass
                if r is not None:
                    pr.join(timeout=10); del running[cid]; finish(c, r); continue
                el = time.time() - ts
                if not pr.is_alive():
                    del running[cid]
                    finish(c, {**c, **R("ERROR", details={"reason": f"worker process ended without a result (exit code {pr.exitcode}); "
                                                          "possible out-of-memory or crash"}), "runtime_s": round(el, 1)})
                elif el > lim or time.time() - t0 > budget:
                    pr.terminate(); pr.join(timeout=10); del running[cid]
                    why = f"per-check limit {_fmt(lim)}" if el > lim else f"overall budget {_fmt(budget)}"
                    finish(c, {**c, **R("INCOMPLETE", details={"reason": f"{why} reached; process stopped. Re-run with --resume (and a larger "
                                                               "--check-timeout if needed): finished checks are reused"}), "runtime_s": round(el, 1)})
            if running and time.time() - last_beat >= a.heartbeat:
                last_beat = time.time()
                desc = ", ".join(f"{cid} {_fmt(time.time() - v[3])}" + (f" (last {_fmt(hist.get(a.level, {}).get(cid))})" if hist.get(a.level, {}).get(cid) else "")
                                 for cid, v in running.items())
                print(f"  … {_fmt(time.time() - t0)} elapsed | done {len(results)} | running: {desc} | queued: {len(pending)}", flush=True)
            time.sleep(0.2)
    except KeyboardInterrupt:
        interrupted = True
        print("\nInterrupted — stopping running checks and writing a partial report (use --resume to continue later).", flush=True)
        for cid, (c, pr, q, ts, lim) in list(running.items()):
            try: pr.terminate(); pr.join(timeout=5)
            except Exception: pass
            finish(c, {**c, **R("INCOMPLETE", details={"reason": "interrupted by user (Ctrl-C)"}), "runtime_s": round(time.time() - ts, 1)})
        for c in pending: finish(c, {**c, **R("INCOMPLETE", details={"reason": "interrupted by user before start"}), "runtime_s": None})
    vd = compute_verdict(results, [c["id"] for c in CHECKS], [c["id"] for c in CHECKS if not a.only or c["id"] in a.only.split(",")])
    jp, cp, counts, doc = _write_reports(a, {"interrupted": interrupted, "resumed_ids": [r["id"] for r in results if r.get("resumed_from_checkpoint")],
                                             "budget_s": budget}, results, t0, pack_dir, ctx, vd)
    print(f"\nVERDICT: {vd['verdict']}   counts={counts}   wall={doc['wall_time_s']} s")
    if vd["skipped"]: print(f"  skipped: {vd['skipped']}   (missing dependencies: {doc['missing_dependencies'] or 'none'}; online={a.online}; pack={'yes' if pack_dir else 'no'})")
    if vd["not_selected"]: print(f"  not selected (--only): {vd['not_selected']}")
    if vd["not_applicable_in_this_mode"]: print(f"  not applicable in this mode (NA): {vd['not_applicable_in_this_mode']}")
    inc = [r["id"] for r in results if r["status"] in ("INCOMPLETE", "ERROR")]
    if inc: print(f"  unfinished/errored: {inc} — re-run the same command with --resume to retry only these")
    slow = sorted([r for r in results if r.get("runtime_s")], key=lambda r: -r["runtime_s"])[:5]
    print("  slowest: " + ", ".join(f"{r['id']} {_fmt(r['runtime_s'])}" for r in slow))
    print(f"JSON: {os.path.abspath(jp)}\nCSV : {os.path.abspath(cp)}")
    print(f"sha256(JSON) = {sha256_file(jp)}")

if __name__ == "__main__":
    main()
