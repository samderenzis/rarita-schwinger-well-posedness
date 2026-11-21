# Paper version 2 (release candidate): change log (2026-11-21)

This version supersedes the frozen candidate `paper_candidate_FROZEN_2026-11-21_1022`. Its frozen main.pdf (SHA-256 b6df56ff0ed725478d75a60f48dabcff966c677726683bfff40be90eae9f1873) is preserved unchanged.

**Source of the changes:**
- the ChatGPT full AI review (GEN34);
- ChatGPT's targeted reviews of the v2 builds (15:32 and 15:37);
- the owner's decision.

Each bibliographic change was confirmed from Crossref, the publisher or the article itself before it was applied.

## Text

| Change | Where | Source |
|---|---|---|
| "proof-carrying scripts" → "exact-check scripts" | data statement; Table 3 caption | ChatGPT 16.2 |
| The necessity lemma's hypotheses are stated as verified for this background | abstract | ChatGPT 12.4 |
| "a single constraint that the reduced operator maps into itself" → "a single constraint whose constrained subspace is preserved by the reduced operator" | abstract | ChatGPT targeted review, item 4 |
| "All computations are exact and public." → "The algebraic witness computations use exact arithmetic, and the scripts and data are publicly available." The validation section also describes numerical stress tests | abstract | ChatGPT targeted review, item 5 |
| New citation: Johnson & Sudarshan (1961) | §1 history | — |
| New citation: Mason & Nicolas (1999), with a short comparison (massless, vacuum; neither implies nor contradicts) | §1.4 | — |
| Repository release v1.0.8; version DOIs; pointer to BACKGROUND/ROADMAP/OUTLOOK (not part of the proof) | data statement | — |
| Perplexity's manuscript and documentation review; ChatGPT's full review | acknowledgements | — |
| New paragraphs "Reviews of this paper" and "Version note" | Appendix C | — |
| "Version 2, November 2026"; unused drafting macro removed | preamble | — |

## Bibliography

| Entry | Change | Confirmed by |
|---|---|---|
| Johnson & Sudarshan 1961 | new: Ann. Phys. 13(1) 126–145, doi:10.1016/0003-4916(61)90030-6 | Crossref |
| Mason & Nicolas 1999 | new: Proc. London Math. Soc. 79(3) 694–720, doi:10.1112/s0024611599012125 | Crossref |
| Strang 1967 | issue 3, pages 397–417; journal given by its 1967 name, *Journal of Mathematics of Kyoto University* (was the current name, *Kyoto Journal of Mathematics*) | Crossref (issue); the article's first page on Project Euclid, "J. Math. Kyoto Univ. 6-3 (1967) 397-417" (pages and journal name); MaRDI/zbMATH record ("Journal of Mathematics of Kyoto University") |
| Colombini–Nishitani–Rauch 2019 | volume 19, issue 1 (pages 217–251 already present) | the publisher's article page |
| Kreiss–Ortiz 2002 | book *The Conformal Structure of Space-Times: Geometry, Analysis, Numerics*, eds. J. Frauendiener and H. Friedrich, Lecture Notes in Physics 604, pp. 359–370 | Springer's book page; Crossref (editors, pages) |
| Benzoni-Gavage–Serre 2006 | subtitle "first-order systems and applications" | Crossref |

## Build
- `build.sh` sets SOURCE_DATE_EPOCH = 1795219200 (2026-11-21 00:00 UTC) and FORCE_SOURCE_DATE = 1.
- main.tex sets `\pdftrailerid{}`.
- The same source therefore gives a byte-identical PDF on the same TeX installation. Two consecutive builds gave identical hashes.
- Builds of the first v2 package (15:32) were not reproducible: every rebuild embedded a new date and ID. That is why a rebuilt PDF had a different hash from the one recorded in that package's manifest. The 15:32 package itself verified correctly against its own manifest.

## Repository release v1.0.8 (verified 2026-11-21 before this version)
- Published, with tag v1.0.8 at commit 554eedb0.
- Its 30 files equal the local snapshot (git blob hashes).
- BACKGROUND.md, ROADMAP.md and OUTLOOK.md are present.
- The agreed documentation corrections are applied:
  - OUTLOOK A5 premise;
  - the HOW_IT_WAS_CHECKED count;
  - the validator-scope wording;
  - "exact-check scripts".

The release contains the code and data this paper uses. The paper itself is not yet in the repository.

## Unchanged
Every theorem, proof, computation, number and table entry. The diff against the frozen main.tex touches 35 lines (the 15:37 → release-candidate step changed refs.bib only, one line: the Strang journal name; the second issue of the release candidate changed FINAL_RELEASE_REPORT.md only), all in the places listed above; the full diff is in DIFF_vs_frozen.txt.

## Checks
See VERSIONS.txt for tool versions and the exact outputs:
- build: 27 pages, 0 errors, 0 BibTeX warnings, 0 overfull boxes;
- `audit/num_audit.py`: 19/19 PASS;
- references: 33/33 cited, none missing;
- the final manifest and zip are checked with `sha256sum -c` and `unzip -t`.

**Status:** AI-checked only; not human or formally verified; not independently replicated.
