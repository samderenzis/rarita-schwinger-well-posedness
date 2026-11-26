# Changelog

## Unreleased
Correction only. No paper, code, data or results file changed.
- ROADMAP §2 no longer says the follow-up repository [rarita-schwinger-off-slice](https://github.com/samderenzis/rarita-schwinger-off-slice) has "no results yet". It points to that repository's README for its status, and states that its results are AI-checked only and not part of this result. Statements elsewhere that describe the off-slice question as open describe this result's scope and are unchanged.

## 1.0.11 (2026-11-22)
Documentation only. No paper, code, data or results file changed.
- README: the Citation section now gives a reference for the paper (rxiVerse:2611.0051), as well as the existing one for the code and data.

## 1.0.10 (2026-11-22)
Documentation only. No paper, code, data or results file changed.
- The paper (version 2, the same PDF) is posted on rxiVerse as [2611.0051](https://rxiverse.org/abs/2611.0051). README, paper/README.md and CITATION.cff link to it.
- README and ROADMAP link to the follow-up repository [rarita-schwinger-off-slice](https://github.com/samderenzis/rarita-schwinger-off-slice), which holds the exploratory work on ROADMAP §2. Nothing there is part of this result.
- paper/README.md gains a Corrections section. It corrects an unsupported explanation in paper/CHANGES_v2.md about a PDF hash in an internal, unpublished package. That package was internally consistent; the differing hash came from an erroneous report in an AI review. CHANGES_v2.md itself is unchanged.

## 1.0.9 (2026-11-21)
Adds the paper. No code, data or results file changed.
- New: `paper/` holds paper version 2, which is the release candidate after the ChatGPT review. It contains:
  - `main.pdf` and its LaTeX source (`main.tex`, `refs.bib`, `build.sh`);
  - `audit/num_audit.py`;
  - `CHANGES_v2.md`;
  - `FINAL_RELEASE_REPORT.md`;
  - `VERSIONS.txt`.

  The PDF builds reproducibly from this source. Its SHA-256 is in `SHA256SUMS` and `paper/README.md`.
- The paper's data statement cites repository release v1.0.8 for the code and data. Those files are unchanged in this release.
- README, ROADMAP, OUTLOOK, BACKGROUND and HOW_IT_WAS_CHECKED now point to the posted paper in place of the "frozen candidate, not yet public". HOW_IT_WAS_CHECKED has a new section on the version 2 release checks, which says who ran which check.
- BACKGROUND references are aligned with the paper's bibliography:
  - Strang (1967) under the journal's 1967 name, *J. Math. Kyoto Univ.*, with first page 397;
  - the volume number for Colombini–Nishitani–Rauch;
  - the full title and volume number of the Kreiss–Ortiz book (Lecture Notes in Physics 604).

## 1.0.8 (2026-11-21)
Documentation only. No code, data or results file changed; the frozen paper candidate is untouched. Corrections follow the full AI review by ChatGPT of the frozen candidate and the archive (GEN33).
- HOW_IT_WAS_CHECKED.md:
  - the validator review is now "26 findings: 24 fixed, 1 in part, 1 documented". It said "all were fixed", an overstatement already corrected in the paper but missed here;
  - new section on the ChatGPT review: what it executed, what it read, what it found, and its scope.
- RUNNING_THE_VALIDATOR.md: the opening now says the validator re-checks the claims covered by the selected mode, and that the reference check confirms identifiers. Archive checks are not applicable in public-repository mode.
- README: "proof-carrying scripts" → "exact-check scripts". They are exact-arithmetic checks, not formal proof objects.
- OUTLOOK A5: clarified that the Jordan chain survives any symbol-level reduction because P_h agrees with P on ker L. The project record's further claim that ker L is P_h-invariant needs the premise P(ker L) ⊆ ker L, which holds here by the paper's Prop. 5.1(b).
- BACKGROUND references: Strang (1967) issue 3; Kreiss–Ortiz book title and pages, from Crossref.

## 1.0.7 (2026-11-21)
Documentation only. No code, data or results file changed; the frozen paper candidate is untouched.
- Added BACKGROUND.md. It covers:
  - the history of the charged spin-3/2 problem, from Rarita–Schwinger (1941) through Johnson–Sudarshan (1961) and Velo–Zwanziger (1969) to recent work;
  - physics tests versus energy-estimate tests;
  - why the area is hard: weak versus strong hyperbolicity, lower-order terms and variable coefficients, constraints, formulation dependence, local versus global and fixed versus dynamical;
  - a table of common pitfalls and how this project handles them;
  - a summary of the kinds of mistake recorded in the project's errata register.

  Every reference has a checked DOI or arXiv number. Literature descriptions follow the paper's introduction, with additional statements checked against the original abstracts or texts.
- BACKGROUND was revised before release after a documentation and scope review by Perplexity (13 points):
  - removed the claim that the theorem shows a theory passing both physics tests (no all-directions causality is established);
  - "third, sharper question" → "an additional, distinct question";
  - weak and strong hyperbolicity are now defined correctly (a Jordan block is one obstruction to strong hyperbolicity);
  - non-real eigenvalues and frequency-proportional growth are distinguished from well-posedness;
  - the J₂ growth needs suitable polarisation;
  - the interaction opening is narrowed;
  - constraint degeneracy no longer automatically changes the count of degrees of freedom;
  - wave directions are separated from polarisations and constraint-violating modes;
  - the numerical claims are qualified;
  - the exact-arithmetic scope is stated (ℚ(i) for the witness certificate only);
  - the blanket errata assurance is replaced by an impact-record statement;
  - the blind attempts are identified (GEN17, GEN25: separate sessions of one AI, not independent review);
  - "tests that cannot fail" is reworded;
  - the ADM summary is qualified by formulation and gauge;
  - the Johnson–Sudarshan summary is made precise;
  - the actual scope of literature checking is stated above the references.

  The links were checked and are relative.
- Final follow-up from the same review (3 points), applied before release:
  - the remaining blanket sentence about constraint-allowed directions is replaced with the reviewer's wording on polarisations, constraint-violating modes and covectors;
  - "weakly but not strongly hyperbolic" is used for the Kreiss–Ortiz lower-order statement, with the coefficient assumptions noted;
  - the links were re-verified as relative in the file (the claude.ai/chat addresses come from the chat rendering).
- Checking record: the ADM gauge qualification was confirmed by Perplexity at abstract level against Kreiss–Ortiz gr-qc/0106085 (not a full-text audit).
- The reviewer's final disposition: this round is closed. It is not certification of every literature summary, the private errata records, the computational implementation, or the complete mathematical proof.
- README: links to BACKGROUND.md (reader signposts, the Open questions section, and the Repository contents table). The README's Repository contents section was already a table (layout-only commit 4f6699ef after v1.0.6).

## 1.0.6 (2026-11-21)
Documentation only. No code, data or results file changed; the frozen paper candidate is untouched.
- Added ROADMAP.md: a research plan, adapted from a planning suggestion by Perplexity, with references to this project's scripts and records. It covers:
  - priority order: secure the existing result; is the witness isolated?; severity; rewritings versus repairs; a positive regime; geometry; numerics; physics as separate projects;
  - evidence labels;
  - a bounded plan for the next question: the defect at off-Pauli-slice crossings near the witness, with what is reused, what is missing, the certificates needed, success and failure criteria, and what it would not establish.
- README: links to ROADMAP.md. The OUTLOOK pointer now says OUTLOOK had a documentation and scope review only and is not independently verified (it previously said "not assessed in any review", which was out of date after v1.0.5).
- OUTLOOK.md: the Next steps section links to ROADMAP.md.
- ROADMAP revised before release, after Perplexity's review of the draft (8 points):
  - evidence categories are no longer presented as a ladder;
  - the off-slice question no longer presupposes the on-slice branch structure, and gives a five-step sequence;
  - the negative outcome is limited to the tested crossings, with "no crossing found" reported separately;
  - Milestone 1 (one exact off-slice witness, hypotheses re-checked) is separated from Milestone 2 (a family argument);
  - reusable scope is stated accurately: witness_min.py and bhmap_defs.py hard-wire the Pauli slice; the π′ factorisation must be re-verified along the family; pointwise versus uniform coercivity;
  - the S^ρ-constancy explanation is tied to the parallel-field and product-geometry properties;
  - the §6 criterion must say what it adds beyond the existing necessity lemma.

  The links were checked and are relative repository links. Adopted as the working plan.
- Final housekeeping from the reviewer's disposition: "no crossing found" is reworded as "the search did not locate a real crossing…", with no exclusion claimed without an exact argument. The reviewer accepted the roadmap as a coherent research plan. This is not confirmation of the script-inspection findings, the private records, or any new result.

## 1.0.5 (2026-11-21)
Documentation and one added check. No proof script, data or results file changed. OUTLOOK.md was revised after a documentation review of OUTLOOK by Perplexity (source-page level; it did not run the script). The frozen paper candidate is untouched.
- OUTLOOK.md was reorganised into A (additional exact algebraic claims), B (mathematical conjectures) and C (physical interpretations), with a status label and specific support for each item.
- **New exact result (A1):** the full dispersion relation for a symbolic covector, det(x − P(ξ)) = (x² − v₁²|ξ_a|² − v₃²|ξ_b|²)²(x² − |ξ|²)⁴(x² − |ξ|²/4)², with multiplicities, and the crossing cone obtained by subtracting the light branch. Added to `scripts/outlook_checks.py` (check 5), together with eigenspace dimensions and ker L membership at random covectors (check 6, regression only).
- Corrected or narrowed:
  - "physical directions" is no longer inferred from ker L membership;
  - phase speed is now distinguished from group velocity and signal propagation;
  - the reversed "wider cones" wording is replaced by "contraction speed";
  - "the fastest characteristic" is now supported by A1;
  - Conjecture A no longer claims that (E) holds and is restated in a shifted Sobolev scale;
  - the claim that a finite Levi-type test is decisive is removed;
  - the Porrati–Rahman description is corrected (their model needs no additional fields);
  - the Pauli-slice "ESTABLISHED" label is narrowed to the witness;
  - the open-set claim is removed;
  - GEN9 results (L2.3, L3.1, L3.2, L4.1, L5.1) are given with their statements and recorded statuses;
  - the supergravity-ratio remark is restated as a Clifford compatibility identity (α = 1/3 in 5D, cf. G-67), not a characterisation of supergravity;
  - the numerical proposal is now a test with stated controls;
  - the EFT reading is explicitly limited;
  - background consistency is separated from dynamical coupling;
  - Conjecture C is replaced by the established π′ result plus an open question.
- README: the pointer to OUTLOOK describes the new observations as principal-symbol statements.
- Second-round follow-up from the same review, applied before release:
  - the opening review status now says this page had a documentation and scope review, and that its computations, records and conclusions have not been independently verified; PAPER items are distinguished from the additional claims;
  - the quotient branch ±|ξ|/2 is identified by its quotient origin only, since v₁ < 1/2 < v₃ means it coincides with the G-branch in some directions;
  - 𝒳 is described as a smooth conic hypersurface in ξ ≠ 0;
  - "the defect needs" is replaced by "the tested records associate";
  - B1 and B2 are relabelled as research questions;
  - the general-dimension Pauli coefficient is kept as an unverified project record, with its source and limits;
  - "that is the theorem" is replaced by the package-failure wording;
  - the supergravity summary is qualified by model, background and field content.
- Final reference-clarity edit in A5 (third round): "The defect is unchanged under the constraint additions and symbol-level reductions explicitly described above. No claim is made for the other reformulations just listed."
- The reviewer's disposition: "The revised OUTLOOK is appropriately qualified as a research outlook. The specific scope and reasoning objections raised in this documentation review have been addressed. Its additional symbolic identities, computational claims, and private project records remain unverified in this review." This is not verification of A1–A6, not execution of outlook_checks.py, and not certification of the mathematical conclusions. This version is preserved for the planned full review.

## 1.0.4 (2026-11-21)
Documentation only. No code, data or results file changed. The README and related pages were brought in line with the frozen paper candidate, following a documentation review by Perplexity.
- README:
  - "the constraint propagates exactly, to all orders" replaced: the identities show that K′ maps constrained fields to constrained fields, which is the property the proof uses; propagation for arbitrary reduced solutions is not claimed;
  - "backward light cones" replaced by "shrinking geodesic cones" (any speed c > 0, not physical light cones);
  - the informal theorem now states "for every start time s ∈ [0, T) with the same K and α" and "for all t ∈ [s, T]";
  - the real spectrum is stated for the selected covector only;
  - the π′-independence result is added, scoped to this family of constraint additions;
  - the one-command checker is distinguished from the reduction and the analytic lemma;
  - the COMPLETE_PASS badge is explained as the validator's verdict, not certification;
  - the literature check is labelled identifiers and metadata only;
  - "three independent engines" → "three different engines";
  - "complete written proofs" → "written proofs".
- OUTLOOK:
  - the faster-than-light observation is labelled in the README and in OUTLOOK.md as an additional claim outside the main theorem, supported only by `scripts/outlook_checks.py` and not assessed in any review;
  - the π′ item is now marked established in the paper (this family only), and Conjecture C is settled for that family.
- Numbering: the oscillatory H⁻¹ estimate is Lemma 4.5 in the paper. The validator and the published results files keep the earlier name "Lemma 4.1"; those historical records are unchanged, and the difference is explained.
- HOW_IT_WAS_CHECKED.md: new section on the Perplexity manuscript review and its limits, in the reviewer's own words. "independent physics cross-checks" → "physics cross-checks". RUNNING_THE_VALIDATOR.md: "independent re-check" → "more thorough re-check".
- paper/README.md: the paper is written and frozen as a candidate under review; it will be posted after the review.

## 1.0.3 (2026-11-21)
- Added OUTLOOK.md: conjectures, speculation and next steps, each labelled ESTABLISHED / NEW (exact, unaudited) / CONJECTURE / SPECULATION. New exact observations, checked by `scripts/outlook_checks.py` (not part of the proof; not externally reviewed): along S²(3) one family of characteristics is faster than light (speed² = 72301009/70013905), along S²(1) slower (349353481/1750347625); its eigenspace lies in ker L; the witness covector satisfies the light-cone crossing condition exactly; P restricted to ker L(ξ\*) and the Jordan chain are independent of the constraint-addition parameter π′ for every value tested. README links to OUTLOOK.md.
- Added the owner's full-archive run of validator v1.7 (standard level, online): COMPLETE_PASS, 34 PASS + 1 INFO + 1 NA (A7, repository-only), all 36 checks accounted for; 7,314/7,314 archive files, 114/114 DOIs, 314/314 arXiv identifiers, H2 16/16. `results/owner_run_v1_7_archive_standard_COMPLETE_PASS.json` is sanitised as before (local paths and private-archive listings removed; statuses and measurements unchanged; original sha256 recorded inside); the CSV is unmodified. The v1.4 run is kept.
- README: published runs shown as one table; wording corrected where it overstated the checking ("all computations were externally re-executed" → the proof-carrying scripts were re-executed by the second AI; "independent programs" → separate programs and engines; not independently replicated, stated explicitly); the paper is marked as in preparation rather than implied to exist; the BHMAP name is explained. New README sections: "In plain terms", "Why this question" (background, using only references the validator checks), "The proof at a glance" (diagram of links L0–L6), the witness checker's expected output, "Open questions" and "Key references"; a collapsible "For specialists" section (setup, exact reduction, coercivity, the constrained necessity lemma and its key oscillatory estimate, the full Jordan data, and what is deliberately not claimed), taken from the frozen core document; signposts at the top for new readers and specialists. HOW_IT_WAS_CHECKED.md: states that ChatGPT reviewed validator v1.0, and that later versions have not had a second external review; same wording corrections.

## 1.0.2 (2026-11-21)
- Added RUNNING_THE_VALIDATOR.md: setup, every option, levels, verdicts and statuses, output files, and how to compare a run with the published ones. Linked from README.md. The validator itself is unchanged.

## 1.0.1 (2026-11-21)
- Added the Zenodo DOI (10.5281/zenodo.24413648) to README.md and CITATION.cff.
- Validator v1.6 replaces v1.5. The first public repository-mode run (v1.5) failed check G1. Reproducing its reference scan showed two causes, neither a bad reference: the DOI badge's image address (the Zenodo DOI followed by `.svg`) was read as a DOI, and the validator scanned its own source code, where the bare arXiv DOI prefix (part of a rule for skipping arXiv DOIs) was read as a DOI. v1.6 normalises DOI-based image addresses and skips only the validator's own source file; a new self-test in H2 checks both. The DOI badge now uses an address without the raw DOI. v1.5 remains in the git history.
- Validator v1.7 replaces v1.6. The repository-mode run of v1.6 passed (COMPLETE_PASS, 32 PASS + 1 INFO + 3 NA), but before its results were added, a check showed that the reference scan also reads the validator's own outputs: a published results file quotes each DOI it checked (with JSON escapes and cut-off context), and the output folder holds a cache of whole Crossref records, including each cited paper's bibliography. Any re-run after publishing results, a second run in the same folder, or an archive run would have read these as citations (on the private archive: 4,251 candidate DOIs instead of 113). v1.7 skips the output folder and files recognised by exact content signature (results JSON and CSV, checkpoint, caches, timing history), lists every skipped file in the G1/G2 details, and adds an H2 self-test. On the private archive it finds exactly the 113 DOIs and 314 arXiv identifiers of the earlier v1.4 run. The v1.6 run is kept by the owner and not published here.
- First public validation of the repository itself: `results/public_run_v1_7_standard_COMPLETE_PASS.json` and `.csv` (validator v1.7, standard level, online; COMPLETE_PASS, 32 PASS + 1 INFO + 3 NA, all 36 checks accounted for). Published unmodified; JSON sha256 `41ad339f…b329`.

## 1.0.0 (2026-11-21)
- First public release: exact witness data (text, JSON, stdlib-only checker), the six proof-carrying scripts, validation suite v1.5 (repository mode), the owner's COMPLETE_PASS results, the method summary, citation metadata.
- The manuscript will be added in `paper/` in a later release.
