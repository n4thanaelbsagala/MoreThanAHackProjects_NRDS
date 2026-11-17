# TASK-005 verification — 2026-11-09

## Identity and scope

- Upstream starter revision: `f8f2629ff1e0985f81d7e59d8413678514ee1530`; local Git HEAD before this uncommitted work: `1d640b1afe47272deaeaeddd5826abf0a2a5ae75`.
- Authorized local inputs in ignored `data/tactical/`: ATD metadata SHA-256 `327e35e32e46a647389b88f883d4f9a2ab931e3e6148aef2fcf8f22b1e93c43a`, raw ATD `f130e350d2bfdf734b7e32f072931fccc6d015c1e837d082064875fe0a700431`, automatic tagging `0594d35e3df01b9c5002372d8615e2e8ef5379ac8f4e84c5ef7a53f4304c9019`.
- Python 3.9.6 in `.venv`; `numpy==2.0.2`, `pandas==2.3.3`, `python-dateutil==3.0.0`, `pytz==2026.6`, `six==1.17.0`, `tzdata==2026.6`; requirements are pinned in `requirements-lock.txt`.
- Config: `model/config.json` SHA-256 `aaa0c55c43a6f241ecceb861b1a24c12a6aa5b15073fe2bad4079b3bd0e5f3fa`. No random seed or stochastic step.
- Code fingerprints: `model/evidence.py` `4dd9bac61519aada525d985402843a0c9c99247100f8f09b4cb5ddbe3ccb237c`; `model/inference.py` `c5eaa4005ed43e09a3b8e159ee01843dd9117a62367253f3efc61ff8a6fce689`; `model/temporal.py` `a40bd241c28c6ed4188dae572191cca77318b1489e658df05cd5fb4ae40b047c`.

## Checks and outputs

| Check | Observed result |
| --- | --- |
| `.venv/bin/python -m unittest discover -s tests -v` | PASS, 26 tests including strict ATD IDs/slot counts, missingness, coordinate scaling, pass/incidental touch/turnover, dead/restart, halftime reset, CSV integration and output-path collision. |
| `.venv/bin/python starter/baseline.py --out evaluation/generated_baseline` | PASS, nearest observed ball 113,488/199,319; four regenerated files previously compared byte-for-byte with the four supplied baseline CSVs. |
| `.venv/bin/python evaluation/run_evaluation.py --results evaluation/generated_baseline --out evaluation/generated_baseline --no-detail` | PASS, four regenerated baseline CSVs only. Public five-minute spellF1: smooth125 0.4242, smooth50 0.3256, smooth25 0.2868, raw 0.0378. Pipeline check only; not used for model selection. |
| `.venv/bin/python evaluation/validate_submission.py evaluation/generated_baseline/baseline_smooth50.csv` | PASS, 199,319 ordered rows. |
| `.venv/bin/python model/run.py --config model/config.json --output evaluation/results/temporal_interface_v1.csv --diagnostics evaluation/reports/temporal_interface_v1_diagnostics.csv` | PASS, tactical team names Barcelona / Atletic Club. |
| Same model command with `temporal_interface_v1_repeat.csv` and matching repeat diagnostics path | PASS, prediction SHA-256 on both runs `fe13eb9a04a544532c757bac2e6df0cc3f63f68c40f48384ca218a0e9b677c78`; diagnostic SHA-256 on both runs `7dbdfaee9d47f43ba45687aac2a5c2bf780fe6e77e80e1130160a3212bf70a8d`. |
| `.venv/bin/python evaluation/validate_submission.py evaluation/results/temporal_interface_v1.csv` | PASS, exactly `frame,label`, 199,319 rows, ordered unique frames 0–199318, legal labels and no blanks. |
| `git diff --check` and independent read-only review | PASS after fixing a same-path output/diagnostics collision. Official `games.py`, `starter/`, and evaluator source have no tracked changes. |

The delivered model CSV has H 78,057; A 69,659; D 10,850; X 40,753. An independent diagnostic scan found 388 label transitions, 324 H/A intervals (median 9.26 s), 13 H/A intervals under one second, 62 D intervals and 113,488 frames with an observed ball. D frames comprise 2,420 sustained out-of-bounds, 902 stationary set-piece, and 7,528 awaiting confirmed restart. These counts check implementation behavior, not prediction accuracy.

The new prediction CSV is byte-identical to the earlier `evaluation/results/temporal_v1.csv`. The work separates and hardens the existing prototype; it does **not** show a new possession rule, a quality improvement, a private full-match score, or organizer acceptance. Public labels were not read by the model or used to choose thresholds. No eligible external labeled game was available, so accuracy remains unvalidated. Homography and an Excel export were unavailable locally and were not used. All generated CSVs and restricted inputs are ignored by Git.

## 2026-11-10 extension: offline stationary-window backfill

This section supersedes only the earlier claim that the new CSV is byte-identical to v1. The
2026-11-09 integration remains reproducible with `model/config.json`; the new variant is
`model/config_v2.json`. The working tree is still uncommitted on HEAD
`1d640b1afe47272deaeaeddd5826abf0a2a5ae75`. Upstream starter revision and the three
authorized tactical input SHA-256 hashes above were checked again and are unchanged.

- Rationale and provenance: after 25 observed, stationary frames within an automatic set-piece
  interval, mark the complete confirmed window as dead evidence. The 25-frame and 0.5 m settings
  are unchanged v1 engineering assumptions. No public labels, private labels, human labels, or
  match-event-specific constants were used to choose the rule. It is an offline timing rule, not
  real-time causal inference or a demonstrated quality improvement.
- Red/green: two synthetic backfill tests first failed on v1 behavior (`[2]` instead of
  `[0,1,2]`, `[4]` instead of `[2,3,4]`); after implementation they passed. A separate invalid
  boolean-configuration test failed first and then passed after validation was added.
- Final `.venv/bin/python -m unittest discover -s tests -v`: PASS, 30 tests, including missing
  observations, short runs, half boundaries, dead/restart, turnovers, output serialization and
  v1 behavior. `.venv/bin/python model/run.py --config model/config.json --output evaluation/results/temporal_v1_unchanged_check.csv --diagnostics evaluation/reports/temporal_v1_unchanged_check_diagnostics.csv`:
  PASS; prediction SHA-256 `fe13eb9a04a544532c757bac2e6df0cc3f63f68c40f48384ca218a0e9b677c78`,
  exactly matching the earlier v1 artifact.
- `.venv/bin/python model/run.py --config model/config_v2.json --output evaluation/results/temporal_v2.csv --diagnostics evaluation/reports/temporal_v2_diagnostics.csv`:
  PASS. The same command with `temporal_v2_repeat.csv` and matching repeat diagnostics also
  passed. Both prediction hashes are
  `dce2ebdb60ecf31967907e7fdb031eafb5533c5642561239cdc285ca149a0c9f`;
  both diagnostic hashes are
  `5c7a30c82b3b474f34f54501e223b36d8640443c664df436236353b25924a360`.
- `.venv/bin/python evaluation/validate_submission.py evaluation/results/temporal_v2.csv`:
  PASS, exactly 199,319 ordered frames `0..199318`, exactly `frame,label`, legal H/A/D/X
  labels, no blanks. Counts: H 77,646; A 69,381; D 11,539; X 40,753.
- A diagnostic comparison with the v1 re-run found exactly 689 changed labels, each changing
  H or A to D on a v2 frame with confirmed stationary set-piece evidence. V2 has 376 label
  transitions and 317 H/A intervals; these are defect checks, not accuracy evidence.
- Configuration SHA-256: v1
  `aaa0c55c43a6f241ecceb861b1a24c12a6aa5b15073fe2bad4079b3bd0e5f3fa`;
  v2 `c2d99e256141d56c168c7ae172e639272aa085f76a7bf336efcfcaaeacc3b36d`.
  Model code SHA-256: `model/evidence.py`
  `1f925ef10505108f3e1c07462316d74c3d9f171200e06d936bd6c5efb63b791d`,
  `model/inference.py` `7397d0b932aeacf0cc2f48175d90f776296766e57212d6d957d96e080d431c02`,
  `model/temporal.py` `e98ceb87e4a1a780a22fa00af161917ecd33765cbc4b88f4cd38c69690d60dfc`.
- Public-window scoring of v2: NOT RUN. Eligible external labeled validation: NOT AVAILABLE.
  Private full-match score: NOT AVAILABLE. No accuracy or spellF1 gain is claimed.
