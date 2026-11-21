# Final release report: paper version 2 (release candidate), 2026-11-21

**This is the second issue of the release candidate.** The first issue was `paper_v2_rc_2026-11-21_1546`. The second issue changes this report only, to make the hash provenance in section G unambiguous after ChatGPT's review of the first issue. main.tex, refs.bib and main.pdf are byte-identical to the first issue.

Input: `paper_v2_2026-11-21_1537`, plus ChatGPT's final targeted review. Output: this package. The frozen predecessor, the 15:37 package and the first issue are preserved unchanged.

## A. Changes made
- **refs.bib, one line:** the Strang 1967 journal is now its 1967 name, *Journal of Mathematics of Kyoto University*. It was the current name, *Kyoto Journal of Mathematics*. The generator `tools/make_bib.py` got the corresponding fix-up line, and its output path now points to this working copy.
- **main.tex:** unchanged from 15:37 (byte-identical).
- **Generated files:** main.pdf (rebuilt), VERSIONS.txt, DIFF_vs_frozen.txt, SHA256SUMS. CHANGES_v2.md was updated to record the correction.
- **Second issue:** this report only. Section G was rewritten, a record of who ran each check was added under section E, and sections F and I were updated. VERSIONS.txt and SHA256SUMS were regenerated. No source, PDF, bibliography or result changed.
- No theorem, proof, witness, parameter, characteristic polynomial, Jordan chain, constraint count, number or scope statement changed. **PASS**

## B. Bibliographic verification
- **Strang 1967 journal name: PASS.** Verified against the article's own first page ("J. Math. Kyoto Univ. 6-3 (1967) 397-417") and the MaRDI/zbMATH record ("Journal of Mathematics of Kyoto University"). Title, author, volume, issue (3), year and pages (397–417) are unchanged.
- **Rendered bibliography: PASS.** Reference [19] reads: "Gilbert Strang. On Strong Hyperbolicity. Journal of Mathematics of Kyoto University, 6(3):397–417, 1967. doi: 10.1215/kjm/1250524339." The DOI is unchanged.
- **Citations: PASS.** 33 entries, 33 cited, none missing, none uncited.
- No unrelated bibliography change. **PASS**

## C. Build results
- `./build.sh` exits 0; pdflatex and bibtex complete; 27 pages. **PASS**
- Undefined references, citations or commands: 0. **PASS**
- Overfull boxes: 0. **PASS**
- Underfull boxes: 2, the long repository URL in the last reference; cosmetic. **PASS**
- BibTeX warnings: 0. **PASS**
- Reproducible: two consecutive builds give the identical main.pdf. **PASS**
- PDF built from the final source: **PASS**. It was rebuilt after the refs.bib change, and a fresh rebuild from the extracted archive was checked (section F).

## D. Numerical audit results
- `python3 audit/num_audit.py data/witness.json main.tex`: exit 0, 19/19 assertions, "ALL PASS". Exact arithmetic (SymPy over ℚ(i)). **PASS**

## E. Exact-check results
All were executed in this workspace (Python 3.13.18, SymPy 1.14.0). Outputs are in VERSIONS.txt.

| Script | Exit | Result | Kind |
|---|---|---|---|
| data/read_witness.py | 0 | PASS | exact |
| scripts/witness_min.py | 0 | PASS | exact |
| scripts/check_1_clifford_intertwining.py | 0 | PASS | exact symbolic |
| scripts/check_2_geometry.py | 0 | PASS | exact symbolic |
| scripts/check_3_divergence_identity.py | 0 | PASS | exact symbolic |
| scripts/check_4_constraint_intertwining.py | 0 | PASS | exact symbolic |
| scripts/check_5_principal_symbol.py | 0 | PASS | exact symbolic, at the witness point and covector |
| review check, λ = +1/√2 | 0 | PASS | exact; π′ symbolic; random covectors are regression only |
| review check, λ = −1/√2 | 0 | PASS | exact; π′ symbolic; random covectors are regression only |
| charpoly_pip.py | 0 | PASS | exact symbolic in π′ |
| sign_cmp.py | 0 | PASS | exact |

- Golden-output comparison (check_1 to check_5, witness_min): **PASS**. Every reference line is present, and no output contains "False".
- Numerical stress tests (validator families E and H): **NOT RUN** in this step. They are not part of the paper's proof. The last published runs are in the repository's results/ folder.
- scripts/outlook_checks.py: **NOT APPLICABLE**. OUTLOOK is not part of the paper.

### Who ran each check
| Check | Claude, this release | ChatGPT, independently | Inherited from earlier records | Status |
|---|---|---|---|---|
| LaTeX/BibTeX build, 0 errors, 27 pages | executed | **not run** (BibTeX unavailable in its environment) | — | PASS (Claude only) |
| Reproducible build; rebuild from fresh extraction | executed | **not run** | — | PASS (Claude only) |
| Numerical audit, 19/19 | executed | executed on the first issue | — | PASS |
| SHA-256 manifest, archive CRC | executed | executed on the first issue (11/11 files) | — | PASS |
| Strang correction in refs.bib and in the rendered PDF | executed | inspected on the first issue | — | PASS |
| Citation count, 33/33 | executed | — | — | PASS |
| Exact-check scripts, golden outputs | executed | — | ChatGPT's earlier full review (GEN33) reported re-running the scripts in its own environment | PASS |
| Validator families E and H (numerical stress tests) | not run | not run | published runs in the repository's results/ | NOT RUN in this release |
| Human expert review of the mathematics | — | — | none | NOT RUN |

Claude and ChatGPT are both AI systems working from this project's own files. Neither column is independent human verification.

## F. Hash and archive verification
- main.tex: `517c74709c802f2e94b95baf7378912fc08216c0ac37778e80efbe0007cc45db`
- refs.bib: `278218f478a50d203b301685e471a30d319b356132110e466d58894777139985`
- main.pdf: `41522f919bed08719fa9ec16314162ad44c1155d3896dcb3f450a4c69adbe3f3`
These are the hashes of **this release candidate**. They are identical to the first issue's, because only this report changed.
- SHA256SUMS is regenerated after all files are final, and every entry is verified.
- The archive CRC test, extraction into a fresh directory, manifest verification of the extracted files, and a rebuild from the extracted source giving a byte-identical main.pdf are run after packaging.
- These after-packaging checks cannot be recorded inside the archive they test. Their commands, exit codes and results are in `VERIFICATION_LOG.txt`, delivered alongside the archive.
- The archive's own SHA-256 cannot be stored inside the archive. It is recorded in the accompanying `.sha256` file and in the delivery message.

## G. Files preserved unchanged
Each row gives the hashes of **that** package's own files, as listed in its own SHA256SUMS. Only the last row is the current release candidate. Its hashes are in section F.

| Package | Role | main.tex | refs.bib | main.pdf | zip |
|---|---|---|---|---|---|
| `paper_candidate_FROZEN_2026-11-21_1022` | frozen predecessor (version 1) | 15d085ba… | 26c635ab… | b6df56ff… | 75e5296a… |
| `paper_v2_2026-11-21_1537` | version 2 before the Strang fix | 517c7470… | 296f5740… | 3f5f3a93… | a57e2cb7… |
| `paper_v2_rc_2026-11-21_1546` | release candidate, first issue | 517c7470… | 278218f4… | 41522f91… | 576f07eb… |
| this package | release candidate, second issue | 517c7470… | 278218f4… | 41522f91… | in `.sha256` file |

- The frozen predecessor's hashes (15d085ba…, 26c635ab…) are **not** hashes of any version 2 file. They are listed only to show that the frozen predecessor, and Claude's working copy of it, are unchanged.
- The first three packages were re-hashed before this issue was made, and all match.
- **Historical records, earlier validation outputs and released archives (GEN1–GEN34):** not modified.
- **Repository:** not changed in this step. The latest release is v1.0.8 (commit 554eedb0). An update adding this paper as v1.0.9 has been prepared for the owner to upload. It is not published, and no tag has been created or changed.

## H. Remaining limitations
- AI-collaborative work, checked by AI systems only. **No human expert review. Not independently replicated:** the re-executions used the project's own code, data and conventions. **Not formally verified** (Lean is future work).
- **The result** is a model-specific, local obstruction to the conjunction of existence, uniqueness and a loss-free L² estimate, at one parameter point, on one fixed background, in one formulation. It does not identify which property fails.
- **Not established:**
  - other parameter points;
  - persistence under arbitrary reformulations;
  - global results;
  - superluminal signal propagation or any causality violation;
  - any physical consequence.

  Principal-symbol characteristic speeds are not signal speeds.
- The paper is not yet in the public repository. The publication plan is in `PUBLICATION_PLAN.md`, delivered alongside the archive.

## I. Final release recommendation
Every check that was run passed. The only change since the first issue is the wording of this report. The numerical stress tests were not re-run in this step (section E); they are not part of the proof.

**Recommendation:** freeze this version as the next release candidate, then put it in the repository with a release.

The next substantive milestone is **independent review by a human expert** in hyperbolic PDEs and constrained higher-spin field systems, not another cycle of cosmetic revisions.
