# How this result was checked

This result was produced by **AI-collaborative research**. The project owner (Sam DeRenzis) defined the programme, set the rules and ran the verification. Three AI systems took separate roles:
- **Claude** (Anthropic): implementer.
- **ChatGPT** (OpenAI): auditor and deriver.
- **Perplexity**: used by the owner, as needed, for literature searches and independent physics cross-checks.

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
| L4 | Necessity lemma (R1) | Blind derivation failed at the oscillatory H⁻¹ estimate (twice, in independent attempts); closed by Claude's lemma; audited PASS by ChatGPT (non-blind) |
| L5 | Application of R1: ball properties, function class | **Blind derivation**: proved |
| L6 | Witness Jordan chain and contradiction | Exact computation, re-executed externally; contradiction re-derived blind |
| All | Interfaces between links | Whole-chain audit (ChatGPT); three presentation defects found and closed; re-audit: all closed |

"Blind" means a fresh AI chat received only the statement, never the existing proof. Its answer was frozen, with a hash, before any comparison.

## Machine validation
The validation suite in this repository (`bhmap_validate_v1_7.py`) was itself reviewed by ChatGPT. That review found 26 issues, including 7 defects in the validator, and all were fixed. The suite's checks include:
- the witness in three independent arithmetic engines;
- representation independence, including dense non-unitary basis changes;
- the operator identities evaluated to 60 digits;
- numerical attacks on the key inequality (Lemma 4.1);
- geometry;
- every citation;
- mutation tests proving the checks can fail.

The owner's deep run gave `COMPLETE_PASS`. The worst ratio found in the attacks on Lemma 4.1 was ≈ 0.50 against a limit of 1.

## What remains
- Review by a human expert in hyperbolic PDE or higher-spin fields.
- Formal verification. A Lean check of the witness algebra is planned.
- The open research questions: other parameter values, off the Pauli slice, and a local-domain version of the H⁻¹ estimate.
