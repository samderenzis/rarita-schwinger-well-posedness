# Outlook: where this might lead

> **Read this as speculation.** The [README](README.md) states what is established. This page looks ahead: what the result *suggests*, what might be true, and what to compute next. Every item carries a label:
>
> - **[ESTABLISHED]**: part of the proved result or the frozen record.
> - **[NEW · exact · unaudited]**: an exact computation made on 2026-11-21 for this page. Run it yourself with `python scripts/outlook_checks.py` (sympy only, a few seconds). It is not part of the proof and has not been reviewed by anyone else.
> - **[CONJECTURE]**: a precise guess that a computation or proof could settle.
> - **[SPECULATION]**: an interpretation or analogy, offered to start a conversation.

---

## 1. The obstruction sits where a faster-than-light sheet meets the light cone

This is the most striking thing on this page, and the main reason it was written.

**What the computation shows** [NEW · exact · unaudited]. At the witness parameters, take the principal symbol P(ξ) of the reduced system for a unit covector. Light speed is 1 in the orthonormal frame. Its characteristic speeds are then exact:

| direction of ξ | speeds |
|---|---|
| along S²(1) | ±1, ±1/2, ±√(349353481/1750347625) ≈ **±0.4468** |
| along S²(3) | ±1, ±1/2, ±√(72301009/70013905) ≈ **±1.0162** |

- So one family of characteristics, called the "G-sheet" in the project's notes, is **anisotropic**. It is faster than light along the second sphere and slower than light along the first.
- The faster-than-light modes are not artefacts. Their whole eigenspace (dimension 4) lies **inside the constraint kernel** ker L, so they are constraint-satisfying, physical directions of the reduced system.
- Faster-than-light characteristics for charged spin-3/2 fields are exactly what Velo and Zwanziger found in 1969.

**Where the witness sits** [ESTABLISHED + NEW]. The G-sheet crosses the light cone on the cone of covectors

  𝒳 = {(v₁² − 1)|ξ_a|² + (v₃² − 1)|ξ_b|² = 0}.

Here ξ_a and ξ_b are the components along the two spheres, and v₁, v₃ are the speeds above.
- The witness covector ξ\* = (20/99, 0, 1, 0) satisfies this **exactly**.
- That is why the Jordan eigenvalue r = 101/99 equals |ξ\*|: the block sits **on the light cone**.
- The project's earlier work showed that such a crossing produces a Jordan block only when it is *transversal*, i.e. when (v₁² − 1)(v₃² − 1) < 0. When the two sheets coincide everywhere, the defect vanishes (GEN9, Theorem L3.2).

Put together: **the L² obstruction lives exactly on the boundary of the directions in which the field outruns light.**

**Why this is more than Velo–Zwanziger again** [ESTABLISHED that the theorem holds for every c; the interpretation is ours]. The theorem holds for *every* cone speed c > 0, including cones wider than the fastest characteristic, c > 1.0162. A failure caused only by signals outrunning the cone would disappear once the cone is wide enough. This one does not. The obstruction is a **degeneracy** (eigenvectors coalescing), not just a speed. The superluminal sheet is what *creates* the transversal crossing; the Jordan block at the crossing is what *breaks* the estimate.

**[SPECULATION]** Deser and Waldron traced the onset of the classic spin-3/2 acausality to a degeneracy: a gauge invariance that appears exactly at the onset ([hep-th/0112182](https://arxiv.org/abs/hep-th/0112182)). Here a different degeneracy appears exactly at the boundary of the superluminal directions. These may be two faces of the same phenomenon: the field equations "lose a direction" where the characteristic geometry changes type. Making that precise would be worthwhile.

## 2. Which of existence, uniqueness and the energy bound actually fails?

The theorem rules out all three *together*. Systems whose principal symbol has real eigenvalues but too few eigenvectors are called *weakly hyperbolic*, and their behaviour is well studied.

- The ADM formulation of Einstein's equations is the textbook example. It is only weakly hyperbolic, and numerical relativity learned to avoid it for that reason ([Sarbach et al., gr-qc/0205064](https://arxiv.org/abs/gr-qc/0205064)).
- Weakly hyperbolic systems may still be well posed, but only under very restrictive conditions on their lower-order terms. Following Kreiss and Ortiz (2002), they can show catastrophic exponential growth once lower-order terms or variable coefficients are added.

**[CONJECTURE A: derivative loss].** Solutions exist and are unique, so (E) and (U) hold, but they lose one derivative: the bound (B) fails and is replaced by ‖Φ(t)‖_{L²} ≲ ‖Φ₀‖_{H¹}. This is what a single J₂ block does in the constant-coefficient model, where solutions grow like 1 + |ξ|t.

**[CONJECTURE B: worse, if a Levi condition fails].** Whether Conjecture A holds is decided by the **lower-order terms acting on the generalised eigenspace**, a Levi-type condition in the sense of Ivriĭ–Petkov. If that condition fails, even C^∞ well-posedness is lost and only Gevrey classes survive.

**The good news: this is a finite computation.** Every ingredient is explicit in this repository: the lower-order terms of K′ come from known connection, potential and mass terms, and v and w are exact. Evaluating the Levi-type quantity at (y₀, ξ\*) is a natural next step, and would turn Conjectures A and B into a theorem one way or the other.

## 3. Is it the theory, or just this formulation?

A fair challenge to any ill-posedness result is that another formulation might avoid it. Numerical relativity escaped ADM's weak hyperbolicity by reformulating, with BSSN and generalised harmonic gauge.

- **[NEW · exact · unaudited]** The formulation here has a free constraint-addition parameter π′. Adding multiples of the constraint is the standard trick for repairing hyperbolicity. At ξ\*, the principal symbol **restricted to ker L** is identical for every π′ tested (0, 1/2, 2, −3/7), and the Jordan chain survives each time. The project's notes record the same independence in general (supported by computation, not proved).
- **[CONJECTURE C].** No constraint addition of this type removes the obstruction, because it lives entirely on constraint-satisfying directions, where constraint addition acts trivially.
- **[SPECULATION]** Reformulations that change the *field content* are a different matter: auxiliary fields, as in Porrati–Rahman, or Stückelberg fields. Section 5 comes back to this.

## 4. How special is the witness point?

- **[ESTABLISHED]** The exact pattern, algebraic multiplicity 6 with two J₂ blocks, belongs to the **Pauli slice** q = λ√(2/3)·m. Off the slice, exploratory computations at the tested values find that the degenerate double pair splits, and the crossing moves to nested-radical points.
- **[CONJECTURE D: persistence].** The *proof* needs only one Jordan chain of length 2 inside ker L. The project's earlier defect formula predicts at most a defect of 1 at the shifted crossings; that prediction has not been checked. If any defect survives, the same argument goes through off the slice too.
  - In that case loss-free L² well-posedness would fail on an open set of parameters, wherever the G-sheet is superluminal in some directions and subluminal in others, not just at one point.
  - This is the most consequential open computation.
- **[SPECULATION]** Picture the parameter space divided by the sign pattern of (v₁² − 1, v₃² − 1):
  - both negative: everything subluminal, no crossing, possibly well-posed;
  - both positive: superluminal, but with no transversal crossing;
  - **mixed signs**: crossings, and Jordan blocks on the light cone.

  A phase diagram of this kind would echo the mass–cosmological-constant diagrams that Deser and Waldron drew for spin-3/2 causality.

## 5. What this might say about physics

**What is known.** In N = 2 supergravity, a massive gravitino charged under the graviphoton propagates consistently. That consistency is an important exception to the general difficulty of charged higher spins ([Rahman, 1111.3366](https://arxiv.org/abs/1111.3366); [Porrati–Rahman, 0906.1432](https://arxiv.org/abs/0906.1432)).
- Making the metric dynamical improves the causality bounds for spin 3/2 ([Deser–Waldron](https://arxiv.org/abs/hep-th/0112182)).
- Recent work revisits charged gravitinos on Einstein–Maxwell backgrounds and compares the supergravity and superstring realisations of a charged massive spin-3/2 particle (Krawczyk, Meissner, Nicolai and Sikorski, [2606.17139](https://arxiv.org/abs/2606.17139); Benakli, [2603.24670](https://arxiv.org/abs/2603.24670)).

**The link to this work** [ESTABLISHED]. The project's divergence identity forces the Pauli coupling to the ratio familiar from supergravity. The project's notes record this as a standard mechanism, not a new result.

**[SPECULATION: frozen backgrounds are the problem].** This result fits the long-standing lore that a charged spin-3/2 field on a **fixed** background is sick even at supergravity-like couplings, and that consistency needs **back-reaction or extra fields**. Porrati and Rahman suggest causality may force other fields to exist besides the spin-3/2 one. This adds a sharper, mathematical version of the symptom: not just superluminal speeds, but the failure of a loss-free energy estimate.
- **Test:** couple the same field to dynamical gravity and the graviphoton, as in gauged supergravity, and check whether the Jordan block survives.

**[SPECULATION: an effective-theory reading].** Well-posedness concerns arbitrarily high frequencies, and an effective field theory is not valid there. Deser, Pascalutsa and Waldron already note that loss of tree unitarity merely signals the scale at which the effective description stops being valid ([hep-th/0003011](https://arxiv.org/abs/hep-th/0003011)). A Jordan block on the light cone could be read the same way: as a high-frequency signature that new physics must take over. The open question is *at which scale*, given that the witness mass is small (m² = 823/142944) compared with the field and curvature scales of the background.

**[SPECULATION: the background].** A product of two spheres threaded by magnetic flux resembles the flux backgrounds used in supergravity compactifications. Whether Model E, or a nearby background, solves the full Einstein–Maxwell(-sugra) equations has not been checked. If it does, the question in this section becomes concrete.

## 6. A prediction a computer can test

**[CONJECTURE E: numerical signature].** If the reduced system is discretised and initial data concentrated near frequency Λξ\* are evolved, then:
- the amplitude should grow roughly in proportion to **1 + Λt**, the signature of a J₂ block;
- the growth should get worse as the grid is refined, the hallmark of a weakly hyperbolic system;
- this growth should not appear for data supported away from the crossing cone 𝒳.

This experiment is cheap. It could run on a desktop machine, and it would give an independent, physical-looking confirmation of the mechanism.

## 7. Next steps, roughly in order of value

1. **Levi-type condition at (y₀, ξ\*):** settles Conjecture A versus B. Finite and exact.
2. **Defect at the off-slice crossings:** settles Conjecture D, and whether the obstruction is generic.
3. **The numerical experiment** of §6.
4. **Map the sign pattern** of (v₁² − 1, v₃² − 1) over parameter space (§4).
5. **Dynamical coupling** (§5): does back-reaction remove the block?
6. **Lean formalisation** of the witness algebra and of the new checks on this page.
7. **Human expert review** of the proof, which matters more than any of the above.

If you work on any of these, or know where they are already answered in the literature, please open an issue.

---

*Written with AI assistance (Claude), directed by the project owner. The exact checks for §1 and §3 are in [`scripts/outlook_checks.py`](scripts/outlook_checks.py). Everything labelled CONJECTURE or SPECULATION is exactly that.*
