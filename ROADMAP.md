# Roadmap: how this work could be extended

> **What this page is.** A research plan, not a set of results. The [README](README.md) states what is established, and [OUTLOOK.md](OUTLOOK.md) collects conjectures and interpretations. This page says what to do next, in what order, and how each step would be judged. Nothing here changes the frozen paper candidate or the status of the theorem. Extensions will be recorded separately as they happen.
>
> Adapted from a planning suggestion by Perplexity (2026-11-21), with references to this project's existing scripts and records added by Claude, and revised after Perplexity's review of the draft. It is adopted as the working plan.

## The overall goal

Turn one exact counterexample into a verified account of when these equations admit reliable evolution, when they do not, and what causes the difference.

Conclusions should not grow faster than the proofs behind them. Every result is labelled by the kind of claim it is:

| Kind of evidence | Example |
|---|---|
| exploratory numerics | a sweep of parameters in floating point |
| an exact check at one point | the witness Jordan chain |
| a symbolic identity | the dispersion relation in OUTLOOK A1 |
| a theorem over a parameter family | (none public yet) |
| a positive well-posedness result | (none yet) |
| a physical interpretation | OUTLOOK Part C |

These are different kinds of claim, not successive grades: an exact check at one point does not become a family theorem through review, and an interpretation is not a stronger kind of evidence than a proof. Each claim is classified by its scope, supporting evidence, and review status separately. Broader conclusions require additional mathematical arguments. External review can assess those arguments but does not itself expand their scope. Agreement between this project's own scripts is code consistency, not independent confirmation.

## Priority order

1. **Secure the existing result** (§1).
2. **Is the witness isolated?** *The next project:* determine the nearby off-slice characteristic structure, locate any crossings, and certify the constrained Jordan structure at selected exact points (§2).
3. **How severe is the failure?** Derivative loss or worse (§3).
4. **Rewritings versus repairs**, and **a positive regime** (§4, §5).
5. **Generalise the local mechanism** (§6).
6. **Physics extensions**: coupled gravity and interpretation, as separate projects (§8).

Numerics (§7) support steps 2–5 but replace none of them.

The long-term target: **a verified family of constrained obstructions, together with one contrasting regime that admits a positive well-posedness result.** That would begin to answer when the equations fail, why, how badly, and what prevents it.

---

## 1. Secure the existing result

Before substantial extensions, the frozen result should be reviewed and reproduced outside the implementation process. Ideally:

- a specialist in hyperbolic PDE reviews the analytic argument (paper §4 and Appendix B);
- a specialist in higher-spin fields checks the model and the literature comparison;
- someone outside this project reproduces the algebra.

**Review package.** Most of it already exists:

| Needed | Where it is |
|---|---|
| field equations and conventions | paper §2–3 |
| reduction and transfer argument | paper §3, scripts `check_1`–`check_5` |
| constrained necessity lemma | paper §4, Appendix B |
| explicit witness | `data/witness.json`, `data/witness.txt`, `data/read_witness.py` |
| minimal reproduction | [Check it yourself](README.md#check-it-yourself), [RUNNING_THE_VALIDATOR.md](RUNNING_THE_VALIDATOR.md) |
| dependency versions and checksums | `SHA256SUMS`; tool versions recorded with the frozen paper |
| which claim each script checks | paper Appendix A, Table 3 |

**Still to do:** post the paper once the planned ChatGPT review is complete, and invite human expert review.

**Deliverable:** a reproducible foundation with a documented review status.

## 2. Is the witness isolated, or part of a family?

Start near the witness rather than scanning all parameters and backgrounds.

**Central question.** When mass, charge, coupling, curvature or field strength change slightly, does the constrained Jordan obstruction disappear, or does it move to another covector?

Persistence cannot be inferred from the original defective matrix, because Jordan blocks can split under perturbation. Crossings, and the conditions for a defect at them, have to be tracked.

**Workflow.**
1. Explore nearby parameters.
2. Locate the characteristic crossings.
3. Check geometric multiplicities and constrained Jordan chains.
4. Look for exact or symbolic patterns.
5. Prove a parameter-family statement where possible.

**Deliverable:** a parameter map that distinguishes, where established:
- invertible versus singular elimination matrices (det S⁰);
- non-real characteristic eigenvalues;
- real spectra with defective eigenvectors;
- regions where the constrained symbol is uniformly controlled.

Sampled evidence and proved regions get separate labels.

### The bounded plan for the next question

**The question.** Off the Pauli slice (q ≠ λ√(2/3)·m), near the witness: do nearby characteristic crossings exist, and does the constrained symbol (P restricted to ker L) have a nontrivial Jordan chain at any of them?

On the slice, the project's records report defect 2 at every crossing on 27 tested slices (GEN9, Theorem L3.1, exact per slice). Off the slice they report that the degenerate double eigenvalue splits at the tested values, and the defect question is **open** (erratum G-66). So the on-slice factorisation and branch names (light branch, G-branch) must **not** be assumed to continue off the slice.

**Sequence.**
1. Derive the off-slice characteristic structure: factor the characteristic polynomial of P(ξ) for symbolic ξ at nearby parameter values.
2. Determine which branches can be continued from the slice or identified.
3. Locate any real crossings near the witness.
4. Test the constrained operator for defects at those crossings.
5. Convert promising examples into exact certificates.

**What can be reused, and its actual scope.**
- `scripts/witness_min.py` and `scripts/bhmap_defs.py` build S^ρ, P and L in exact arithmetic for given values of m, λ, b₁, b₂ and π′. **Both hard-wire the Pauli slice:** the charge is set as q = λ√(2/3)·m. (The factor `kap` in witness_min.py scales λ in both q and the Pauli term, so it does not move off the slice.) Going off the slice therefore needs a code change that makes q an independent parameter.
- The divergence identity (paper, Prop. 3.2) is stated for general q. Whether the scripts that check it (`check_3`, `check_4`) tested q independently of λ and m must be inspected, and the reduction re-verified with q free, before off-slice symbols are trusted.
- **π′-independence.** The paper's Prop. 5.1(a) rests on the symbolic factorisation P_{π′} − P_{π″} = (π′ − π″)M⁻¹TL. Verify that this factorisation through L remains valid throughout the proposed family, wherever the reduction is defined (det S⁰ ≠ 0, M invertible).
- **Coercivity.** The principal constraint symbol satisfies LL† = 3|ξ|²I independently of the parameters, which is useful. But the small-ball argument also needs control of the lower-order coefficients (the constant m₀ in paper §4.2). An estimate on a sufficiently small ball at each fixed parameter point is not the same as a uniform estimate on a common ball for a whole family; the second does not follow automatically from the first.
- `scripts/outlook_checks.py` (check 5): the method for factoring the characteristic polynomial for symbolic ξ.
- The GEN9 methods for exact rank computation along a crossing family.

**What is missing.**
- A parametrisation of the off-slice family near the witness, for example q = (1 + ε)·λ√(2/3)·m.
- Exact arithmetic beyond ℚ(i). The project's notes place off-slice crossings at nested-radical points, so ranks must be computed over algebraic number fields.
- det S⁰ ≠ 0 along the family.

**Exploratory computations.** For a few small ε, carry out steps 1–4 in high-precision arithmetic, to decide where exact work is worthwhile.

**Exact certificates needed, at a chosen parameter point.**
- The crossing covector, as an exact algebraic number.
- The ranks of (P − r)^j restricted to ker L, over the corresponding number field.
- If a defect is found, an explicit chain v → w inside ker L, as for the witness.

**Milestones.**
- **Milestone 1:** one exact off-slice constrained Jordan chain, with every hypothesis needed by the analytic argument re-checked at that parameter point: det S⁰ ≠ 0, the reduction identities, coercivity on some ball, and the curved-symbol identification. The paper's argument would then apply at that point. This is a second pointwise witness, not a family theorem.
- **Milestone 2:** a parametrised argument establishing where such chains exist, and where the required reduction and analytic hypotheses hold (including uniformity, if a common ball is wanted). Only this would support a family-level statement. Persistence on an open set needs its own proof.

**Possible outcomes, reported separately.**
- *Positive:* an exact constrained Jordan chain at a tested off-slice crossing, which leads to Milestone 1.
- *Negative:* the selected off-slice crossings are exactly semisimple. This rules out the proposed Jordan mechanism at those tested crossings only. It does not establish that all off-slice directions are free of defects: another crossing direction, another eigenvalue, or a different obstruction is not excluded.
- *No crossing found:* the search did not locate a real crossing near the witness at the tested parameters. This does not show that no real crossing exists in any specified neighbourhood; that would need an exact exclusion argument. It is a different result from finding a crossing and proving it semisimple, and is reported as such.

**What this would not establish.**
- Persistence on an open set of parameters.
- Which of existence, uniqueness or the bound fails.
- Anything about physics.

Pointwise results are reported as pointwise results. Family-level and open-set conclusions are reserved for separate proofs.

## 3. How severe is the failure?

The theorem rules out the conjunction of the specified existence, uniqueness and loss-free bound. It does not say which property fails.

**Investigate whether the system admits:**
- well-posedness in a shifted Sobolev scale, with derivative loss;
- a stronger instability that obstructs well-posedness for smooth data;
- failure of existence or uniqueness in a specified class.

Before asserting any result, state the function spaces, data class, constraints, domains, time interval and continuity estimate.

**Workflow.**
1. Analyse the frozen constant-coefficient constrained model.
2. Determine which lower-order couplings matter.
3. Study them near the defective characteristic set.
4. Identify an applicable theorem.
5. Verify its regularity, multiplicity and microlocal hypotheses.

One frozen lower-order computation does not settle the variable-coefficient problem. Relevant literature includes work on hyperbolic systems with non-diagonalisable principal part, such as Garetto–Jäh–Ruzhansky; its applicability must be shown, not assumed.

**Deliverable:** a precise statement of how badly prediction fails, or of what weaker well-posedness remains. (OUTLOOK B1–B2 describe the two scenarios.)

## 4. Rewritings versus repairs

The paper shows that the π′ family of constraint additions does not remove the witness. The project's records extend this to symbol-level reductions (GEN9, Proposition L5.1).

**Next, analyse carefully:**
- admissible invertible changes of variables;
- broader reductions of the same constrained equations;
- alternative non-minimal couplings;
- enlarged formulations with additional variables or fields.

**For each proposal, record whether it:**
1. preserves the same solution space;
2. changes only the representation or reduction;
3. changes the regularity requirements;
4. changes the underlying equations or physical model.

**Central question.** Can an equivalent formulation restore the estimate, or must the underlying system change?

The work of Abalos and Reula on strong hyperbolicity of constrained constant-coefficient systems, and their matrix-pencil methods, is a relevant comparison. Its conclusions cannot be transferred to this variable-coefficient setting without a verified bridge.

**Deliverable:** a theorem about a clearly specified class of reductions, or an explicit alternative model with a proved improvement.

## 5. Prove positive cases, not only obstructions

A complete picture needs regimes where well-posedness can actually be proved. Find a tractable parameter regime and try to establish:

- a uniformly bounded symmetriser, or a comparable estimate;
- compatibility with the constraints;
- a positive result for the variable-coefficient system, in clearly specified domains and function spaces.

A real spectrum, or failing to find a Jordan block, is not enough by itself.

**Deliverable:** a verified positive regime compared with a verified defective one, explaining what protects the equations and what destroys that protection. Counterexamples locate failures; positive and negative results together begin to locate the boundary.

## 6. Generalise the geometry, after the local mechanism is understood

Does the obstruction depend essentially on:
- the product-of-spheres background;
- the parallel magnetic field;
- the anisotropy of the curvature;
- the spacetime dimension;
- the chosen mass/Pauli ansatz?

**Questions.**
- Does the mechanism survive small geometric perturbations?
- Can it be expressed through local geometric and electromagnetic quantities?
- Which parts of the exact reduction survive? The present construction uses the specific parallel-field and product-geometry properties that make S^ρ constant in the chosen frame. An extension must identify which of these properties are needed, and what survives under perturbation.
- Can the constraint correction and the necessity argument still be justified?

**Longer-term target.** The paper's necessity lemma, combined with a constrained Jordan chain, already gives a criterion: wherever its hypotheses hold, a chain inside ker L at a real eigenvalue rules out the loss-free package. A new deliverable here has to add something to that. It must say which of these it is:
- a clean, reusable corollary of the existing result, stated for a general class of constrained systems (useful, but a repackaging, and labelled as such);
- an extension to weaker or different hypotheses, for example non-constant frame matrices S^ρ, or a weaker coercivity condition;
- a geometric characterisation of which backgrounds and fields satisfy the hypotheses;
- a classification of the backgrounds and parameters that produce the defect.

A characteristic crossing alone is not sufficient (OUTLOOK A4), so the model-specific coupling and defect hypotheses must be included in any of these.

**Deliverable:** one of the above, with what it adds beyond the existing argument stated explicitly. The present example is one application.

## 7. Numerics, as a controlled supporting project

Begin with the frozen constant-coefficient model, then localised packets in the variable-coefficient system. Requirements:
- appropriate initial polarisation;
- data compatible with the constraints;
- monitoring of constraint errors;
- convergence and stability checks;
- separation of discretisation artefacts from continuum growth;
- an explicitly stated time and frequency regime.

Numerics can illustrate the mechanism, test conjectures and guide exact work. They do not replace proof. An experiment is called independent only if its implementation and provenance justify it. (OUTLOOK B4 has the details.)

## 8. Physics extensions, as separate projects

Once the mathematics is clearer:
- compare with known consistent higher-spin constructions;
- check whether the background satisfies appropriate coupled background equations;
- study the full perturbation system with dynamical gravity and gauge fields;
- consider effective-theory interpretations.

Keep these distinct, because none follows automatically from another:
- background consistency;
- consistency of a test field on that background;
- well-posedness of the fully coupled perturbation system;
- causal propagation;
- validity of an effective theory.

---

## How progress will be recorded

- The frozen paper candidate is not changed. Any later correction goes into a new version with a change log.
- Each extension gets its own record, with its evidence label from the table above, in this repository's CHANGELOG and the project archive.
- Each claim keeps its scope, evidence and review status recorded separately. Broader conclusions need new mathematical arguments; review assesses those arguments but does not widen their scope.

If you would like to work on any of these, or know where one is already answered in the literature, please open an issue.
