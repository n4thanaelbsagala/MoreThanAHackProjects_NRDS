# Task board — 2026-11-12

### TASK-015 — Improve dead-ball generalization with grouped development evaluation
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-014
- Goal: Improve dead-ball evidence and possession-spell quality without tuning on WCSF or the challenge public labels, then freeze a reproducible candidate using match-grouped development evidence.
- Scope: explicit dataset manifest; seven-match IDSSE grouped cross-validation; failure diagnostics; bounded dead-evidence/temporal ablations; synthetic regression tests; frozen configuration, tactical output and verification record. Preserve v7 and official evaluation code.
- Acceptance criteria: every collected match has an explicit role; no frame-level leakage; WCSF/public references are not opened by the experiment; baseline and candidates use the unchanged official spell metric; controlling-team regression tolerance is predeclared; targeted missingness/freeze/stoppage/restart tests pass; selected output validates and repeats byte for byte; lack of an untouched final test is reported rather than concealed.
- Verification: manifest/protocol validation; grouped-fold tests; full unit suite; reproducible development report; official CSV validator; repeated tactical generation and hashes; diff/leakage review.
- Evidence: `model/dataset_manifest_v8.json` and `model/v8_protocol.json` were frozen before the bounded 12-candidate experiment. V7 reproduced on 1,002,644 IDSSE development frames at 84.11% H/A/D agreement, 0.4432 official spellF1 and 85.94% D recall. Whole-match out-of-fold selection produced 88.77% agreement and 0.4841 spellF1. Frozen `observed75` v8 produced 88.55% development agreement, 0.4785 spellF1, 96.82% D recall and 88.54% conditional live-team agreement; these are provider-reference development results, not independent accuracy. All 93 tests passed. The exact 199,319-row tactical CSV passed the official validator; two predictions matched SHA-256 `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`, diagnostics also matched, and a v7 regression retained its earlier hash. Full evidence: `docs/verification/TASK-015.md`; aggregates: `docs/verification/TASK-015-development.json`; frozen record: `model/v8_frozen.json`.
- Blocker: none for implementation and development evaluation. No untouched compatible final-test match is available, so 85% independent accuracy remains unverified.
- Last updated: 2026-11-12
- Handoff: obtain several compatible, legally usable labelled matches whose labels have never been inspected; freeze the final-test protocol before opening them. Restart release delay is the highest-value model issue, but do not tune it against WCSF, BAR–ATH public labels, or the now-inspected IDSSE matches.

### TASK-014 — Freeze, refine and independently assess the temporal model
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-013
- Goal: Execute the four-stage completion plan: reserve a fresh external test, improve live/dead and possession coherence on development data, run one frozen external test, and choose the challenge candidate by the official ranking metric.
- Scope: a pinned WCSF test protocol; development-only model refinement; a separate WCSF adapter and synthetic tests; official spell metrics on external references; final model choice and reproducibility evidence. Official baseline/evaluator files remain unchanged.
- Acceptance criteria: the WCSF match and source revision are recorded before download/scoring; all parameter selection uses only the five pre-existing IDSSE development matches; the candidate is frozen before WCSF references are inspected; WCSF is scored once with the official metrics implementation; selection prioritizes `spell_f1_mean`, then macro-F1; the chosen tactical CSV validates and repeats byte for byte.
- Verification: protocol review and fingerprint; red/green synthetic adapter and selection tests; complete unit suite; official metric output; official tactical CSV validator; repeated generation/hash; diff and leakage review.
- Evidence: Stage 1 reservation saved in `model/wcsf_protocol.json` before data download or scoring. Public source HEAD was `1c9ba798f98a9fffb16081a5d3965774d4e5662c` when reserved on 2026-11-12; sealed archive hashes are `e7e5d753...` and `8653a296...`. Stage 2 searched 75 settings on only the five declared IDSSE development matches and froze `model/config_v7_stoppage.json` at SHA-256 `c28b2df9...` before archive inspection. Development metrics: spellF1 0.43125, macro-F1 0.82925, H/A/D agreement 84.07%, dead recall 87.04%, live-team agreement 81.51%. On the one fresh 57,374-frame WCSF match, v7 led the predeclared comparison with spellF1 0.47698 and 76.47% H/A/D agreement; this is provider agreement, not challenge accuracy. All 81 tests passed. The selected 199,319-row tactical CSV passed the official validator and two generations matched SHA-256 `5637746f...`; diagnostics also matched. `git diff --check` passed, official baseline/evaluator files are unchanged, and upstream HEAD remains the pinned `f8f2629...`. Full record: `docs/verification/TASK-014.md`.
- Blocker: none for stages 1–4. The WCSF source contains one anonymized professional match, so evidence is limited and the earlier 10–50-match/90% aspirations remain unmet.
- Last updated: 2026-11-12
- Handoff: use v7 as the current challenge candidate. TASK-007 remains: prepare the team-named submission and technical document once the registered team name is supplied; do not claim an official/private score.

### TASK-013 — Detect observed unattended stoppages
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-012
- Goal: Stop emitting a controlling team during sustained stationary, unattended ball periods and require renewed control at restart.
- Scope: separate stoppage evidence, optional inference cue, versioned configuration, synthetic tests, external development diagnostic, tactical artifact and verification record.
- Acceptance criteria: no D from missing ball or short pauses; sustained cue backfills within a half; no state or backfill crosses halftime; a restart requires confirmed control; full output validates and repeats byte for byte.
- Verification: full unit suite, official CSV validator, repeat hash, aggregate diagnostics and diff review.
- Evidence: 70 synthetic/existing tests passed; tactical CSV passed official format validator and two runs matched SHA-256 `a6857d51e8a46628c154a9d0bbfa0ebb1ecb7ed4827f4794686cecb5c9588980`. V4 regression output retained SHA-256 `9b14309313b4d5e163d8513b06c1c87afcfbb489b3259f3f7f647d5a4955a655`. Five IDSSE development matches showed 80.92% full H/A/D provider agreement versus 63.72% v4, with lower live-team agreement and more transitions; exploratory only. A later descriptive run over all seven yielded 808,788/1,002,644 = 80.67%; the other two matches were previously inspected, so this is not a fresh holdout. Diff and leakage review passed. Details: `docs/verification/TASK-013.md`.
- Blocker: none.
- Last updated: 2026-11-11
- Handoff: assess this fixed rule on new independent matches and spell metrics before claiming a challenge improvement; the earlier IDSSE holdouts cannot serve as fresh tests.

The upstream public starter is pinned at `f8f2629ff1e0985f81d7e59d8413678514ee1530`.
Statuses describe completed work in this checkout; no private-match score or organizer submission exists.
The project Git root is now `/Users/nathanaelsagala/MoreThanAHackProjects_NRDS`;
the former nested folder was moved here on 2026-11-11 (TASK-011).

### TASK-012 — Research new possession data and retry external tuning
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-010
- Goal: Audit ten additional public resources and run a reproducible new-data tuning experiment, targeting >95% without claiming an unmeasured result.
- Scope: external dataset adapter, synthetic tests, frozen match split/grid, candidate configuration, aggregate results and a Markdown methods/calculation report.
- Acceptance criteria: ten cited resources with availability and compatibility; actual tuning on eligible new inputs; whole-match holdout untouched until selection; report all eligible reference frames including errors/abstentions, baseline and candidate, per-match results, limitations and reproduction evidence.
- Verification: full unit suite, deterministic report regeneration, official validation and repeat hash if a new tactical CSV is generated; diff review.
- Evidence: ten resources assessed; seven IDSSE matches (1,002,644 frames) used with fixed five/two match split and 128-setting grid. Candidate holdout accuracy 185,314/289,155 = 64.09% versus v4 63.75%; live-team agreement 88.08%. The >95% target was not achieved. All 64 tests passed; candidate tactical CSV passed official validation with repeat SHA-256 c896d3548af7f608491626a5c3815f91ad8b219c3c543bbb33aafef12763a999. Full search counts/config repeated; holdout report repeated byte for byte. Final-code fingerprints verified. Results, sources, commands and limitations: `docs/verification/TASK-012.md`, `docs/POSSESSION_DATA_RESEARCH.md`.
- Blocker: none for this experiment. General accuracy and challenge ranking improvement remain unverified; live/dead detection and independent validation limit further claims.
- Last updated: 2026-11-11
- Handoff: retain v5 as experimental (more fragmentation, one test match worsened). Develop live/dead evidence with a fresh reserved external source; do not retune against now-inspected IDSSE or prior SkillCorner holdouts. No commit/push made.

## Coordinated work (2026-11-09)

The lead established `docs/INTERFACE.md` before delegating. On 2026-11-09, the data agent owned
`model/evidence.py`, `tests/test_evidence.py`, and data-audit notes (TASK-008).
The model agent owned `model/inference.py` and `tests/test_inference.py` (TASK-009).
The lead handled integration, and a read-only review agent inspected the result. The
2026-11-10 TASK-005 extension is lead-owned. Official starter/evaluator files are unchanged.
Public-window scores were never used for selection.

Current local output: `evaluation/results/temporal_v2.csv` (ignored by Git), SHA-256
`dce2ebdb60ecf31967907e7fdb031eafb5533c5642561239cdc285ca149a0c9f`.
The experimental external-tuned v4 output is `evaluation/results/temporal_v4.csv`
(ignored), SHA-256 `9b14309313b4d5e163d8513b06c1c87afcfbb489b3259f3f7f647d5a4955a655`.
The v1 output remains byte-identical to its 2026-11-09 artifact. V2 changes only
confirmed stationary set-piece timing and has no established accuracy gain.
The tactical ATD and tagging inputs are present only under ignored `data/tactical/` in this
workspace; a fresh clone needs the authorized bundle. Nineteen public SkillCorner matches and
seven IDSSE matches are available under ignored `data/external/` for provider-reference checks, but
independent human-labeled external data, a registered team name, and a final technical document
are not available. No performance improvement over the official baseline has been established.

### TASK-001 — Establish official scorer and isolated environment
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: none
- Goal: Execute the supplied public baseline scorer without gated data.
- Scope: official starter snapshot, dependency lock, local setup instructions.
- Acceptance criteria: isolated install; official scorer executes four supplied CSVs; one CSV validates.
- Verification: `docs/verification/TASK-001.md`.
- Evidence: public scorer and validator passed on 2026-11-08.
- Blocker: none
- Last updated: 2026-11-08
- Handoff: repeat after any upstream update; do not use public scores for selection.

### TASK-002 — Audit actual tracking and regenerate baseline
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-001; authorized tactical ATD bundle
- Goal: Verify input alignment and regenerate the official baseline from match data.
- Scope: metadata/raw schema, frame counts, missingness, Excel comparison if supplied, baseline CSV.
- Acceptance criteria: verified 1..199319 ATD IDs, correct H/A metadata, four regenerated files validated and fingerprinted.
- Verification: `starter.load_atd.check_alignment_raw()`, `starter/baseline.py`, official validator, input/output hashes.
- Evidence: `docs/verification/TASK-002.md` records input hashes, alignment, four matching baseline hashes and validation; audit in `docs/DATA_AUDIT.md`.
- Blocker: none for ATD baseline; no Excel file to compare.
- Last updated: 2026-11-08
- Handoff: retain input fingerprints and do not commit restricted source assets.

### TASK-003 — Implement and synthetically verify temporal prototype
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-001
- Goal: Explainable temporal possession labels with strict frame ingestion and no public-label tuning.
- Scope: `model/`, `tests/`, configuration and behavior documentation.
- Acceptance criteria: synthetic boundary, missingness, pass, incidental touch, turnover, dead/restart, halftime and serialization tests pass.
- Verification: `docs/verification/TASK-003.md`.
- Evidence: six synthetic unit tests pass after tactical set-piece evidence was added.
- Blocker: none for prototype; actual-match behavior remains unverified.
- Last updated: 2026-11-08
- Handoff: consider external-match validation before claiming any improvement in scoring.

### TASK-004 — Validate and reproduce full-length prototype output
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-002, TASK-003
- Goal: Generate the exact 199,319-row prototype CSV twice with matching hashes.
- Scope: input fingerprints, official validator, label and transition diagnostics, reproduction record.
- Acceptance criteria: exact CSV contract passes validator; identical runs hash alike; diagnostics inspected.
- Verification: commands in README and `docs/verification/TASK-004.md`.
- Evidence: `docs/verification/TASK-004.md` records official validator result, diagnostics, and matching repeat hashes.
- Blocker: none for generation; model quality remains unvalidated against eligible external labels.
- Last updated: 2026-11-08
- Handoff: evaluate dead-ball detection and turnovers on eligible external games; do not tune to the public five minutes.

### TASK-005 — Harden and extend temporal possession inference
- Status: done
- Priority: P1
- Owner: lead (integration)
- Depends on: TASK-004, TASK-008, TASK-009
- Goal: Keep the verified separated pipeline and add a general offline timing rule that starts a confirmed stationary set-piece dead interval at the beginning of its observed window.
- Scope: `model/evidence.py`, model docstrings, `model/temporal.py`, versioned configuration, synthetic tests, model rationale and diagnostics; preserve the v1 files and official starter/evaluator.
- Acceptance criteria: a short or interrupted stationary/tagged run remains insufficient; a sustained observed run can backfill only within the same half; existing v1 predictions remain reproducible; new full-length output validates and repeats with an identical hash; diff review finds no unresolved correctness issue.
- Verification: `.venv/bin/python -m unittest discover -s tests -v`; `.venv/bin/python evaluation/validate_submission.py evaluation/results/temporal_v2.csv`; repeat v2 generation and compare SHA-256; inspect aggregate diagnostics and diff. Full record: `docs/verification/TASK-005.md`.
- Evidence: PASS, 30 tests and official validation of 199,319 ordered H/A/D/X rows. Two v2 runs matched SHA-256 `dce2ebdb60ecf31967907e7fdb031eafb5533c5642561239cdc285ca149a0c9f`; the v1 re-run matched its prior hash. Exactly 689 labels changed to `D` under confirmed stationary set-piece evidence. No public-window or private-match score was used to select v2. The diff was reviewed.
- Artifact: ignored `evaluation/results/temporal_v2.csv`; separate diagnostics at `evaluation/reports/temporal_v2_diagnostics.csv`; configuration `model/config_v2.json`.
- Blocker: none for TASK-005 completion. Accuracy claims remain unverified without eligible external labeled data (TASK-006).
- Last updated: 2026-11-10
- Handoff: TASK-006 is next: obtain an eligible labeled match from another game, document its provenance, then assess possession and dead-ball timing. Do not infer an accuracy gain from the 689 changed frames or transition counts.

### TASK-008 — Extract and audit tactical frame evidence
- Status: done
- Priority: P1
- Owner: data agent
- Depends on: TASK-004; `docs/INTERFACE.md`
- Goal: Return strict, documented per-frame tracking and tagging evidence for inference.
- Scope: `model/evidence.py`, `tests/test_evidence.py`, data-audit notes only.
- Acceptance criteria: exact tactical frame count and 1→0 indexing; metadata-based H/A slot mapping; normalized-to-metre distance scaling; explicit missingness; set-piece evidence requires observed stationary ball; malformed input fails loudly.
- Verification: red/green synthetic tests, full Python test suite, official raw alignment check, aggregate input audit; report commands/results to lead.
- Evidence: six focused tests and the 26-test suite passed on 2026-11-09; real tactical scan returned 199,319 ordered records, correct team names, and 113,488 observed balls. Audit and input hashes are in `docs/DATA_AUDIT.md`; the later 30-test TASK-005 check is in `docs/verification/TASK-005.md`.
- Blocker: none; authorized tactical ATD/tagging files are local and ignored.
- Last updated: 2026-11-09
- Handoff: interface integrated in `model/temporal.py`; homography and Excel remain unavailable locally.

### TASK-009 — Extract and harden temporal inference
- Status: done
- Priority: P1
- Owner: model agent
- Depends on: TASK-004; `docs/INTERFACE.md`
- Goal: Convert agreed evidence records into coherent H/A/D/X labels with reason codes.
- Scope: `model/inference.py`, `tests/test_inference.py` only.
- Acceptance criteria: same-team passes retain control; incidental opposing touches do not switch it; sustained opposing control does; missing ball is not dead; dead/restart and halftime state reset work; invalid block boundaries fail loudly.
- Verification: red/green synthetic tests and full Python test suite; report commands/results to lead.
- Evidence: 12 focused tests and the 26-test suite passed on 2026-11-09, including malformed boundaries/candidates, missingness, turnover and restart behavior; the later 30-test TASK-005 check is in `docs/verification/TASK-005.md`.
- Blocker: none; synthetic evidence follows the interface.
- Last updated: 2026-11-09
- Handoff: interface integrated in `model/temporal.py`; no performance claim until eligible external validation.

### TASK-006 — Compare fixed model on public external matches
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-005; public SkillCorner open data
- Goal: Compare the fixed temporal model with provider possession fields across 10 external matches, without tuning on the challenge public window.
- Scope: external-data provenance, separate 10 fps adapter, provider-label agreement and coverage, reproducible aggregate comparison; keep official challenge code and output unchanged.
- Acceptance criteria: process 10 closed matches with date and H/A mapping; document source, revision, license, label provenance and definition limits; synthetic adapter tests and full suite pass; record per-match results and fingerprints. Do not call automatic provider fields verified ground truth or select a new configuration from them.
- Verification: `docs/verification/TASK-006.md` records source identity, code/configuration and input hashes, commands, aggregate results, full-suite result and repeat hash.
- Evidence: 10 closed SkillCorner matches, 648,120 frames, processed with the fixed v2 model. Agreement with provider H/A fields was 250,979 / 314,964 (79.7%); agreement on provider live-phase frames was 263,178 / 309,236 (85.1%). Initial repeat hash was `70d119164aeab6e1a57a86066612fcff7e1769c9b43a6e827d7c33927c08ef6f`; after TASK-010 added aggregate diagnostics, the same agreement counts re-generated with current artifact hash `1493abcafa28487da0fbd710e7187e9c41347fda08ae65c7f857d1ab1a85ccc8`. The original 40-test suite and official v2 format validation passed. These are noisy-provider agreement checks, not official accuracy or `spellF1`.
- Artifact: `docs/verification/TASK-006-results.json` (safe aggregates and fingerprints only); raw external files stay under ignored `data/external/skillcorner/`.
- Blocker: none for this scoped comparison. Independent human-labeled data is still needed to validate model quality or choose new parameters.
- Last updated: 2026-11-10
- Handoff: prepare TASK-007 submission document once the registered team name is known; seek a compatible independent labeled match before claiming any model gain.

### TASK-007 — Prepare the reproducible submission package
- Status: verifying
- Priority: P1
- Owner: Codex
- Depends on: TASK-005; TASK-006 completed or explicitly deferred; registered team name
- Goal: Produce an exact validated team-named CSV and short technical document from one documented command.
- Scope: final configuration, input/code/dependency fingerprints, technical document, restricted-data review and delivery checklist.
- Acceptance criteria: exact team-named CSV passes the official validator; repeated generation hashes match; document covers approach, assets, training-data provenance, possession rules, limitations and reproduction; no restricted assets or reconstructive exports are tracked.
- Verification: official validator, repeat hash, clean-clone reproduction instructions, diff and Git content review; record in `docs/verification/TASK-007.md`.
- Evidence: Team name `NRDS` confirmed. Frozen temporal v8 and local `evaluation/results/NRDS.csv` selected. The submission-ready document is `docs/NRDS_technical_document.md`. Current public revision `ce39ad6...` passed 100 tests and regenerated the exact validated CSV, SHA-256 `97bf92b0...a0ff19`. Content, provenance, rules, secrets/restricted-data, diff and claim checks passed. Full record: `docs/verification/TASK-007.md`.
- Blocker: none for local package preparation. Committing/pushing the document and submitting the form require separate user authorization.
- Last updated: 2026-11-16
- Handoff: review the technical document with the team, then request authorization to commit/push it. Upload `NRDS.csv`, the public repository URL and the technical document through the team’s emailed Google Form; no form submission has been made.

### TASK-010 — Tune temporal settings on external matches
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: TASK-006; public SkillCorner development and holdout matches
- Goal: Search a small predeclared configuration grid for higher agreement with external provider team labels, then assess the selected candidate on unseen matches.
- Scope: external-only tuning runner and tests, versioned candidate config, holdout report, reproducible tactical output if retained. Preserve official baseline/evaluator and existing v2 output.
- Acceptance criteria: source and match split are fixed before tuning; only ten development matches select parameters; nine additional matches are held out until selection; no challenge public labels are used for selection; report both provider-reference agreement and coverage, plus transition/dead diagnostics; do not call provider agreement challenge accuracy. A ~90% agreement target is aspirational, not a completion claim.
- Verification: synthetic tests, full suite, repeat aggregate hash; if a new tactical CSV is generated, exact official validator and repeat generation hash; review diff and record commands/results in `docs/verification/TASK-010.md`.
- Evidence: 144-setting development search selected v3; one exploratory offline backfill rule yielded v4 before holdout scoring. Frozen v4 matched 241,131 / 290,725 provider H/A frames (82.94%) across nine held-out matches versus 240,264 / 290,725 (82.64%) for v2. Provider live-phase agreement was 88.72%. The ~90% per-frame target was not met. The v4 BAR-ATH CSV passed the official 199,319-row format validator and repeated with SHA-256 `9b14309313b4d5e163d8513b06c1c87afcfbb489b3259f3f7f647d5a4955a655`. The nine-match holdout report repeated byte-for-byte, SHA-256 `d80eb68a27f4117de9d59a1ac1a452c83132d2d358b6a5dd1894e6b4b1a18289`. Full suite: 50 tests passed; `git diff --check` passed. Commands and limits are in `docs/verification/TASK-010.md`.
- Artifact: `model/config_v3.json`, `model/config_v4.json`, aggregate reports under `docs/verification/TASK-010-*.json`, ignored `evaluation/results/temporal_v4.csv` and separate ignored diagnostics.
- Blocker: none for this tuning/format-verification task; independent human-labeled validation and official ranking evidence remain unavailable.
- Last updated: 2026-11-10
- Handoff: prepare TASK-007 once the registered team name and final method choice are available. Seek independent human-labeled matches before calling v4 a quality gain or expanding supervised tuning. Do not report a 90% or official-score claim.

### TASK-011 — Isolate the project Git repository
- Status: done
- Priority: P1
- Owner: Codex
- Depends on: none
- Goal: Make this folder the project Git root and stop unrelated folders under the home directory from inheriting a Git repository.
- Scope: preserve the nested project's Git history, move its files into this folder, disable the home Git root, retain recoverable backups, and update stale path instructions.
- Acceptance criteria: this folder resolves to itself as Git root with project HEAD intact; the home folder is no longer a Git repository; project inputs and environment still work; prediction output is unchanged.
- Verification: `docs/verification/TASK-011.md`.
- Evidence: 50 tests passed; official validator accepted the existing 199,319-row v4 CSV; regenerated v4 CSV matched SHA-256 `9b14309313b4d5e163d8513b06c1c87afcfbb489b3259f3f7f647d5a4955a655` byte for byte; Git root and HEAD checks passed.
- Blocker: none. VS Code may need its old window reloaded to clear cached repository discovery.
- Last updated: 2026-11-11
- Handoff: open this folder directly in a new VS Code window; keep the recoverable Git backups until the user is satisfied with the workspace behavior.
