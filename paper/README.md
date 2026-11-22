# Paper, version 2

**[main.pdf](main.pdf)**: *A Jordan-block obstruction to L² well-posedness for charged spin-3/2 fields*. 27 pages, version 2, 2026-11-21.

> **Status:** AI-collaborative work, reviewed by AI systems only (Perplexity, ChatGPT). **Not peer reviewed, not reviewed by a human expert, not independently replicated, and not formally verified.** Expert comments and corrections are welcome: please open an issue.

## What is here

| File | What it is |
|---|---|
| [`main.pdf`](main.pdf) | the paper |
| [`main.tex`](main.tex), [`refs.bib`](refs.bib) | LaTeX source and bibliography |
| [`build.sh`](build.sh) | builds `main.pdf` (pdflatex, bibtex, pdflatex ×2), with a fixed build date for reproducibility |
| [`audit/num_audit.py`](audit/num_audit.py) | checks the numbers printed in the paper against the exact witness data (19 assertions, exact arithmetic) |
| [`CHANGES_v2.md`](CHANGES_v2.md), [`DIFF_vs_frozen.txt`](DIFF_vs_frozen.txt) | what changed from the first, unpublished version, and the source diff |
| [`FINAL_RELEASE_REPORT.md`](FINAL_RELEASE_REPORT.md) | the release checks, and who ran each one |
| [`VERSIONS.txt`](VERSIONS.txt) | tool versions and the exact outputs of those checks |

## Check it

From the repository root:

```sh
python3 paper/audit/num_audit.py data/witness.json paper/main.tex   # expect: ALL PASS
sh paper/build.sh                                                      # needs a TeX installation
```

The second command overwrites `main.pdf` with a rebuild. On TeX Live 2023, the rebuild is byte-identical to the posted PDF. Other TeX versions may differ in bytes but not in content. The exact-check scripts behind every computation in the paper are in [`../scripts/`](../scripts/), described in the paper's Appendix A, Table 3. The two review checks named in the release report (`charpoly_pip.py`, `sign_cmp.py`) are in the project archive, not in this repository.

## Fingerprints (SHA-256)

- main.pdf `41522f919bed08719fa9ec16314162ad44c1155d3896dcb3f450a4c69adbe3f3`
- main.tex `517c74709c802f2e94b95baf7378912fc08216c0ac37778e80efbe0007cc45db`
- refs.bib `278218f478a50d203b301685e471a30d319b356132110e466d58894777139985`

They are also listed in the repository's [`SHA256SUMS`](../SHA256SUMS).

## Versions

- **Version 2 (this one)** is the paper's first public version. Version 1 was an internal frozen candidate. It went through the reviews described in [HOW_IT_WAS_CHECKED.md](../HOW_IT_WAS_CHECKED.md) and was not posted.
- The paper's version number is separate from the repository's. Version 2 of the paper was added in repository release **v1.0.9**. The code and data it cites are those of release **v1.0.8**, which are unchanged in v1.0.9.
- Any later correction will be a new paper version with its own change log. Posted versions are not edited.

## Corrections
- **CHANGES_v2.md, "Build" section.** The sentence "That is why a rebuilt PDF had a different hash from the one recorded in that package's manifest" gives an unsupported explanation.
  - The 15:32 package it refers to was an internal, unpublished one, and it was internally consistent: its main.pdf matched its own manifest.
  - The different hash came from an erroneous report in an AI review. Where that hash came from is unknown.
  - The paper, its PDF and every result are unaffected. CHANGES_v2.md is left unchanged as part of the posted version.

## License

The text is under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The scripts are under the [MIT License](../LICENSE).
