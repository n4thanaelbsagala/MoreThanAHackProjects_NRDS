# NRDS — More than a Hack 2027 Ball Possession

**Final model:** Temporal v8 (`model/config_v8.json`)  
**Submission:** `NRDS.csv`  
**Code:** https://github.com/n4thanaelbsagala/MoreThanAHackProjects_NRDS  
**Verified public code revision:** `ce39ad61a4b089b1611cafb7f110279ab2db6b8d`  
**Frozen v8 base revision:** `c9d1c46082784f12562e8de609d74fd93c1a00cb`  
**Official starter revision:** `f8f2629ff1e0985f81d7e59d8413678514ee1530`

## 1. Approach and rationale

NRDS uses a deterministic, explainable offline temporal state machine rather than a learned
frame classifier. The supplied ball is missing on many frames, tracking slots are not stable
player identities, and the competition ranks possession *spells* with spellF1 rather than raw
frame accuracy. We therefore treat player–ball proximity as temporary evidence, require
persistent evidence before assigning control, retain the last controller through loose or
missing-ball periods, and model dead-ball intervals separately.

The pipeline is divided into strict ingestion and alignment (`model/evidence.py`), motion and
stoppage evidence (`model/motion.py`, `model/stoppage.py`), temporal decoding
(`model/inference.py`), and two-column export (`model/temporal.py`). It has no random component
and no fitted estimator. The final configuration was selected before producing the submitted
BAR–ATH file and is frozen at SHA-256
`61ab5e79210abfd7ba07c24d785890bdeb7f507f43d0c2e0f41d96f7926f6238`.

## 2. Assets, preprocessing, and alignment

The final inference run uses only three authorised **tactical** assets from the supplied game:

- `BAR-ATH_tactical_atd.xml`: metadata, team membership, and tracking-slot order;
- `BAR-ATH_tactical_atd.txt`: automatic player and ball positions for every tactical frame;
- `BAR-ATH_tactical_smart_tagging.xml`: automatic `SET PIECES` intervals.

We did **not** use either video, broadcast tracking, tactical or broadcast homography, external
event data about BAR–ATH, an Excel export, or any human correction. Homography is unnecessary
because ATD already supplies normalised pitch coordinates. Smart Tagging is automatic Metrica
output and is treated as noisy evidence, never copied as a possession answer.

The loader rejects missing, duplicated, shifted, or extra ATD rows instead of repairing them.
ATD `frame_id` is converted with `video_frame = frame_id - 1`; Smart Tagging time is mapped with
`round(seconds * 25)`. The submission timeline is 199,319 tactical frames at 25 Hz, indexed
0–199318. The official first-half block is 11,185–90,651 and the second-half block is
110,808–190,197, both inclusive. All temporal state resets at halftime; frames outside these
blocks are `X`.

ATD coordinates remain normalised in evidence records, but distances and motion are calculated
in metres using the configured 105.3 × 68.0 m pitch. Metadata maps every tracking slot to home or
away; a slot is not treated as a stable person. Barcelona is `H` and Athletic Club is `A`.
Non-finite ball or player coordinates remain missing. We do not interpolate through tracking
gaps.

## 3. Features and temporal inference

For each observed in-pitch ball frame, the model calculates the nearest observed home and away
player. A team becomes the frame-level control candidate only when its nearest player is within
2.5 m of the ball and at least 0.75 m closer than the nearest opponent. This is evidence of
control, not possession by itself.

The final temporal rules are:

- **Initial control and turnovers:** a candidate must persist for 12 uninterrupted frames
  (0.48 s). Once confirmed, offline backfill assigns that team from the first frame of the
  uninterrupted run. A genuine turnover therefore requires sustained opposing control.
- **Loose balls, challenges, passes, and deflections:** if evidence is absent, contested, or too
  brief, the previous controlling team is retained. A single opposing touch does not transfer
  possession.
- **Missing observations:** a missing ball cannot create `D`. During a live loose or missing
  period, the last controller is retained; before either team has established control the model
  emits `X`. Missingness also breaks stationary-ball evidence windows.
- **Out of bounds:** 25 consecutive observed out-of-bounds frames confirm `D`. The pitch boundary
  tolerance is 0.005 in normalised coordinates.
- **Tagged set pieces:** inside an automatic `SET PIECES` interval, 25 observed frames whose ball
  positions remain within 0.5 m confirm `D`; after confirmation the observed window is backfilled.
  A tag without observed stationarity is insufficient.
- **Unattended stationary ball:** 25 valid frames within a 0.5 m region confirm `D` when the
  nearest observed player from each team remains at least 2.0 m away.
- **General observed stationary ball:** 75 valid frames (3 s) within a 0.5 m region confirm `D`
  even with nearby players. Both teams need finite nearest-player distances. Exact coordinated
  freezes of both nearest-team distance series suppress this cue. This confirmation is offline
  and may backfill up to three seconds, but never across a half.
- **Restart:** after `D`, the system remains dead until one team completes the same 12-frame
  control confirmation. Backfill then starts the live label at the beginning of that confirmed
  run. No separate speed-gated restart is enabled in the submitted configuration.

Ball speed and acceleration are computed causally from actual timestamp differences without
bridging missing observations or halves. They supported controlled restart experiments, but the
frozen v8 configuration does not use a motion threshold. Diagnostic reason codes remain in a
separate file and never enter the submitted `frame,label` CSV.

## 4. Training and labelled-data provenance

There was **no supervised model training**, gradient fitting, learned imputation, or learned
preprocessing. However, thresholds and rules were selected using labelled/provider-reference
fields from other games, so those sources are disclosed below. No label from the supplied
BAR–ATH game was used for training, threshold selection, feature selection, or model selection.

| Source | Amount and role | Label origin and use |
| --- | --- | --- |
| [SkillCorner Open Data](https://github.com/SkillCorner/opendata), revision `4340d274…` | 19 closed Australian A-League matches at 10 Hz; 1,185,564 tracking frames. Ten development matches contained 314,964 available provider H/A frames; nine later matches contained 290,725. | SkillCorner `possession.group` and in-play phase team fields are automatic provider references, not independently verified human annotations. Ten matches selected the 2.5 m control reach, 0.75 m margin, 12-frame confirmation, zero evidence gap, and control backfill inherited by v8. Nine matches were a one-time historical holdout. |
| [IDSSE / DFL / Sportec](https://huggingface.co/datasets/pysport/idsse-data), original dataset [DOI](https://doi.org/10.6084/m9.figshare.28196177), revision `a715a38…` | Seven German professional matches at 25 Hz; 1,002,644 frames. All seven were classified as development for the final whole-match grouped v8 experiment. | Provider `BallStatus` and `BallPossession` fields supplied H/A/D references. Their exact annotation/generation procedure was not established as human adjudication, so we call them provider references rather than ground truth. Reference fields were isolated from inference features. They selected stoppage rules and the final v8 candidate. |
| [WCSF Solution Room](https://github.com/MatKempeGroningen/WCSF_SolutionRoom), revision `1c9ba798…` | One anonymised professional match at 10 Hz; 57,374 frames. | Source `AliveFlag` and `PossessionFlag` fields were used as provider references for a one-time historical v7 assessment. The source withholds team names/date and does not establish human-adjudicated provenance. It influenced the v7 checkpoint inherited by v8, but was excluded from all v8 candidate selection. |
| Official BAR–ATH public window | Five minutes / 17 published possessions. | Used only in the official baseline pipeline check. It was not opened for v8 training, tuning, threshold selection, model selection, or reported v8 performance. The private full-match labels were never available. |

All external matches are from other games and public, inspectable sources. Whole matches—not
overlapping frames—form v8 cross-validation groups. SkillCorner and WCSF results had already been
inspected and were explicitly excluded from v8 selection. All seven IDSSE matches had also been
seen in earlier work; grouped evaluation reduces within-match leakage but does not make them a
pristine independent final test.

## 5. Evaluation and observed results

The unchanged official possession metric implementation was used for development scoring.
spellF1—the ranking metric—matches maximal H/A spells one-to-one by temporal IoU and averages F1
over IoU thresholds 0.3–0.7. Macro-F1 is the first tie-break. H/A/D agreement is included only as
a diagnostic and is not the competition ranking score.

The bounded v8 experiment compared 12 predeclared variants on seven complete IDSSE matches.
Each outer fold selected a candidate on six matches and evaluated it on the seventh. Candidate
selection prioritised pooled spellF1, then macro-F1 and H/A/D agreement, while permitting no more
than a 0.5 percentage-point regression from v7 in overall agreement or conditional live-team
agreement.

| Development/provider-reference result | v7 baseline | Frozen v8 |
| --- | ---: | ---: |
| Pooled H/A/D agreement | 84.11% | **88.55%** |
| Macro-F1 | 0.8327 | **0.8724** |
| spellF1 | 0.4432 | **0.4785** |
| Dead-ball recall | 85.94% | **96.82%** |
| Conditional H/A agreement when both labels are live | 88.51% | **88.54%** |

The merged whole-match out-of-fold selection result was 88.77% H/A/D agreement and 0.4841
spellF1. These are **development results against provider fields**, not independent accuracy and
not BAR–ATH scores. No untouched compatible match remained after development, so independent
85% accuracy is unverified.

The public five-minute BAR–ATH window was not used to score or select v8. We report no public v8
metric and have no private full-match score. The final `NRDS.csv` contains 75,339 H, 70,868 A,
12,460 D, and 40,652 X labels. The official validator accepted exactly 199,319 ordered rows,
frames 0–199318, with only H/A/D/X. Two generations matched byte-for-byte; the final SHA-256 is
`97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`.

## 6. Limitations and compliance

Stationary-ball evidence can confuse a genuine low-motion live situation with a stoppage, while
missing-ball stoppages may remain undetected. On IDSSE development data the largest remaining
timing error was delayed restart release. The exact-freeze safeguard catches only a narrow class
of tracking freezes. Proximity cannot prove control, and automatic Smart Tagging and external
provider fields have definition and measurement noise. The final method is offline because
confirmed windows are backfilled. Results may shift between 10 Hz broadcast tracking, 25 Hz
external tracking, and the challenge's 25 Hz tactical tracking.

No manual BAR–ATH labels, frame-specific corrections, private ground truth, or human-produced
BAR–ATH event data were used. Restricted match assets and frame-level tracking exports are
gitignored and are not in the public repository. The submission is entirely algorithmic and
reproducible. We know of no deviation from the competition rules; the principal evidence gap is
the absence of a genuinely untouched, compatible external final-test set.

## 7. Installation and exact reproduction

Python 3.9.6 on macOS arm64 was used for the verified run. The pinned environment contains NumPy
2.0.2, pandas 2.3.3, python-dateutil 3.0.0, pytz 2026.6, six 1.17.0, and tzdata 2026.6.

```bash
git clone https://github.com/n4thanaelbsagala/MoreThanAHackProjects_NRDS.git
cd MoreThanAHackProjects_NRDS
git checkout ce39ad61a4b089b1611cafb7f110279ab2db6b8d

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt

# Point this at the authorised bundle root containing tactical/.
export MTAH_DATA_DIR=/absolute/path/to/OTWBARCA

# Confirm strict ATD alignment, run tests, and generate the exact submission.
.venv/bin/python -c 'from starter.load_atd import check_alignment_raw; print(check_alignment_raw())'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python model/run.py \
  --config model/config_v8.json \
  --output evaluation/results/NRDS.csv \
  --diagnostics evaluation/reports/NRDS_diagnostics.csv

# Validate and fingerprint the exact file to upload.
.venv/bin/python evaluation/validate_submission.py evaluation/results/NRDS.csv
shasum -a 256 evaluation/results/NRDS.csv
```

Expected submission hash:

```text
97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19
```

The authorised bundle used for the verified run had these input hashes:

```text
f130e350d2bfdf734b7e32f072931fccc6d015c1e837d082064875fe0a700431  BAR-ATH_tactical_atd.txt
327e35e32e46a647389b88f883d4f9a2ab931e3e6148aef2fcf8f22b1e93c43a  BAR-ATH_tactical_atd.xml
0594d35e3df01b9c5002372d8615e2e8ef5379ac8f4e84c5ef7a53f4304c9019  BAR-ATH_tactical_smart_tagging.xml
```

The public five-minute scorer is deliberately absent from the reproduction commands because it
is not required to generate or validate the submission and was not used to select v8.
