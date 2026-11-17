# Model directory

The submission model is **temporal v8**, configured by `config_v8.json` and frozen in
`v8_frozen.json`. Run it through `run.py`; the root README contains the exact final command.

## Final inference path

- `run.py`: command-line entry point.
- `temporal.py`: orchestration, output serialization, and diagnostics.
- `evidence.py`: strict tactical ATD and Smart Tagging ingestion.
- `motion.py` and `stoppage.py`: motion, tracking-quality, and dead-ball evidence.
- `inference.py`: temporal possession state machine.
- `config_v8.json`: final thresholds and durations.
- `v8_frozen.json`, `v8_protocol.json`, and `dataset_manifest_v8.json`: frozen provenance,
  development protocol, and leakage-safe match roles.

## Retained research history

Earlier `config*.json` files and the external adapters/evaluation scripts are retained because
they support the documented ablations and provenance records. They are not required for final
BAR–ATH inference. `config_v9_experiment.json` and the opponent-restart scripts describe a
rejected, opt-in experiment; they do not replace v8. Raw external datasets stay outside Git.

The official baseline remains in `starter/baseline.py` and was not modified by NRDS.
