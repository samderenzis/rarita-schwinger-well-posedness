# Background: why charged spin-3/2 fields are hard, and the common pitfalls

> **What this page is.** Context for readers new to the area, and a checklist of traps for anyone working in it. It explains the problem, why it has resisted easy answers for decades, and which mistakes are easy to make. The last section summarises the kinds of mistake this project itself made and caught.
>
> This page contains no new results. The [README](README.md) states what is established, [OUTLOOK.md](OUTLOOK.md) collects conjectures, and [ROADMAP.md](ROADMAP.md) sets out the research plan. Every reference below is listed with its DOI or arXiv number at the end. Descriptions of other people's work are short summaries, and the original papers are the authority.

---

## 1. The problem in brief

A spin-3/2 particle, such as the gravitino of supergravity or certain baryon resonances, is described by the **Rarita–Schwinger equation** (Rarita and Schwinger, 1941). The standard free massive equation in flat spacetime provides a consistent starting point. Interactions introduce additional compatibility, degree-of-freedom and propagation conditions that must be checked for each model. Some couplings fail these checks; others pass, as the remedies listed below show.

- **Gravity (1958).** Buchdahl studied whether the equations remain compatible in a gravitational field.
- **Quantum inconsistency (1961).** Johnson and Sudarshan showed that, for the local quantum theory of a charged spin-3/2 field in an external electromagnetic field, the equal-time quantisation relations and relativistic covariance are incompatible. (Their abstract speaks of "commutation relations"; for a fermion field these are anticommutators.) The result concerns that theory, not every interacting spin-3/2 construction.
- **Classical acausality (1969).** Velo and Zwanziger showed that, with the simplest ("minimal") coupling to an external electromagnetic potential, the classical field propagates non-causally: some of its waves travel faster than light. This is now called the **Velo–Zwanziger problem**.
- **Further inconsistencies (1975).** Seetharaman, Prabhakaran and Mathews found inconsistencies of spin-3/2 theories in homogeneous magnetic fields.
- **Proposed remedies:**
  - modified wave equations (Khalil, 1977);
  - supergravity, where the spin-3/2 field is coupled to dynamical gravity (Deser and Zumino, 1976);
  - non-minimal couplings, with their causality bounds (Deser, Pascalutsa and Waldron, 2000; Deser and Waldron, 2002; Porrati and Rahman, 2009; Rahman, 2013);
  - recent work on charged spin-3/2 fields in constant and Einstein–Maxwell backgrounds (Benakli, Daniel and Ke, 2023; Delplanque and Skvortsov, 2024; Benakli, 2026; Krawczyk, Meissner, Nicolai and Sikorski, 2026).
- **Revisited (2003).** The Velo–Zwanziger phenomenon itself was revisited by Frauendiener.

Porrati and Rahman (2009) point out a general difficulty that runs through this whole history: writing down a Lagrangian does not by itself guarantee that only physical degrees of freedom propagate, or that they propagate causally, once the field is coupled to external or dynamical fields. Each coupling has to be checked.

## 2. Different kinds of test

Two checks appear often in the physics literature on coupled spin-3/2 theories (among others; this is not a complete list, and well-posedness has also been studied there):

1. **Can the constraints be solved?** Some components of the field (here, the time component ψ₀) have no evolution equation of their own and must be determined by a constraint. Degeneracy can change the constraint structure; determining the resulting number of degrees of freedom requires further analysis. An algebraic elimination failure is one part of that, not the full constraint analysis.
2. **Are the characteristic cones real and causal?** Non-real principal eigenvalues can produce growth rates proportional to spatial frequency, which obstructs a uniform high-frequency estimate. Real principal eigenvalues avoid that particular mechanism, but do not rule out growth or guarantee well-posedness. Causality, propagation no faster than light, is a further requirement.

The mathematical theory of hyperbolic equations asks an additional, distinct question: **does the initial-value problem admit an energy estimate?** For first-order systems, the standard notion is L² well-posedness: solutions exist, are unique, and are bounded in L² by their initial data, without losing derivatives. This is closely tied to whether the system's principal symbol can be diagonalised or symmetrised in a uniform way (Kreiss, 1962; Strang, 1966 and 1967; Ivriĭ and Petkov, 1974; Métivier, 2014; and the textbooks of Benzoni-Gavage and Serre, 2006, and Rauch, 2012).

Causality and energy-estimate well-posedness are different requirements, not weaker and stronger versions of one test. Solvability of the algebraic elimination relation and a real spectrum at a selected covector do not suffice for the stated loss-free estimate. This project supplies an exact example of that distinction. It does not establish that the system passes an all-directions causality test.

## 3. Why it is hard

### Real speeds are not enough
Weak hyperbolicity requires real characteristic eigenvalues. Strong hyperbolicity additionally requires a uniformly controlled complete set of characteristic modes. A Jordan block is one explicit obstruction to strong hyperbolicity. For variable coefficients, the well-posedness theory also needs regularity of the coefficients and a suitable symmetriser; pointwise diagonalisability alone does not settle the problem.
- Kreiss and Ortiz (2002), who use "weakly hyperbolic" in contrast to "strongly hyperbolic", explain that strongly hyperbolic systems tolerate lower-order terms (under the usual regularity and boundedness assumptions on the coefficients). For systems that are weakly but not strongly hyperbolic, suitable lower-order perturbations can destroy well-posedness.
- In a constant-coefficient model with a 2 × 2 Jordan block, data with a suitable generalised-eigenvector component produce a term proportional to frequency times time. Not every polarisation excites that growth.

So "all characteristic speeds are real" says little on its own.

### Lower-order terms and variable coefficients matter
For weakly hyperbolic systems, terms that are usually negligible can decide the outcome.
- Nagy, Ortiz and Reula (2004) note that variable-coefficient weakly hyperbolic systems are unstable under perturbations of their lower-order terms and of their initial data.
- Whether a weaker kind of well-posedness survives depends on conditions on the lower-order terms (so-called Levi conditions). This is a specialised theory of its own (for example, Garetto, Jäh and Ruzhansky, 2018; Colombini, Nishitani and Rauch, 2019).
- A curved background with a magnetic field brings both lower-order terms and variable coefficients.

### Constraints change the question
A spin-3/2 field carries constraints, and these interact with hyperbolicity in subtle ways.
- For the constrained continuum problem, one must identify which field polarisations satisfy the principal constraints. For a full evolution formulation or numerical implementation, the behaviour of constraint-violating modes may also matter. Uniform hyperbolicity claims require consideration of all relevant spatial covectors. Abalos and Reula (2020) and Abalos (2022) study strong hyperbolicity for systems with constraints.
- Numerical relativity met related issues with Einstein's equations. Kreiss and Ortiz (2002) analyse, among other cases, the ADM equations linearised around flat space with constant lapse and shift, and discuss how the choice of lapse changes the hyperbolicity conclusion. So "ADM is weakly hyperbolic" depends on the formulation and gauge. Reformulations with better hyperbolicity properties have mattered for numerical work (Nagy, Ortiz and Reula, 2004; Sarbach and Tiglio, 2012), though better hyperbolicity alone does not guarantee stable, convergent simulations.

### The answer can depend on how the equations are written
The same physical theory can be written in different ways: different constraint additions, different choices of variables, extra auxiliary fields. Some of these are mere rewritings that cannot change the answer; others genuinely change the system.
- A naive first-order form of minimal dRGT massive gravity, a theory of a massive spin-2 field, is only weakly hyperbolic for exactly this Jordan-block reason, and can be reformulated (Kożuszek and Wiseman, 2024).
- Telling a rewriting apart from a genuine repair takes care.

### Local versus global, fixed versus dynamical
- Many constructions, including this one, work on a coordinate patch with a local electromagnetic potential. Global questions, such as charge quantisation on a compact space, are separate.
- A test field on a **fixed** background is not the same system as the field coupled to **dynamical** gravity and electromagnetism. Results for one need not carry over to the other.

## 4. Common pitfalls, and how this project handles them

"The paper" below is the project's paper, version 2; see [paper/](paper/).

| Pitfall | Why it is a trap | How this project handles it |
|---|---|---|
| Reading "real speeds" as "well-behaved" | Real eigenvalues do not guarantee a complete, uniformly controlled set of modes (§3) | The theorem exhibits this at one covector: a real spectrum there, a constrained Jordan block, and no loss-free estimate |
| Confusing wave directions with field polarisations | Wave directions (covectors), field polarisations inside or outside ker L, and constraint-violating modes of a full evolution formulation are different things. For the constrained continuum problem, an obstruction must affect admissible polarisations. For a full evolution formulation or a numerical implementation, constraint violations may also matter. Either way, a claim about all wave directions needs all relevant covectors checked | The Jordan chain consists of admissible polarisations, inside ker L, at one selected covector (paper §5). No claim about all directions is made |
| Assuming the constraints "take care of themselves" | Keeping constraints satisfied in the evolution is a separate question | The paper uses only the exact algebraic identity R⁰K′ = 𝒞R⁰, and says what it does not prove |
| Mistaking a rewriting for a repair | Constraint additions act trivially on the constrained directions | The paper proves the witness is the same for the whole π′ family of constraint additions (Prop. 5.1) and claims nothing for other reformulations |
| Trusting floating-point arithmetic near a degeneracy | Small perturbations and floating-point computations can obscure or split a defective eigenvalue, making multiplicity and Jordan structure difficult to determine reliably | The witness certificate is checked exactly over ℚ(i); other identities use the symbolic or algebraic arithmetic appropriate to their stated scope (symbolic parameters, radicals). Exact arithmetic verifies the encoded calculation; it does not by itself verify that the code encodes the intended equations |
| Freezing coefficients and stopping there | A frozen-coefficient Jordan block does not by itself defeat a variable-coefficient estimate | A variable-coefficient necessity lemma with wave packets and an exact constraint correction (paper §4, Appendix B) |
| Equating phase speed with signal speed | For weakly hyperbolic systems the usual link to domains of dependence fails | OUTLOOK keeps characteristic speeds separate from any causality claim |
| Treating one exact example as a family result | Jordan blocks can split under perturbation | The result is stated at one parameter point; families are left to ROADMAP §2 |
| Reading physics into a fixed-background result | The coupled system is different | No physical claim is made; physics questions are separate projects (OUTLOOK Part C) |

## 5. Lessons from this project's own mistakes

The project keeps an errata register (74 entries so far, G-1 to G-74, in the project's archive) and never deletes a mistake. The kinds of error it caught are typical of careful mathematical work, and some are specific to work done with AI systems. They may be useful to others.

- **Overstatement creeps in at every stage.** The most common error was wording that claimed more than had been shown: "loses exactly one derivative", "robust", "new", "constraint propagates to all orders", "decisive finite computation". These were caught by audits and reviews, and corrected repeatedly, in internal reports, the paper draft, the README and OUTLOOK. *Lesson:* review scope and wording separately from the mathematics, more than once.
- **Generalising instead of re-deriving.** A remark about other spacetime dimensions extended a fixed coefficient (⅓) instead of solving for it, and was wrong. Another remark about general metrics was withdrawn. *Lesson:* a formula verified in one case has to be re-derived, not extrapolated.
- **Numerics are unreliable near degeneracies.** Early attempts to locate crossings and compute Levi-type indicators failed in this project: an eigenvalue solver did not converge at a repeated root, and a double-precision conversion lost the structure. Repeated or nearly defective eigenvalues make numerical identification of crossings, multiplicities and Jordan structure unreliable without additional error control or exact verification. *Lesson:* this is why the project checks its algebraic certificates exactly.
- **Checks should be designed to detect incorrect inputs, and their failure-detection behaviour should itself be tested; tools can also read their own output.** The validation suite includes deliberate-corruption tests, which it must detect. Even so, two versions of its literature check were fooled: one by a badge address, one by its own results files, which it read as citations. *Lesson:* test the tests, and keep a tool's outputs out of its own inputs.
- **Blind tests are only as good as their packets.** A statement-only test packet once omitted a key definition, and a summary once misrepresented the structure of a lemma. Both were caught and the packets re-issued. *Lesson:* a blind derivation tests the packet as much as the proof.
- **The hardest step shows itself.** Two separate statement-only attempts at the necessity lemma each stopped at the same point: the two-derivative oscillatory estimate (paper, Lemma 4.5; the archive calls it Lemma 4.1). Both were fresh ChatGPT sessions given the same statement-only packet. They are recorded in the archive as GEN17 (first attempt) and GEN25 (repeat). They are separate sessions of one AI system, not independent review. *Lesson:* where such attempts stall is where review should look hardest.
- **Proof routes change, and records must keep up.** One older erratum describes a proof route that was later replaced. The records have to say which route is current; a note on this is being added for the next review.
- **Citations need checking too.** Several errata fix author names, numbering or attributions. One description of a published paper (Porrati–Rahman) said the opposite of its abstract and was corrected after review. *Lesson:* check what a source says, not only that it exists.
- **Keep the failures.** Every failed computation and withdrawn claim stays on record, labelled. This makes the history auditable, and stops a failed approach from being silently retried.

The project records corrections and their assessed impact. Those assessments remain subject to review; the existence of an errata register does not itself establish that all remaining results are correct. Catching these mistakes took several distinct kinds of check:
- AI mathematical audits by a second system;
- statement-only blind tests;
- code re-execution;
- exact re-computation;
- a validation suite with self-tests;
- documentation and scope reviews of the paper and these pages.

None of these is independent replication, and **none replaces review by a human expert**, which the project has not yet had.

---

## References

Each DOI below has been checked to resolve, with metadata matched on Crossref. That checks identifiers only. It does not verify any summary on this page.

**What was checked against the sources (2026-11-21, by Claude):**
- Johnson–Sudarshan: the abstract (first page of the paper).
- Porrati–Rahman: the arXiv abstract.
- Kreiss–Ortiz: excerpts of the arXiv text (gr-qc/0106085), on strong versus weak hyperbolicity and lower-order terms.
- Nagy–Ortiz–Reula: excerpts of the arXiv text (gr-qc/0402123), on variable-coefficient weak hyperbolicity.

The ADM gauge qualification was confirmed by Perplexity at abstract level against the Kreiss–Ortiz arXiv abstract (gr-qc/0106085). That abstract discusses ADM linearised around flat space with constant lapse and shift, its weak hyperbolicity in that setting, and a different lapse choice yielding strong hyperbolicity. This is not a full-text audit.

**What was not checked:** the other summaries follow the introduction of the project's paper. They have not been checked against the sources beyond DOI and metadata.

The documentation review of this page was selective. It was not an exhaustive verification of the bibliography.

- W. Rarita, J. Schwinger, *On a theory of particles with half-integral spin*, Phys. Rev. 60 (1941) 61. [doi:10.1103/PhysRev.60.61](https://doi.org/10.1103/PhysRev.60.61)
- H. A. Buchdahl, *On the compatibility of relativistic wave equations for particles of higher spin in the presence of a gravitational field*, Nuovo Cimento 10 (1958) 96. [doi:10.1007/BF02859608](https://doi.org/10.1007/BF02859608)
- K. Johnson, E. C. G. Sudarshan, *Inconsistency of the local field theory of charged spin 3/2 particles*, Ann. Phys. 13 (1961) 126. [doi:10.1016/0003-4916(61)90030-6](https://doi.org/10.1016/0003-4916(61)90030-6)
- G. Velo, D. Zwanziger, *Propagation and quantization of Rarita–Schwinger waves in an external electromagnetic potential*, Phys. Rev. 186 (1969) 1337. [doi:10.1103/PhysRev.186.1337](https://doi.org/10.1103/PhysRev.186.1337)
- M. Seetharaman, J. Prabhakaran, P. M. Mathews, *Rarita–Schwinger particles in homogeneous magnetic fields, and inconsistencies of spin-3/2 theories*, Phys. Rev. D 12 (1975) 458. [doi:10.1103/PhysRevD.12.458](https://doi.org/10.1103/PhysRevD.12.458)
- S. Deser, B. Zumino, *Consistent supergravity*, Phys. Lett. B 62 (1976) 335. [doi:10.1016/0370-2693(76)90089-7](https://doi.org/10.1016/0370-2693(76)90089-7)
- M. A. K. Khalil, *Relativistic wave equations without the Velo–Zwanziger pathology*, Prog. Theor. Phys. 58 (1977) 1538. [doi:10.1143/PTP.58.1538](https://doi.org/10.1143/PTP.58.1538)
- S. Deser, V. Pascalutsa, A. Waldron, *Massive spin 3/2 electrodynamics*, Phys. Rev. D 62 (2000) 105031. [doi:10.1103/PhysRevD.62.105031](https://doi.org/10.1103/PhysRevD.62.105031)
- S. Deser, A. Waldron, *Inconsistencies of massive charged gravitating higher spins*, Nucl. Phys. B 631 (2002) 369. [doi:10.1016/S0550-3213(02)00199-2](https://doi.org/10.1016/S0550-3213(02)00199-2)
- J. Frauendiener, *On the Velo–Zwanziger phenomenon*, J. Phys. A 36 (2003) 8433. [doi:10.1088/0305-4470/36/31/306](https://doi.org/10.1088/0305-4470/36/31/306)
- M. Porrati, R. Rahman, *Causal propagation of a charged spin 3/2 field in an external electromagnetic background*, Phys. Rev. D 80 (2009) 025009. [doi:10.1103/PhysRevD.80.025009](https://doi.org/10.1103/PhysRevD.80.025009)
- R. Rahman, *Helicity-1/2 mode as a probe of interactions of a massive Rarita–Schwinger field*, Phys. Rev. D 87 (2013) 065030. [doi:10.1103/PhysRevD.87.065030](https://doi.org/10.1103/PhysRevD.87.065030)
- K. Benakli, C. A. Daniel, W. Ke, *Spin-3/2 and spin-2 charged massive states in a constant electromagnetic background*, JHEP 03 (2023) 212. [doi:10.1007/JHEP03(2023)212](https://doi.org/10.1007/JHEP03(2023)212)
- W. Delplanque, E. Skvortsov, *Massive spin three-half field in a constant electromagnetic background*, JHEP 08 (2024) 173. [doi:10.1007/JHEP08(2024)173](https://doi.org/10.1007/JHEP08(2024)173)
- K. Benakli, *The two lives of a massive charged spin-3/2 particle: from superstrings EFT to supergravity*, JHEP 06 (2026) 117. [doi:10.1007/JHEP06(2026)117](https://doi.org/10.1007/JHEP06(2026)117)
- A. Krawczyk, K. A. Meissner, H. Nicolai, B. Sikorski, *Planck mass gravitinos in Einstein–Maxwell backgrounds*, Phys. Rev. D 114 (2026) 045013. [doi:10.1103/qpnl-91n5](https://doi.org/10.1103/qpnl-91n5)
- H.-O. Kreiss, *Über die Stabilitätsdefinition für Differenzengleichungen die partielle Differentialgleichungen approximieren*, BIT 2 (1962) 153. [doi:10.1007/BF01957330](https://doi.org/10.1007/BF01957330)
- G. Strang, *Necessary and insufficient conditions for well-posed Cauchy problems*, J. Differential Equations 2 (1966) 107. [doi:10.1016/0022-0396(66)90066-0](https://doi.org/10.1016/0022-0396(66)90066-0)
- G. Strang, *On strong hyperbolicity*, J. Math. Kyoto Univ. 6(3) (1967) 397. [doi:10.1215/kjm/1250524339](https://doi.org/10.1215/kjm/1250524339)
- V. Ya. Ivriĭ, V. M. Petkov, *Necessary conditions for the Cauchy problem for non-strictly hyperbolic equations to be well-posed*, Russian Math. Surveys 29 (1974) 1. [doi:10.1070/RM1974v029n05ABEH001295](https://doi.org/10.1070/RM1974v029n05ABEH001295)
- G. Métivier, *L² well-posed Cauchy problems and symmetrizability of first order systems*, J. Éc. polytech. Math. 1 (2014) 39. [doi:10.5802/jep.3](https://doi.org/10.5802/jep.3)
- S. Benzoni-Gavage, D. Serre, *Multi-dimensional Hyperbolic Partial Differential Equations*, Oxford University Press (2006). [doi:10.1093/acprof:oso/9780199211234.001.0001](https://doi.org/10.1093/acprof:oso/9780199211234.001.0001)
- J. Rauch, *Hyperbolic Partial Differential Equations and Geometric Optics*, AMS Graduate Studies in Mathematics 133 (2012). [doi:10.1090/gsm/133](https://doi.org/10.1090/gsm/133)
- C. Garetto, C. Jäh, M. Ruzhansky, *Hyperbolic systems with non-diagonalisable principal part and variable multiplicities, I: well-posedness*, Math. Ann. 372 (2018) 1597. [doi:10.1007/s00208-018-1672-1](https://doi.org/10.1007/s00208-018-1672-1)
- F. Colombini, T. Nishitani, J. Rauch, *Weakly hyperbolic systems by symmetrization*, Ann. Sc. Norm. Super. Pisa Cl. Sci. 19 (2019) 217. [doi:10.2422/2036-2145.201610_006](https://doi.org/10.2422/2036-2145.201610_006)
- F. Abalos, O. Reula, *On necessary and sufficient conditions for strong hyperbolicity in systems with constraints*, Class. Quantum Grav. 37 (2020) 185012. [doi:10.1088/1361-6382/ab954c](https://doi.org/10.1088/1361-6382/ab954c)
- J. F. Abalos, *On constraint preservation and strong hyperbolicity*, Class. Quantum Grav. 39 (2022) 215004. [doi:10.1088/1361-6382/ac88af](https://doi.org/10.1088/1361-6382/ac88af)
- H.-O. Kreiss, O. E. Ortiz, *Some mathematical and numerical questions connected with first and second order time-dependent systems of partial differential equations*, in *The Conformal Structure of Space-Times: Geometry, Analysis, Numerics*, Lecture Notes in Physics 604 (Springer, 2002) 359–370. [doi:10.1007/3-540-45818-2_19](https://doi.org/10.1007/3-540-45818-2_19); [arXiv:gr-qc/0106085](https://arxiv.org/abs/gr-qc/0106085)
- G. Nagy, O. E. Ortiz, O. A. Reula, *Strongly hyperbolic second order Einstein's evolution equations*, Phys. Rev. D 70 (2004) 044012. [doi:10.1103/PhysRevD.70.044012](https://doi.org/10.1103/PhysRevD.70.044012); [arXiv:gr-qc/0402123](https://arxiv.org/abs/gr-qc/0402123)
- O. Sarbach, M. Tiglio, *Continuum and discrete initial-boundary value problems and Einstein's field equations*, Living Rev. Relativ. 15 (2012) 9. [doi:10.12942/lrr-2012-9](https://doi.org/10.12942/lrr-2012-9)
- J. Kożuszek, T. Wiseman, *Well-posedness of minimal dRGT massive gravity*, [arXiv:2410.19491](https://arxiv.org/abs/2410.19491) (2024; v2 2026).

---

*Written with AI assistance (Claude), directed by the project owner, and revised after a documentation and scope review by Perplexity (2026-11-21). The scope of the literature checking is stated above the reference list.*
