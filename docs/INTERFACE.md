# Tactical evidence → temporal inference contract (2026-11-09)

This contract permits independent implementation of input handling and temporal logic.
The lead owns this file and integration. The official `games.py`, `starter/`, and
`evaluation/` files are read-only for this work.

## Data module: `model/evidence.py`

`load_tactical_evidence(config, data_dir=None)` returns `(evidence, team_names)`:

- `evidence` is a list of exactly `games.source_frames("tactical", GAME)` records, ordered
  by zero-based tactical video frame. ATD `frame_id` must be exactly `index + 1`, with
  no skipped, duplicated, or extra records. A mismatch raises `ValueError` rather than
  shifting or truncating data.
- `team_names` is `(home_name, away_name)` from the two metadata teams. Each ATD slot
  maps to H or A through its metadata `teamId`; slots are not stable player identities.
- Each evidence record is a dict with these required keys and meanings:

| Key | Type | Meaning |
| --- | --- | --- |
| `candidate` | `"H"`, `"A"`, or `None` | Nearby team's tentative control evidence, never a final label. |
| `outside` | `bool` | Finite ball coordinate beyond the configured pitch tolerance. |
| `ball_seen` | `bool` | Both normalized ball coordinates are finite. |
| `ball_xy` | normalized `(x, y)` tuple or `None` | Raw tactical pitch position, not metres. |
| `players_seen` | nonnegative `int` | Number of slots with finite positions in this frame. |
| `stationary_set_piece` | `bool` | Sustained observed stationary ball within an automatic set-piece interval; a tag alone is insufficient. With v2 offline backfill, the entire confirmed observation window is marked. |
| `nearest_distance_m` | H/A to finite metres or infinity | Nearest observed player of each team; slots are not identities. |
| `timestamp_s` | finite seconds | Monotonic within a half; tactical and IDSSE use their own 25 Hz timelines. |
| `ball_speed_mps` | nonnegative float or `None` | Causal derivative using actual adjacent timestamps; absent after missing observations and at half starts. |
| `ball_acceleration_mps2` | float or `None` | Causal speed derivative; absent until two consecutive speed estimates exist. |
| `stationary_unattended` | `bool` | Optional confirmed stationary-ball cue requiring both teams' finite player distances and configured clearance. |
| `stationary_observed` | `bool` | Optional confirmed stationary-ball cue that allows nearby players but rejects exact coordinated distance freezes. |

Distance calculations scale normalized x/y by `games.GAMES[GAME]["pitch"]` in metres.
Missing ball or player coordinates yield absent evidence, never dead-ball evidence by
themselves. Smart Tagging uses its official rounded seconds × 25 frame conversion.
Only tactical assets are loaded, through `games.require` and starter helpers.

## Model module: `model/inference.py`

`infer(evidence, blocks, config)` returns `(labels, reasons)` as lists of equal length
to `evidence`. `blocks` is the official `games.half_video_blocks(GAME)` tuple sequence
with inclusive first/last frames. Outside these blocks, labels are `X`. Within each
half, no state carries from the previous half. Labels are only `H`, `A`, `D`, `X`.
Reasons describe uncertainty and transitions for a separate diagnostic file.
Inference may read evidence keys above, but must not read tracking files, public
ground truth, or scorer output.

`model/config.json` retains v1 behavior. `model/config_v2.json` enables optional
backfill of an observed stationary set-piece window after it has been confirmed;
the duration and radius thresholds are unchanged. Neither file is changed
independently; any new threshold requires lead coordination and a documented
general rationale. Synthetic tests must cover missing evidence, incidental touches,
confirmed turnovers, stoppages, restarts, half boundaries, and invalid blocks.

The later external-only TASK-010 experiment leaves v1/v2 configurations unchanged.
`model/config_v3.json` records tuned distance and duration settings from public
SkillCorner development matches. `model/config_v4.json` additionally enables
`control_backfill`: after a sustained candidate run confirms control, offline
inference assigns that team from the run's first frame within the same half.
Backfill requires `evidence_gap_frames: 0`, so it never spans a missing or
contested candidate frame.
Unconfirmed opposing evidence is never backfilled. This optional behavior uses
future evidence, and its reason code stays in diagnostics rather than labels.

The optional v6 rule (`model/config_v6_stoppage.json`) adds
`stationary_unattended` to evidence after 50 consecutive observed 25 Hz frames
where the ball stays within 0.5 m and each team's nearest observed player remains
at least 3 m away. A player from both teams must be observed. Confirmation
backfills only within one half; missing observations and motion break the run.
Inference treats this cue as D only when the configuration enables it. Restart
still requires confirmed control. The cue is derived from positions, never an
external possession/live-dead reference field.

The frozen v8 configuration adds `stationary_observed`: the ball and player-distance
observations must be valid, inside the pitch, and stationary inside the configured radius for
the configured duration. It is independent of the unattended cue. Exact simultaneous freezes
in both nearest-team distance series suppress this evidence. Confirmation can backfill only the
observed window inside one half, so v8 is offline with bounded lookahead. Missing observations
remain unknown rather than dead. Optional restart settings can use a separate control duration
and causal minimum ball speed, but those settings are not enabled in frozen v8. Dataset roles,
selection safeguards and limitations are in `model/dataset_manifest_v8.json`,
`model/v8_protocol.json`, and `docs/verification/TASK-015.md`.

## Integration and verification

The lead wires these modules into `model/temporal.py` / `model/run.py` and owns
submission serialization. The output remains exactly `frame,label` with 199,319
ordered rows. The official validator checks the exact generated file. The public
five-minute labels may check pipeline alignment, never select models or thresholds.
