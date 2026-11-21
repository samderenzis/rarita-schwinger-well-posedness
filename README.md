# rarita-schwinger-well-posedness

**Exact algebraic witness and full verification suite for a well-posedness obstruction in charged, Pauli-coupled Rarita–Schwinger fields on ℝ×S²×S².**

![Status](https://img.shields.io/badge/status-preprint_·_not_peer_reviewed-orange?style=flat-square)
![Validation](https://img.shields.io/badge/validation-COMPLETE__PASS_35%2F35-brightgreen?style=flat-square)
![Code license](https://img.shields.io/badge/code-MIT-blue?style=flat-square)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24413648.svg)](https://doi.org/10.5281/zenodo.24413648)
![Text and data license](https://img.shields.io/badge/text_%26_data-CC_BY_4.0-lightgrey?style=flat-square)

---

## The result in one paragraph

For a charged, massive spin-3/2 (Rarita–Schwinger) field with Pauli coupling, on the background ℝ × S²(1) × S²(3) with a parallel magnetic field, the local Cauchy problem **cannot simultaneously have existence, uniqueness, and an L² energy bound that loses no derivatives** at the explicit parameter point λ² = 1/2, m² = 823/142944, π′ = 1/2 (Pauli slice). This holds on every sufficiently small backward light cone and at every Sobolev level ℓ ≥ 2. The obstruction is an exact, checkable algebraic object: after the constraints are eliminated, the principal symbol has a **Jordan block** (eigenvalue r = 101/99, two J₂ blocks) on the constraint-admissible directions. A necessity lemma turns this block into a contradiction with any loss-free bound.

📄 **Paper:** *link coming soon* · 🔖 **DOI:** [10.5281/zenodo.24413648](https://doi.org/10.5281/zenodo.24413648)

## Main theorem (informal statement)

> There is r\* ∈ (0, π/6] such that for every R ∈ (0, r\*/2), every integer ℓ ≥ 2, every c > 0 and every T ∈ (0, R/c), no constants K ≥ 1, α ≥ 0 make the following hold together on the backward light cones B_t = B_d(y₀, R − ct):
> **(E)** existence of H^ℓ solutions from every constrained H^ℓ datum,
> **(U)** uniqueness in the much larger class C¹(L²) ∩ C(H¹),
> **(B)** the loss-free bound ‖Φ(t)‖_{L²(B_t)} ≤ K e^{α(t−s)} ‖Φ₀‖_{L²(B_s)}.

The precise statement, definitions and complete proof are in the paper.

## The witness

At the covector ξ\* = (20/99, 0, 1, 0) and r = 101/99, there are exact vectors v ≠ 0 and w (entries in ℚ(i)) with

$$L v = 0,\qquad L w = 0,\qquad (P - r)\,v = 0,\qquad (P - r)\,w = v,$$

where P is the principal symbol of the reduced evolution operator and L that of the constraint. With $a_\gamma = v - i\gamma w$,

$$\big(\gamma - i(P - r)\big)\,a_\gamma = -\,i\gamma^2 w,$$

so any loss-free bound would give $|v| \le (1+K)\,\gamma\,|w|$ for all γ > 0, which forces v = 0, a contradiction.

The exact v, w, P, L and det S⁰ = 3063716808343140625 / 132101812606622109696 are in [`data/`](data/), readable without running anything.

## Check it yourself

Three levels, from no software at all to full re-computation:

1. **Read the certificate.** Open [`data/witness.txt`](data/witness.txt) and verify the four witness relations above by hand or with any computer algebra system. Or run the standard-library-only checker (no installs needed):
   ```bash
   python data/read_witness.py      # uses only Python's built-in fractions module
   ```
2. **Run the proof scripts** (a few minutes):
   ```bash
   pip install sympy
   cd scripts
   python witness_min.py              # det S⁰, LL† = 3|ξ|²I, the Jordan chain, the a_γ identity
   python check_1_clifford_intertwining.py   # and check_2 … check_5
   ```
   Each script prints `True` for every identity it verifies. The expected output is listed in [`results/golden_outputs.txt`](results/).
3. **Run the full validation suite** (5–30 minutes depending on level):
   ```bash
   pip install sympy numpy scipy mpmath python-flint requests
   python bhmap_validate_v1_5.py --level standard --online
   ```
   Run it from the repository folder: it detects the repository automatically. Use `--level deep` for the full stress test (about 30 minutes on a 12-core desktop); `--online` adds the citation checks (Crossref, arXiv). A complete run ends with `VERDICT: COMPLETE_PASS`.

   In this repository the archive checks verify the repository itself (every file against `SHA256SUMS`, the pinned scripts, and `data/witness.json` against a fresh recomputation). Three checks that need the project's private working archive (A2, A3, A5) are reported as **NA** (not applicable), listed, and never counted as passes. The owner's full-archive run is in [`results/`](results/).

## What the validation covers

| Group | What is checked | How |
|---|---|---|
| **A** Archive | file integrity, archived scripts reproduce their output | sha256 manifests, golden-output comparison |
| **B** Algebra | Clifford relations, intertwining identity, LL† = 3\|ξ\|²I, representation independence (incl. non-unitary and dense basis changes) | exact arithmetic |
| **C** Geometry & operators | connection and Einstein tensor re-derived from the metric; divergence and constraint identities | symbolic + 60-digit evaluation |
| **D** Witness | Jordan structure (alg. multiplicity 6, two J₂ blocks), determinants, chain identities | three independent engines (SymPy, FLINT, pure-Python fractions) |
| **E** Analysis | the key oscillatory H⁻¹ inequality (Lemma 4.1), coercivity constants, ball geometry | numerical falsification incl. an adversarial optimiser (worst ratio ≈ 0.50, limit 1) |
| **F** Logic | finite-dimensional models of the abstract argument | illustration only |
| **G** Literature | every cited DOI and arXiv identifier exists and matches | Crossref and arXiv APIs |
| **H** Self-tests | deliberately corrupted inputs must be caught | mutation tests of the checks themselves |

**Owner's deep run (Ryzen 9 9900X, full private archive, validator v1.4):** `COMPLETE_PASS`, 34 PASS + 1 INFO, all 35 checks. The published copy in `results/` has local paths and private-archive file listings removed; statuses and measurements are unchanged, and the hash of the unmodified original (`ec5b8f29…b1ce`) is recorded inside it. v1.5 adds repository mode and one check (A7).

## How this work was produced, and its status

This is **AI-collaborative research**. The project owner defined the programme, directed the work and ran the verification. Two AI systems (Claude and ChatGPT) acted as implementer and independent auditor, and the owner used Perplexity as needed for literature searches and physics cross-checks. Key lemmas were tested by statement-only blind derivations with hash-frozen records, every interface of the proof chain was audited, all computations were externally re-executed, and every failed attempt and correction was kept on record.

**What this does and does not establish:**
- ✅ The finite algebraic identities (the witness, the reduction identities) are verified exactly, by several independent programs.
- ✅ The analytic steps have complete written proofs, cross-checked by two AI systems; the key inequality survived extensive attempts to break it numerically.
- ⚠️ The proof has **not yet been reviewed by a human expert** and is **not formally machine-verified** (a Lean formalisation of the witness algebra is planned).
- ⚠️ The scope is narrow: one background, one parameter point, the Pauli slice. It rules out the three properties *together* and does not say which one fails. It makes no physical claims.

Feedback, especially from specialists in hyperbolic PDE and higher-spin fields, is very welcome.

## Repository contents

```
data/          witness.txt (readable), witness.json (exact, machine-readable), read_witness.py (stdlib-only checker)
scripts/       shared definitions + witness_min.py + check_1 … check_5 (the proof-carrying computations)
results/       owner's COMPLETE_PASS run (JSON, CSV) and the expected output of every script
paper/         the manuscript (PDF and LaTeX source), when released
bhmap_validate_v1_5.py   the validation suite (36 checks)
HOW_IT_WAS_CHECKED.md    verification method and provenance in brief
SHA256SUMS     fingerprints of every file      CITATION.cff   citation metadata
LICENSE        MIT (code)      CHANGELOG.md   version history
```

## Citation

Use GitHub's **"Cite this repository"** button (from `CITATION.cff`), or cite the Zenodo archive: [doi:10.5281/zenodo.24413648](https://doi.org/10.5281/zenodo.24413648). This DOI always resolves to the latest version; Zenodo also lists a DOI for each individual release.

## License

Code: [MIT License](LICENSE). Paper, witness data and validation results: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

Sam DeRenzis · waitandhope123@gmail.com · [GitHub](https://github.com/samderenzis)
