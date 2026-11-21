# Outlook: where this might lead

> **What this page is.** The [README](README.md) states what is established. This page collects **additional** exact computations, conjectures and interpretations that go beyond the main theorem. The additional claims and interpretations on this page are not used in the theorem's proof; items labelled PAPER summarise results already used or established in the manuscript. This page has received a documentation and scope review (Perplexity, 2026-11-21). Its additional computations, internal project records and mathematical conclusions have not been independently verified. It is organised in three parts:
>
> - **A. Additional exact algebraic claims**: explicit formulas, with the script that checks each one.
> - **B. Mathematical conjectures**: precise guesses, what motivates them, and what would settle them.
> - **C. Physical interpretations**: kept separate from the algebra, with their limits stated.
>
> Every item carries a status label:
> - **[PAPER]**: proved in the paper (frozen candidate, not yet public). Like the rest of the project, it is AI-checked only.
> - **[PROJECT RECORD]**: an earlier internal result of this project, with the status recorded there. The records are in the project's private archive and will be included in the planned full review.
> - **[NEW · exact · unaudited]**: an exact computation checked by [`scripts/outlook_checks.py`](scripts/outlook_checks.py) (sympy only, under a minute). It is project code and has not been reviewed by anyone else.
> - **[CONJECTURE]**: a precise statement that is not proved.
> - **[RESEARCH QUESTION]**: a scenario worth investigating, not yet stated with full quantifiers.
> - **[INTERPRETATION]** or **[SPECULATION]**: a reading or analogy, offered to start a conversation.
>
> The script supports only the algebraic items marked NEW. It cannot support any conjecture, research question or physical interpretation.

---

## Part A. Additional exact algebraic claims

All of Part A concerns the **frame principal symbol** P(ξ) of the reduced system at the witness parameters, with π′ = 1/2 unless stated. Here ξ = (ξ₁, ξ₂, ξ₃, ξ₄) is a frame covector, with ξ_a = (ξ₁, ξ₂) along S²(1) and ξ_b = (ξ₃, ξ₄) along S²(3). The background is homogeneous and the matrices S^ρ are constant in the frame, so the frame symbol is the same at every point of the chart. Light speed is 1 in this orthonormal frame.

### A1. The full dispersion relation [NEW · exact · unaudited]

For a **symbolic** covector ξ, the characteristic polynomial of P(ξ) factors exactly as

  det(x − P(ξ)) = (x² − v₁²|ξ_a|² − v₃²|ξ_b|²)² · (x² − |ξ|²)⁴ · (x² − |ξ|²/4)²,

with

  v₁² = 349353481/1750347625 (v₁ ≈ 0.4468),  v₃² = 72301009/70013905 (v₃ ≈ 1.0162).

This is checked as an identity of polynomials in (ξ₁, ξ₂, ξ₃, ξ₄, x) by `outlook_checks.py`, check 5. So the symbol has three branches:

| branch | eigenvalues ω | algebraic multiplicity |
|---|---|---|
| "light" | ±\|ξ\| | 4 each |
| "G-branch" | ±ω_G(ξ), with ω_G² = v₁²\|ξ_a\|² + v₃²\|ξ_b\|² | 2 each |
| constraint quotient | ±π′\|ξ\| = ±\|ξ\|/2 | 2 each |

The third branch depends on π′. The final factor is the characteristic polynomial of the map that P induces on the quotient by ker L ([PAPER], Prop. 5.1(c)); this identifies its quotient origin. Since v₁ < 1/2 < v₃, the G-branch and the quotient eigenvalue coincide in some directions. Where spectral branches coincide, an eigenvalue alone does not identify whether an eigenvector lies in the constraint kernel, so no constraint violation is inferred from the value ±|ξ|/2 alone.

### A2. Which branches lie in the constraint kernel [NEW · exact · unaudited]

- Along ξ = e₃, the G-branch eigenspace for ±ω_G together has dimension 4 (2 for each sign), and L(ξ) annihilates all of it (check 2).
- At three random rational covectors away from the crossing (check 6): the G-branch eigenspace has dimension 4 (±ω_G together) and the light-branch eigenspace has dimension 8 (±|ξ| together). Both lie in ker L, so together they span the 12-dimensional ker L, and P is diagonalisable there. This is regression evidence at sample covectors, not a proof for every ξ.

So the relevant eigenspaces lie inside the principal constraint kernel, and these modes are not merely constraint-violating modes of this reduction. That is a statement about the principal symbol. Their physical interpretation is a separate question (Part C), and no variable-coefficient mode construction is claimed.

### A3. Characteristic speeds [NEW · exact · unaudited, derived from A1]

- **Phase speeds.** For a unit covector, the eigenvalues give directional characteristic phase speeds:
  - light branch: 1;
  - constraint quotient: π′ = 1/2;
  - G-branch: ω_G, which lies between v₁ ≈ 0.4468 (along S²(1)) and v₃ ≈ 1.0162 (along S²(3)).

  At π′ = 1/2 the largest phase speed over all branches and all directions is therefore v₃. The G-branch has phase speed above 1 exactly when (v₁² − 1)|ξ_a|² + (v₃² − 1)|ξ_b|² > 0.
- **Group velocity.** The G-branch is ellipsoidal. Its group velocity ∇_ξ ω_G = Dξ/ω_G, with D = diag(v₁², v₁², v₃², v₃²), reaches magnitude v₃ > 1 for ξ along S²(3).
- **What "faster than light" means here, and what it does not.** On this page it means only that the G-branch phase speed, and its geometric-optics group speed, exceed 1 in some directions.

  This is a statement about the principal symbol. It is not a statement about the actual propagation of signals or about domains of dependence for this system. At the witness crossing, the constrained Jordan chain supplies a principal-symbol obstruction, and the theorem establishes the resulting failure of the specified loss-free well-posedness package. The usual link between characteristic speeds and domains of dependence is therefore not available here. No causality claim is made.

### A4. The crossing cone, and where the witness sits [NEW · exact · unaudited; PROJECT RECORD]

Subtracting the light branch from A1 gives

  ω_G² − |ξ|² = (v₁² − 1)|ξ_a|² + (v₃² − 1)|ξ_b|².

The G-branch meets the light branch exactly on the cone 𝒳 where this vanishes. Since v₁² − 1 < 0 < v₃² − 1, in the punctured cotangent space ξ ≠ 0 the set 𝒳 is a smooth codimension-one conic hypersurface; its closure includes the vertex at zero. The witness covector ξ\* = (20/99, 0, 1, 0) lies on 𝒳 exactly (check 3).

So at ξ\* the two branches coincide: r = 101/99 = |ξ\*|, with algebraic multiplicity 4 + 2 = 6 for each sign, as in the paper's Table 1.

**A crossing alone does not give a Jordan block.** The project's earlier records separate the two conditions:

- **[PROJECT RECORD]** GEN9 Corollary L2.3: on the Pauli slice, P restricted to ker L has a real eigenvalue crossing between the light branch and the G-branch exactly on 𝒳. 𝒳 is a real codimension-1 cone exactly when (v₁² − 1)(v₃² − 1) < 0, a transversal crossing. Recorded status: ESTABLISHED given GEN9's Lemma L2.1.
- **[PROJECT RECORD]** GEN9 Theorem L3.1: on 27 tested parameter slices, the restricted operator has defect exactly 2 at **every** crossing point. Exact computation per slice; status ESTABLISHED per slice.
- **[PROJECT RECORD]** GEN9 Theorem L3.2: on the coincident stratum β = 1 (six tested values), v₁² = v₃² = 1. The G-branch then equals the light branch for every ξ, and the defect is **0**. Status: ESTABLISHED per slice.
- The tested records associate the defect with transversal crossings **and** a model-specific coupling. These finite records do not establish a universal necessity statement over every parameter choice. GEN9 interprets this coupling as a "forward coupling" from the light branch to the G-branch, of rank 2 at the crossing, but records that interpretation only as SUPPORTED. The sign condition guarantees that the branches intersect. It does not by itself make the symbol defective there.

These are AI-only results of this project, recorded in `GEN9/G9_THEORY_UPGRADE.md` in the private archive. They are not part of the paper.

### A5. Constraint additions [PAPER; PROJECT RECORD]

- **[PAPER, Prop. 5.1(a)]** For the one-parameter family of constraint additions π′: P_{π′} − P_{π″} = (π′ − π″)M⁻¹TL, which vanishes on ker L. So P restricted to ker L, and the Jordan chain, are the same for every π′. (`outlook_checks.py` check 4 is a regression test of this at four values.)
- **[PROJECT RECORD]** GEN9 Proposition L5.1 extends the same elementary argument to any symbol-level reduction P_h = P − A⁻¹BL with A invertible: it agrees with P on ker L, so it keeps the Jordan chain. Recorded status: ESTABLISHED (elementary).
- **Open question.** Reformulations that change the variables or field content, such as keeping ψ₀ dynamical, Stückelberg fields, auxiliary fields or other gauges, are not covered. The defect is unchanged under the constraint additions and symbol-level reductions explicitly described above. No claim is made for the other reformulations just listed.

### A6. The coefficient in the Pauli term [PROJECT RECORD]

The mass/Pauli term has the form X_A = −(m/3)Γ_A + λc₁(F̸Γ_A − α Γ_A F̸). Within this ansatz, the Clifford intertwining identity used in the reduction holds in five dimensions at α = 1/3, the value used here.

This is a Clifford compatibility identity, used in the paper in five dimensions only. **[PROJECT RECORD, not verified here]** For the same ansatz in other dimensions d, the project's errata register (G-67) records α = (d − 4)/(d − 2). That value came from ChatGPT's blind derivation in GEN14 (V1), and it corrected an earlier, wrong remark. The written proof in the record (GEN14 V4) covers d = 5 only. The general-d formula has not been re-derived or checked for this page, the record does not state its exact dimensional scope or exceptional cases (for example, it is undefined at d = 2), and nothing here uses it. The project's notes compare this structure with the gravitino Pauli term in supergravity (cf. Deser–Waldron, eq. 15), but that comparison has not been derived in detail. Selecting a coefficient within a restricted ansatz is **not** a characterisation of supergravity.

---

## Part B. Mathematical conjectures

The theorem rules out existence, uniqueness and the loss-free bound **together**. Systems whose principal symbol has real eigenvalues but too few eigenvectors are called *weakly hyperbolic*. The ADM formulation of Einstein's equations is the textbook example ([Sarbach et al., gr-qc/0205064](https://arxiv.org/abs/gr-qc/0205064)). Kreiss and Ortiz (2002) show that such systems can be very sensitive to lower-order terms and variable coefficients.

### B1. [RESEARCH QUESTION A: well-posedness with derivative loss]

The system may admit existence, uniqueness and continuous dependence in a shifted Sobolev scale, with an estimate of the form

  ‖Φ(t)‖_{H^s} ≤ C_t ‖Φ₀‖_{H^{s+1}}.

This would be a weaker well-posedness statement than the package excluded by the theorem. It does **not** imply that property (E), as defined in the paper, holds, and an estimate alone would not establish existence or uniqueness.

- **To become a precise conjecture, it needs:** the data class (constrained H^{s+1} data), the solution class, the admissible s, the spatial domains (shrinking geodesic balls, as in the theorem) and the time interval.
- **Motivation.** In the frozen constant-coefficient model, a single J₂ block makes solutions grow like 1 + |ξ|t, a loss of one derivative. That motivates the conjecture. It does not prove it for the variable-coefficient constrained system.

### B2. [RESEARCH QUESTION B: a stronger obstruction]

This is an alternative scenario, not yet a definite proposition with explicit quantifiers. Lower-order terms acting on the generalised eigenspace could make things worse than a loss of one derivative, for example C^∞ ill-posedness.

- Computing the lower-order couplings near the defective characteristic set may help identify an applicable Levi-type criterion.
- A conclusion about Sobolev loss, smooth ill-posedness or Gevrey well-posedness requires a theorem whose hypotheses are verified for this system. Before any decisive claim, one must name the precise condition, the theorem connecting it to a conclusion, its multiplicity and regularity assumptions, and its neighbourhood or microlocal hypotheses, and say which of these have actually been checked.
- Failure of a proposed Levi condition would not by itself establish well-posedness in some Gevrey class.
- Scenarios A and B are **not** shown to exhaust the possibilities.

### B3. [CONJECTURE D: persistence away from the witness]

- **[ESTABLISHED AT THE WITNESS]** The stated Jordan pattern (algebraic multiplicity 6, two J₂ blocks) occurs at the selected parameter point on the Pauli slice q = λ√(2/3)·m.
- **[PROJECT RECORD]** GEN9 Theorem L4.1 extends the obstruction, at the symbol level, to every transversal crossing point of the 27 tested Pauli-slice parameter slices. This is a codimension-1 family of parameters and covector directions, not an open set. Recorded status: SUPPORTED. It relies on an identification of the curved-operator symbol at other parameter points that was not re-run there.
- **Off the slice [PROJECT RECORD, erratum G-66]:** exploratory computations at the tested values find that the degenerate double pair splits. Whether any Jordan defect survives at the shifted crossings is **open**.
- **The conjecture.** A Jordan chain of length 2 inside ker L persists at transversal crossings off the slice. If so, the theorem's argument would apply there. Persistence on an **open** set of parameters would need its own argument, with appropriate crossing and defect hypotheses. One additional off-slice example would not establish it.

### B4. [A numerical test]

A first experiment would reproduce linear-in-frequency growth in the frozen constant-coefficient constrained model. A separate variable-coefficient experiment would test whether, on a specified time scale, localised packets near frequency Λξ\* show the same behaviour. Any such experiment must:

- start from data that satisfy the constraints, and monitor constraint errors during the evolution;
- control the initial polarisation: not every datum excites the generalised eigenvector, so the data must be chosen to do so;
- separate discretisation and stability effects from the continuum mechanism, since grid-dependent growth alone is not diagnostic;
- treat absence of growth away from the crossing cone 𝒳 as an additional hypothesis to test, not an established prediction.

The result would be a numerical illustration or test of the proposed mechanism. Whether it is independent of this project depends on how it is implemented.

---

## Part C. Physical interpretations

Everything in Part C is interpretation. None of it is established, and none of it is used in the theorem.

### C1. [INTERPRETATION] Speed versus degeneracy

The theorem holds for every contraction speed c > 0, including speeds exceeding the characteristic speeds of A3, c > v₃. So the obstruction is not removed by shrinking the domain fast enough to accommodate a larger propagation speed. That suggests the obstruction is a **degeneracy**, eigenvectors coalescing at the transversal crossing (A4), rather than a matter of speed alone.

Velo and Zwanziger (1969) found characteristic speeds above light speed for the minimally coupled charged spin-3/2 field. Here a superluminal **phase speed** of one branch (A3) is what makes the crossing transversal, and the Jordan block at the crossing is what the theorem uses.

### C2. [SPECULATION] Two degeneracies

Deser and Waldron traced the onset of spin-3/2 acausality to a degeneracy: a gauge invariance that appears exactly at the onset ([hep-th/0112182](https://arxiv.org/abs/hep-th/0112182)). Here a different degeneracy appears exactly where the G-branch crosses the light branch. Whether these are related is an open question. Making it precise would require an explicit comparison of the two systems.

### C3. Known consistent constructions [literature]

- Known consistent constructions show that the outcome depends on the interaction structure and the background.
- Porrati and Rahman construct a non-minimally coupled massive charged spin-3/2 model in a constant external electromagnetic background, in which only physical degrees of freedom propagate, inside the light cone, without adding fields ([0906.1432](https://arxiv.org/abs/0906.1432)).
- Appropriate supergravity constructions provide known consistent realisations of a massive charged gravitino, subject to their coupling relations, background assumptions and retained field content. The literature also discusses pathologies in particular truncations; these are not interchangeable claims about every system called N = 2 supergravity (see, for example, [Rahman, 1111.3366](https://arxiv.org/abs/1111.3366)).
- Making the metric dynamical improves the causality bounds for spin 3/2 ([Deser–Waldron](https://arxiv.org/abs/hep-th/0112182)).
- Recent work revisits charged gravitinos on Einstein–Maxwell backgrounds, and compares supergravity and superstring realisations of a charged massive spin-3/2 particle (Krawczyk, Meissner, Nicolai and Sikorski, [2606.17139](https://arxiv.org/abs/2606.17139); Benakli, [2603.24670](https://arxiv.org/abs/2603.24670)).
- The present obstruction concerns a **different, specified system**: a fixed background, this Pauli coupling, this formulation. It should not be generalised to every charged spin-3/2 theory on a fixed background.

### C4. [SPECULATION] Fixed backgrounds and back-reaction

It is often suggested that a charged spin-3/2 field on a fixed background can be problematic, and that dynamical gravity changes the picture. Two different projects would test this here:

1. **Background consistency.** Determine whether this background (a product of two spheres with magnetic flux), or a nearby one, solves an appropriate Einstein–Maxwell or supergravity background system. This has not been checked.
2. **Dynamical coupling.** Analyse the coupled field equations, including perturbations of the metric and the gauge field, and ask whether the Jordan obstruction survives.

Solving the background equations would not by itself answer the second question.

### C5. [SPECULATION] An effective-theory reading

Well-posedness concerns arbitrarily high frequencies, where an effective field theory is not valid. Deser, Pascalutsa and Waldron note that loss of tree unitarity can be read as marking the scale at which an effective description stops being valid ([hep-th/0003011](https://arxiv.org/abs/hep-th/0003011)). A high-frequency obstruction like this one can motivate a similar question.

It does not by itself identify a cutoff, show the onset of new physics, or establish an equivalence with tree-unitarity breakdown. Inferring a scale would need a quantitative calculation, for example the frequency at which the growth contemplated in B1 becomes order one for physically normalised data. Comparing m² = 823/142944 with the field and curvature scales would need explicit normalisation and coupling-dependent dimensionless ratios.

### C6. [SPECULATION] A phase diagram

One could divide parameter space by the signs of (v₁² − 1, v₃² − 1):
- both negative: the G-branch is slower than light in every direction, and there is no crossing;
- both positive: the G-branch is faster than light in every direction, and there is again no transversal crossing;
- mixed signs: a transversal crossing exists, and by A4 a Jordan block is possible there, though not guaranteed.

Whether well-posedness behaves accordingly in each region is entirely open. A map of this kind would echo the mass–cosmological-constant diagrams that Deser and Waldron drew for spin-3/2 causality.

---

## Next steps

A fuller research plan, with priorities and success criteria, is in [ROADMAP.md](ROADMAP.md). These are listed roughly by value. None of them is expected to settle a question on its own; each says what it would add.

1. **Human expert review** of the proof. This matters more than anything below.
2. **Lower-order couplings near the defective set** (B1, B2): identify which Levi-type criterion, if any, applies, and check its hypotheses.
3. **The defect at off-slice crossings** (B3).
4. **The numerical tests** of B4, constant-coefficient first.
5. **The sign map** of (v₁² − 1, v₃² − 1) over parameter space (C6), from the formula in A1 at other parameter points.
6. **Background consistency and dynamical coupling** (C4), as two separate projects.
7. **Lean formalisation** of the witness algebra and of the checks in Part A.

If you work on any of these, or know where they are already answered in the literature, please open an issue.

---

*Written with AI assistance (Claude), directed by the project owner. Revised in v1.0.5 after a documentation review by Perplexity (two rounds); see CHANGELOG. The exact checks for Part A are in [`scripts/outlook_checks.py`](scripts/outlook_checks.py). Items labelled CONJECTURE, INTERPRETATION or SPECULATION are exactly that.*
