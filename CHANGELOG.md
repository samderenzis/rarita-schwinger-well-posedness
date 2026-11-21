# Changelog

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
