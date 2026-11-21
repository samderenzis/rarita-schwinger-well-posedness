# Running the validator

`bhmap_validate_v1_7.py` re-checks the computational claims covered by the selected mode, checks this repository's files, and (optionally) checks that every cited reference's identifier resolves online. In this public repository some archive checks (A2, A3, A5) are not applicable, because they concern the project's private archive; the full archive run covers them. This page explains how to run it, what the options do, and how to read the result.

## 1. Set up (once)

You need Python 3.10 or newer. Then install the packages:

```bash
pip install sympy numpy scipy mpmath python-flint requests
```

On Windows, use `py` in place of `python` in every command on this page (for example `py -m pip install …`).

## 2. Run it

Open a terminal **in the repository folder** (the one that contains `data/`, `scripts/` and `results/`), then run:

```bash
python bhmap_validate_v1_7.py --level standard --online
```

The second line of the output should read `repository mode (auto-detected)`. If it says `mode=none` instead, you are in the wrong folder: most checks will be skipped and the run cannot reach `COMPLETE_PASS`.

A progress line is printed every minute. Each check prints one line when it finishes.

## 3. Choose a level and options

| Option | What it does | When to use it |
|---|---|---|
| `--level quick` | Fewer random trials. A smoke test. | First run, or a slow computer |
| `--level standard` | The normal run. About 3 minutes on a 12-core desktop; longer on smaller machines. | Most people |
| `--level deep` | Many more random trials and larger stress tests. Considerably longer. | A more thorough re-check |
| `--online` | Also checks every cited DOI (Crossref, doi.org) and arXiv identifier (arXiv API). Needs internet. | Include it for a complete run: without it, G1 and G2 are skipped |
| `--mailto you@example.com` | Identifies you to Crossref, which makes its lookups faster and more reliable. | Optional, with `--online` |
| `--workers N` | Number of checks run in parallel (default: the smaller of 8 and your CPU count). | Lower it if memory runs short, especially with `--level deep` (try 4) |
| `--only D1,E1` | Runs only the listed checks. The verdict is then at most `PARTIAL_PASS`. | Re-checking one item |
| `--resume` | After an interruption or timeout, reuses the finished checks from the last run with identical settings and runs the rest. | Continuing a stopped run |
| `--seed S` | Seed for the random tests (default 20261120). Every random test records its seed. | Trying different random trials |
| `--out DIR` | Output folder (default `bhmap_validation_out`). | Keeping several runs apart |
| `--budget SEC`, `--check-timeout SEC`, `--online-cap SEC`, `--heartbeat SEC` | Overall time budget, per-check time limit, time cap inside each online check, and progress-line interval. The defaults are generous. | Rarely needed |
| `--repo DIR` | Points at the repository folder explicitly. | Only if you run the script from somewhere else |
| `--pack ZIP` | Checks the project's private working archive instead of this repository. | The project owner only; the archive is not public |

`python bhmap_validate_v1_7.py --help` lists the same options.

Press **Ctrl+C** to stop a run at any point. A partial report is still written, and `--resume` continues it.

## 4. Read the result

The run ends with a line such as:

```
VERDICT: COMPLETE_PASS   counts={'PASS': 32, 'NA': 3, 'INFO': 1}
```

| Verdict | Meaning |
|---|---|
| `COMPLETE_PASS` | Every one of the 36 checks ran, and each is PASS, INFO or NA. |
| `PARTIAL_PASS` | Nothing failed, but some checks were skipped (for example, no `--online`) or not selected (`--only`). They are listed. |
| `FAIL` | At least one check failed. |
| `ERROR` | A check crashed, timed out or could not finish. Re-run with `--resume` to retry only those checks. |

| Status of one check | Meaning |
|---|---|
| `PASS` | The stated property held under the stated method. |
| `INFO` | Reports a fact without a pass/fail threshold (for example B5: behaviour under the other Clifford representation). |
| `NA` | Not applicable here. A2, A3 and A5 check the private working archive, which is not in this repository. They are never counted as passes. |
| `SKIP` | Not run, with the reason given (missing package, or no `--online`). |

What a PASS establishes depends on the kind of check. An **exact** check proves the finite identity it tests. A **numerical** check is an attempt to find a counterexample: PASS means none was found, which is not a proof. A **toy-model** check (group F) illustrates the logic of the argument only.

## 5. The output files

Two files are written to `bhmap_validation_out/`:

- `bhmap_validation_results.json`: everything, including your environment, every check, every sub-measurement and the seeds used.
- `bhmap_validation_results.csv`: one row per check.

The same folder also holds a checkpoint (for `--resume`), the online lookup caches and a timing history. The validator never reads any of these as citations.

## 6. Compare with the published runs

The published runs are in [`results/`](results/). Compare the **verdict and the status of each check**, not the file hash: the JSON records your machine, your package versions and the time of the run, so its hash will differ from ours even when every result agrees. With the default seed, the random tests draw the same inputs as the published runs; results from numerical optimisation may differ slightly between machines.

If your result differs from ours, please open an issue on GitHub and attach your JSON file.
