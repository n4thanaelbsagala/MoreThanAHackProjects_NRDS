# TASK-007 verification — NRDS submission package

Date: 2026-11-16  
Technical document: `docs/NRDS_technical_document.md`  
Submission: ignored local file `evaluation/results/NRDS.csv`

## Verified

- Official upstream HEAD was rechecked and remains
  `f8f2629ff1e0985f81d7e59d8413678514ee1530`.
- Current public NRDS `main` is
  `ce39ad61a4b089b1611cafb7f110279ab2db6b8d`. An archive of that exact tree ran all
  100 tests successfully and regenerated v8 byte-for-byte from the authorised tactical inputs.
- Strict ATD alignment passed: 199,319 contiguous records, raw IDs 1–199319 mapping to video
  frames 0–199318.
- The official validator accepted the regenerated and delivered `NRDS.csv`: exactly 199,319
  ordered rows, `frame,label`, frames 0–199318, labels H/A/D/X.
- Delivered and regenerated CSVs matched SHA-256
  `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`.
- A claim audit checked the document against `model/config_v8.json`,
  `model/dataset_manifest_v8.json`, `docs/verification/TASK-015-development.json`, and the exact
  CSV. Required submission topics were present. `git diff --check` passed.
- The document contains no local absolute path, token, password, credential, Drive link, private
  key, raw tracking row, or frame-specific match correction. Git tracks only `data/README.md` and
  the four official baseline CSVs from the protected data/results areas; official evaluation,
  starter, and `games.py` files have no local diff.

## Commands

```bash
.venv/bin/python -c 'from starter.load_atd import check_alignment_raw; print(check_alignment_raw())'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python model/run.py --config model/config_v8.json \
  --output /private/tmp/NRDS_document_verify.csv \
  --diagnostics /private/tmp/NRDS_document_verify_diagnostics.csv
.venv/bin/python evaluation/validate_submission.py /private/tmp/NRDS_document_verify.csv
cmp -s evaluation/results/NRDS.csv /private/tmp/NRDS_document_verify.csv
shasum -a 256 evaluation/results/NRDS.csv /private/tmp/NRDS_document_verify.csv
```

The public revision was separately extracted to a temporary directory, tested, regenerated with
`config_v8.json`, validated, compared, and produced the same hash.

## Unresolved and deliberately unclaimed

- The exact human/automatic annotation process behind IDSSE and WCSF provider reference fields
  is not established; the document identifies them as provider references, not ground truth.
- No untouched compatible final-test match remains, so independent v8 accuracy is unverified.
- No public-window v8 metric or private BAR–ATH score is reported.
- The owner later committed and pushed the document in `8dfadb1`; the cleanup followed in
  `2c6f9f1`. This record preserves the earlier verification snapshot. No Google Form submission
  has been made, and the submission URL is only available to the team by email.
