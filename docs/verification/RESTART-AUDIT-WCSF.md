# V8 restart and previous-team audit

Date: 2026-11-12. Base commit: `c9d1c46082784f12562e8de609d74fd93c1a00cb`.

This is a diagnostic on the previously inspected WCSF provider-reference match, not fresh validation or model selection. The source's AliveFlag/PossessionFlag are comparison references only. V7 and v8 are run unchanged with the same external adapter and source archives. The official scoring implementation reports full-match H/A/D agreement and spellF1. Clean restart events are D runs immediately preceded and followed by a known H/A reference within one half; unknown boundary cases are excluded. For each restart, the first predicted H/A before the next reference-team change is assessed, and D persistence is checked only when the reference stays live long enough.

| Metric | V7 | V8 |
| --- | ---: | ---: |
| Full-match H/A/D provider agreement | 76.47% | 82.52% |
| Official-implementation spellF1 | 0.4770 | 0.5028 |
| Clean provider restarts | 102 | 102 |
| Predicted D at the reference restart | 11/102 | 32/102 |
| Still D after 1 s of reference-live play | 9/99 eligible | 20/99 eligible |
| Still D after 3 s of reference-live play | 1/69 eligible | 2/69 eligible |
| No predicted live team before next reference-team change | 4/102 | 11/102 |
| First predicted live team matches the new reference team | 96/98 evaluable | 85/91 evaluable |
| First predicted live team matches the pre-dead team when reference team changed | 1/80 evaluable | 5/75 evaluable |

V8 is better overall on this source, but it holds D longer around provider restarts. In `model/inference.py`, entry to D resets pending control and sets `state = 'D'`; there is no instruction to restore the pre-dead team. A later H/A output requires a new observed candidate to confirm control. The five previous-team returns among changed-team restarts show an empirical failure mode, not a hard-coded return policy. They are fewer than the 70 changed-team restarts where the first predicted live team matches the new team.

This match was previously used to assess v7 and inspect v8; its reference provenance is not independently human verified. Event boundaries can differ from physical restart time, and the one-match results cannot establish full challenge accuracy. There are no fresh compatible final-test matches locally. Do not tune a new restart rule on this audit and then report this source as a holdout.

Reproduction:

```sh
python -m model.run_restart_audit \
  --first /path/to/positions_FIRST_HALF.csv.zip \
  --second /path/to/positions_SECOND_HALF.csv.zip \
  --output /tmp/restart-audit.json
python -m unittest tests.test_restart_audit
```

The aggregate JSON with input hashes is `RESTART-AUDIT-WCSF-v2.json`. The full 95-test suite passed after the audit-count correction. No match data or frame-level output is tracked.
