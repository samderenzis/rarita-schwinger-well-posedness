# Changelog

## Unreleased
- Added RUNNING_THE_VALIDATOR.md: setup, every option, levels, verdicts and statuses, output files, and how to compare a run with the published ones. Linked from README.md. The validator itself is unchanged.

## 1.0.1 (2026-11-21)
- Added the Zenodo DOI (10.5281/zenodo.24413648) to README.md and CITATION.cff.
- Validator v1.6 replaces v1.5. The first public repository-mode run (v1.5) failed check G1. Reproducing its reference scan showed two causes, neither a bad reference: the DOI badge's image address (the Zenodo DOI followed by `.svg`) was read as a DOI, and the validator scanned its own source code, where the bare arXiv DOI prefix (part of a rule for skipping arXiv DOIs) was read as a DOI. v1.6 normalises DOI-based image addresses and skips only the validator's own source file; a new self-test in H2 checks both. The DOI badge now uses an address without the raw DOI. v1.5 remains in the git history.
- Validator v1.7 replaces v1.6. The repository-mode run of v1.6 passed (COMPLETE_PASS, 32 PASS + 1 INFO + 3 NA), but before its results were added, a check showed that the reference scan also reads the validator's own outputs: a published results file quotes each DOI it checked (with JSON escapes and cut-off context), and the output folder holds a cache of whole Crossref records, including each cited paper's bibliography. Any re-run after publishing results, a second run in the same folder, or an archive run would have read these as citations (on the private archive: 4,251 candidate DOIs instead of 113). v1.7 skips the output folder and files recognised by exact content signature (results JSON and CSV, checkpoint, caches, timing history), lists every skipped file in the G1/G2 details, and adds an H2 self-test. On the private archive it finds exactly the 113 DOIs and 314 arXiv identifiers of the earlier v1.4 run. The v1.6 run is kept by the owner and not published here.
- First public validation of the repository itself: `results/public_run_v1_7_standard_COMPLETE_PASS.json` and `.csv` (validator v1.7, standard level, online; COMPLETE_PASS, 32 PASS + 1 INFO + 3 NA, all 36 checks accounted for). Published unmodified; JSON sha256 `41ad339f…b329`.

## 1.0.0 (2026-11-21)
- First public release: exact witness data (text, JSON, stdlib-only checker), the six proof-carrying scripts, validation suite v1.5 (repository mode), the owner's COMPLETE_PASS results, the method summary, citation metadata.
- The manuscript will be added in `paper/` in a later release.
