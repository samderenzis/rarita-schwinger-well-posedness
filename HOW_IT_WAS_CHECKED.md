# How this result was checked

This result was produced by **AI-collaborative research**. The project owner (Sam DeRenzis) defined the programme, set the rules and ran the verification. Three AI systems took separate roles:
- **Claude** (Anthropic): implementer.
- **ChatGPT** (OpenAI): auditor and deriver.
- **Perplexity**: used by the owner, as needed, for literature searches and physics cross-checks, and, for the paper, a manuscript review (see below).

Nothing here has been reviewed by a human expert.

## Rules followed throughout
- Exact arithmetic only (no floating-point "recognition" of numbers) for every algebraic claim.
- Every file is fingerprinted (SHA-256). Frozen records are never edited; corrections are made by superseding versions plus an errata register.
- Failed attempts and errors are kept on record, never deleted.
- A status is never upgraded just because scripts agree.
- No independent-replication or human-verification claims.

## The proof chain and how each link was checked
| Link | Content | Check |
|---|---|---|
| L0 | Algebraic reduction: divergence identity, elimination of ψ₀, constraint intertwining | Exact computation; externally re-executed (6/6 scripts, identical output, 7/7 mutation tests caught) |
| L1 | Transfer between the original and reduced problems | Statement-only **blind derivation** by ChatGPT: proved, frozen hash verified |
| L2 | Energy estimate from the well-posedness package | Blind derivation conditional on one lemma; closed by Claude's lemma; audited by ChatGPT (non-blind) |
| L3 | Local coercivity | **Blind derivation**: proved, frozen hash verified |
| L4 | Necessity lemma (R1) | Blind derivation failed at the oscillatory H⁻¹ estimate (twice, in separate fresh attempts); closed by Claude's lemma; audited PASS by ChatGPT (non-blind) |
| L5 | Application of R1: ball properties, function class | **Blind derivation**: proved |
| L6 | Witness Jordan chain and contradiction | Exact computation, re-executed externally; contradiction re-derived blind |
| All | Interfaces between links | Whole-chain audit (ChatGPT); three presentation defects found and closed; re-audit: all closed |

"Blind" means a fresh AI chat received only the statement, never the existing proof. Its answer was frozen, with a hash, before any comparison.

## Machine validation
The first version of the validation suite (v1.0) was reviewed by ChatGPT. That review reported 26 findings, including 7 defects in the validator: 24 were fixed, one was fixed in part, and one was documented rather than changed. Later versions, up to `bhmap_validate_v1_7.py` in this repository, were developed by Claude and tested against the owner's runs; they have not had a second external review. Three defects found in those runs (in how the literature check reads files) were fixed and are recorded in CHANGELOG.md. The suite's checks include:
- the witness in three different arithmetic engines (SymPy, FLINT, pure-Python fractions);
- representation independence, including dense non-unitary basis changes;
- the operator identities evaluated to 60 digits;
- numerical attacks on the key inequality (the paper's Lemma 4.5; the validator calls it "Lemma 4.1", following an earlier draft);
- geometry;
- every citation;
- mutation tests proving the checks can fail.

Every published owner run gave `COMPLETE_PASS`: v1.7 on the full private archive, v1.7 on this repository, and the earlier v1.4 deep run on the archive. They are listed in the README, with the results in `results/`. The worst ratio found in the attacks on Lemma 4.1 was ≈ 0.50 against a limit of 1.

All of these checks use this project's own code and data. Re-execution by a second AI confirms that the supplied computations run as claimed; it is not independent replication.

## What remains
- Review by a human expert in hyperbolic PDE or higher-spin fields.
- Formal verification. A Lean check of the witness algebra is planned.
- The open research questions: other parameter values, off the Pauli slice, and a local-domain version of the H⁻¹ estimate.

## Review of the paper (2026-11-21)

The paper (written, and not yet posted at the time) was reviewed by Perplexity at the manuscript level: 12 items, two rounds of follow-up, and a final reading of the frozen candidate PDF. Every item was addressed. Of the reviewer's points, one was a misreading that the reviewer withdrew; the others led to clarifications, narrower wording, two notation and dimension corrections, and one new result (the witness is the same for every value of the constraint-addition parameter π′).

In the reviewer's own words: "The frozen candidate PDF was inspected, and the reported manuscript corrections were confirmed in the document. The specific objections raised during this review were addressed. The associated source code, computational certificates, archive integrity, and complete mathematical proof were not independently verified in this review."

It is not independent replication, not execution of the verification suite, not certification of the theorem, and not human expert review. A further review by ChatGPT of the paper, code, data, OUTLOOK and archive together followed; it is described in the next section.

## Full AI review by ChatGPT (2026-11-21)

After the Perplexity rounds, ChatGPT reviewed the frozen paper candidate together with the full project archive (GEN33), in three parts: a partial report, then two batches.

**What it executed** (its own environment: Python 3.13.5, SymPy 1.14.0):
- the archive and manifest checksums;
- the witness programs and the 19-item number audit;
- `check_1` … `check_5`;
- the review check scripts (both signs of λ);
- `outlook_checks.py`.

All of these passed.
- `check_4` completed in a background retry after the first attempt hit its environment's time limit.
- It confirmed that the scripts' matrix M is the negative of the paper's, so the signs cancel and the implemented reduction agrees with the paper's §3.

**What it read and analysed:**
- **The paper's §4 and Appendix B.** It found no invalid inference: the order of limits is correct and the constants of Lemma B.4 are independent of the difference step.
- **The constraint route.** The current route needs only uniqueness among constrained solutions, not subsidiary uniqueness for the constraint equation.
- **The project records behind OUTLOOK.**
- **All 31 references.** Most were checked at abstract or metadata level; two (Ivriĭ–Petkov, Métivier) were checked at full-text level.
- **Consistency across the documents.**

**What it found:**
- No error in the mathematics.
- Documentation inconsistencies, now corrected in v1.0.8:
  - this page's validator-review count;
  - the validator's scope wording;
  - "proof-carrying" for scripts that are exact checks, not formal proofs.
- One premise missing from an internal project record (GEN9 Proposition L5.1). It does not affect the witness.
- Bibliographic metadata to complete in a later paper version (done in paper version 2).

**Its scope, in its own terms:** this is an AI review, not human expert review, certification or independent replication. The checks re-ran the project's own code, data and conventions. Its overall verdict: the result is a specific, model-dependent mathematical theorem with an exact witness. Which property fails, other parameter points, formulation independence, causality and physical interpretation are not established.

## Paper version 2 and its release checks (2026-11-21)

Paper version 2 adds the corrections from the reviews above: wording, two added references, completed bibliographic metadata, and a description of the reviews in Appendix C. No theorem, proof, witness or number changed. Its change log and release report are in [paper/](paper/).

**Claude** ran the release checks:
- the LaTeX/BibTeX build: no errors, 27 pages;
- a reproducible build, in which a rebuild from the packaged source gives an identical PDF;
- the 19-item number audit;
- the citation check, 33 of 33 references cited;
- the exact-check scripts, run from this repository's v1.0.8 files.

All passed.

**ChatGPT** independently checked the release candidate archive: its checksums, the bibliography correction, and the number audit. All passed. It did **not** re-run the LaTeX build, because BibTeX was not available in its environment.

Both are AI systems working from this project's own files. This is not human expert review and not independent replication.

