# NRDS — More than a Hack 2027 ball possession

NRDS generates one possession label for every frame of the official BAR–ATH tactical timeline.
The final submission model is the deterministic, offline **temporal v8** state machine configured
by [`model/config_v8.json`](model/config_v8.json). It produces the required labels `H` (home live),
`A` (away live), `D` (dead ball), and `X` (abstention).

The official starter, scorer, baseline files, and challenge documentation are retained from
[`metrica-sports/more-than-a-hack-2027`](https://github.com/metrica-sports/more-than-a-hack-2027)
at revision `f8f2629ff1e0985f81d7e59d8413678514ee1530`. Team code is separate under
`model/`; the official evaluator and starter are unchanged.

## Submission package

The official challenge requires three deliverables. The directory layout below is a project
organization choice, not an additional organizer requirement.

| Required deliverable | Project artifact |
| --- | --- |
| Possession CSV | `evaluation/results/NRDS.csv` (generated locally and intentionally ignored by Git) |
| Public reproducible code repository | This repository, including pinned dependencies and tests |
| Short technical document | [`docs/NRDS_technical_document.md`](docs/NRDS_technical_document.md) |

The frozen-model record is [`model/v8_frozen.json`](model/v8_frozen.json). The expected SHA-256
of the exact CSV is `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`.
The CSV must be uploaded separately; it is not intended for the public repository. For the form,
upload the technical document under the organizer-recommended team filename `NRDS.md` (or an
exported `NRDS.pdf`); the longer repository filename keeps its purpose explicit.

## Directory layout

```text
.
├── model/                  NRDS ingestion, evidence, temporal inference, and frozen config
├── tests/                  synthetic, integration, metric, and leakage-safety tests
├── docs/                   technical document, data audit, decisions, and verification records
├── data/                   authorized local inputs (ignored except data/README.md)
├── evaluation/             unchanged official scorer, validator, public GT, and baselines
├── starter/                unchanged official loaders, notebooks, and baseline generator
├── games.py                official match/frame constants
├── requirements-lock.txt   pinned verified Python environment
└── TASKS.md                completed work, evidence, blockers, and handoff
```

See [`model/README.md`](model/README.md) for the final runtime files versus historical experiments,
and [`docs/README.md`](docs/README.md) for the documentation index.

## Installation

Python 3.9 or later is recommended. Run all commands from the repository root.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m unittest discover -s tests -v
```

`requirements.txt` is the official upstream list; `requirements-lock.txt` pins the environment
used for the verified NRDS generation.

## Authorized data placement

Do not commit challenge assets. Either place the authorized bundle under `data/` or point
`MTAH_DATA_DIR` to its root:

```text
$MTAH_DATA_DIR/
└── tactical/
    ├── BAR-ATH_tactical_atd.xml
    ├── BAR-ATH_tactical_atd.txt
    └── BAR-ATH_tactical_smart_tagging.xml
```

```bash
export MTAH_DATA_DIR=/absolute/path/to/OTWBARCA
.venv/bin/python -c 'from starter.load_atd import check_alignment_raw; print(check_alignment_raw())'
```

V8 uses only those three tactical files. It does not require either video, homography, an Excel
export, or broadcast data. The ATD loader maps `frame_id` to zero-based tactical frames with
`video_frame = frame_id - 1`; Smart Tagging uses `round(seconds * 25)`.

## Generate the final prediction

```bash
.venv/bin/python model/run.py \
  --config model/config_v8.json \
  --output evaluation/results/NRDS.csv \
  --diagnostics evaluation/reports/NRDS_diagnostics.csv
```

Diagnostics are deliberately separate from the two-column submission. V8 is deterministic and
has no random seed. To verify reproducibility without replacing the deliverable:

```bash
repeat_dir=$(mktemp -d)
.venv/bin/python model/run.py \
  --config model/config_v8.json \
  --output "$repeat_dir/NRDS.csv" \
  --diagnostics "$repeat_dir/NRDS_diagnostics.csv"
cmp evaluation/results/NRDS.csv "$repeat_dir/NRDS.csv"
shasum -a 256 evaluation/results/NRDS.csv "$repeat_dir/NRDS.csv"
```

## Validate and evaluate

Validate the exact file that will be uploaded:

```bash
.venv/bin/python evaluation/validate_submission.py evaluation/results/NRDS.csv
```

The validator must find exactly the columns `frame,label`, 199,319 data rows, ordered unique
frames 0–199318, and only H/A/D/X labels.

To reproduce the official baseline **public-window pipeline check** without accidentally scoring
local predictions:

```bash
baseline_dir=$(mktemp -d)
cp evaluation/results/baseline_*.csv "$baseline_dir/"
.venv/bin/python evaluation/run_evaluation.py \
  --results "$baseline_dir" --out "$baseline_dir" --no-detail
```

The public five-minute labels are not training or model-selection data. `spellF1` is the ranking
metric; public-window accuracy is not a private full-match score. NRDS has no observed private
BAR–ATH accuracy. V8's recorded 88.55% H/A/D agreement and 0.4785 spellF1 are development results
against provider reference fields on seven external IDSSE matches, not independent challenge
results. Full definitions, provenance, ablations, and limitations are in
[`docs/verification/TASK-015.md`](docs/verification/TASK-015.md).

## Model behavior and records

V8 treats proximity as evidence rather than proof. It requires sustained opposing control before
a turnover, retains the last controller through loose or missing-ball periods, separates
dead-ball evidence from team control, requires confirmed control after a restart, and resets all
state at halftime. Confirmed windows may be backfilled, so inference is offline with up to three
seconds of lookahead. Threshold provenance and the absence of an untouched compatible final test
are documented in the technical document and frozen record.

Restricted assets, generated frame-level predictions, credentials, caches, and environments are
excluded by [`.gitignore`](.gitignore). Do not add private ground truth or manually correct the
provided match. See [`TASKS.md`](TASKS.md) for the current handoff.
