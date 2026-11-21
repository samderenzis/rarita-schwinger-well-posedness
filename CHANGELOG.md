# Changelog

## Unreleased
- Added the Zenodo DOI (10.5281/zenodo.24413648) to README.md and CITATION.cff.
- Validator v1.6 replaces v1.5. The first public repository-mode run (v1.5) failed check G1 for two reasons, neither a bad reference: the DOI badge's image address (the Zenodo DOI followed by `.svg`) was read as a DOI, and the validator scanned its own source code, where the bare arXiv DOI prefix (part of a rule for skipping arXiv DOIs) was read as a DOI. v1.6 normalises DOI-based image addresses and skips only the validator's own source file; a new self-test in H2 checks both. The DOI badge now uses an address without the raw DOI. v1.5 remains in the git history.

## 1.0.0 (2026-11-21)
- First public release: exact witness data (text, JSON, stdlib-only checker), the six proof-carrying scripts, validation suite v1.5 (repository mode), the owner's COMPLETE_PASS results, the method summary, citation metadata.
- The manuscript will be added in `paper/` in a later release.
