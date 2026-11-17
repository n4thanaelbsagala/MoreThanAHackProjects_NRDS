# TASK-016 verification — final repository organization

Date: 2026-11-16  
Initial verification base: `8dfadb199da75b3502e68a001951811be30a37fa`
Owner's subsequent cleanup commit: `2c6f9f17bf0a5f39493a583fa1e68a4790f1d891`
Final model: `model/config_v8.json` (SHA-256 `61ab5e79210abfd7ba07c24d785890bdeb7f507f43d0c2e0f41d96f7926f6238`)

## Organization and scope review

- The root README now identifies the three mandatory organizer deliverables separately from the
  repository's suggested directory layout.
- `model/README.md` distinguishes the final v8 inference path from retained research history;
  `docs/README.md` indexes submission and verification records.
- The final local artifacts are `evaluation/results/NRDS.csv` and
  `evaluation/reports/NRDS_diagnostics.csv`. Generated prediction/diagnostic files remain ignored.
- Official `starter/`, `games.py`, and evaluator source were not edited. The only tracked file
  under `evaluation/` changed by TASK-016 is the explanatory `evaluation/results/README.md`.
- Unique historical configurations, aggregate reports, outputs, and the recoverable
  `.git.outer-backup-20261111/` were retained. No source directories were moved.

## Removed local generated duplicates

Before removal, SHA-256 comparisons established that `temporal_v8.csv` and
`temporal_v8_repeat.csv` were byte-identical to `NRDS.csv`; repeat v1/v2/v7 artifacts were also
identical to their retained originals. The duplicate v8 diagnostics matched the retained final
diagnostics. Regenerated baseline CSVs matched the four tracked official baseline files.

Only those byte-identical repeats, recreatable generated scoreboards/baseline copies, and
`.DS_Store` were removed. These files were ignored and untracked. They are recoverable from the
documented generation, baseline, and evaluation commands; no unique work was deleted.

## Executed checks

1. `.venv/bin/python -m unittest discover -s tests -v`
   - PASS: 100 tests.
2. `.venv/bin/python -c 'from starter.load_atd import check_alignment_raw; print(check_alignment_raw())'`
   - PASS: 199,319 records and video frames; ATD IDs 1–199,319; zero-based first video frame 0;
     contiguous and aligned.
3. Fresh v8 generation to a temporary directory using the command in the root README.
   - PASS: output and diagnostics both matched the retained final files byte-for-byte.
   - Prediction SHA-256: `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`.
   - Diagnostics SHA-256: `34d0a7c44f0f070126edd174711e46083841b54b505570f0b303035959da1dd9`.
4. `.venv/bin/python evaluation/validate_submission.py evaluation/results/NRDS.csv`
   - PASS: exactly 199,319 rows, frames 0–199318, labels H/A/D/X only.
   - Distribution: H 75,339; A 70,868; D 12,460; X 40,652.
5. Isolated official public baseline scorer using a temporary results directory.
   - PASS: `baseline_smooth125` spellF1 0.4242, `baseline_smooth50` 0.3256,
     `baseline_smooth25` 0.2868, and `baseline_raw` 0.0378.
   - These are public-window pipeline checks, not model-selection or private-match results.
6. `git diff --check`
   - PASS.
7. Tracked-file and full-history high-confidence secret/restricted-asset scans.
   - PASS: no credential/private-key pattern, tactical/external raw asset, NRDS/temporal prediction,
     report directory, or generated-baseline path was found in tracked history.
   - `git check-ignore -v` confirmed tactical inputs, final output, diagnostics, and `.venv` are
     excluded. The local Git backup was excluded by `.git/info/exclude`; the follow-up adds a
     portable `.gitignore` rule.

## Remaining limitations

- `NRDS.csv` is intentionally not part of the public Git tree and must be uploaded separately.
- The local Git backup and unique historical ignored outputs remain for recovery/audit; deleting
  them would require a separate decision because they are not all demonstrably redundant.
- No untouched compatible external final-test match exists. The documented v8 figures are
  development/provider-reference metrics, not independent accuracy or a private BAR–ATH score.
- The original cleanup was not committed or pushed during its verification. The owner subsequently
  committed and pushed the changes as `2c6f9f1`. The present documentation follow-up is local;
  no organizer form submission has been made.

## Follow-up review after the owner's commit

On 2026-11-16, starting from clean `main` at `2c6f9f1`, the follow-up corrected the historical
commit status, clarified that `code_base_revision` predates v8, recorded the v8 candidate commit,
and added a portable ignore rule for the local Git backup. The technical document now checks out
the public cleanup commit. No inference logic or configuration threshold changed.

- `.venv/bin/python -m unittest discover -s tests -q`: PASS, 100 tests.
- The documented v8 generation to a temporary directory: PASS, prediction and diagnostics both
  matched the retained final files byte for byte; prediction SHA-256 remained
  `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`.
- `.venv/bin/python evaluation/validate_submission.py evaluation/results/NRDS.csv`: PASS,
  199,319 ordered frames and H/A/D/X labels.
- `git check-ignore -v`: confirmed `.git.outer-backup-20261111/` now matches the tracked
  `.gitignore` rule, alongside ignored match assets and final predictions.
