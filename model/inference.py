"""Temporal possession inference from tactical frame evidence.

The evidence contract is documented in docs/INTERFACE.md. Candidate proximity
must persist before it becomes control; a brief opposing touch is insufficient.
All state resets at each official half boundary. No match labels are used here.
"""


def infer(evidence, blocks, config):
    """Return submission labels and separate diagnostic reasons per video frame."""
    if config.get("control_backfill", False) and config["evidence_gap_frames"] != 0:
        raise ValueError("control_backfill requires zero evidence_gap_frames")
    count = len(evidence)
    labels = ["X"] * count
    reasons = ["outside_half"] * count

    # Validate the entire block schedule before applying any temporal state.
    previous_half = 0
    previous_last = -1
    for block in blocks:
        if not isinstance(block, (tuple, list)) or len(block) != 3:
            raise ValueError("half block must contain half, first, last")
        half, first, last = block
        if (any(isinstance(value, bool) or not isinstance(value, int)
                for value in block)
                or half <= previous_half or first <= previous_last
                or first < 0 or last < first or last >= count):
            raise ValueError("invalid or overlapping half boundary: {!r}".format(block))
        previous_half, previous_last = half, last

    for _, first, last in blocks:
        state = None
        pending = None
        pending_first = None
        votes = gap = outside_run = 0
        pre_dead_team = None
        fast_candidate = None
        fast_votes = 0
        fast_first = None
        for frame in range(first, last + 1):
            row = evidence[frame]
            candidate = row["candidate"]
            if candidate not in (None, "H", "A"):
                raise ValueError("invalid candidate at frame {}".format(frame))

            outside_run = outside_run + 1 if row["outside"] else 0
            if (outside_run >= config["out_of_bounds_frames"]
                    or row["stationary_set_piece"]
                    or (config.get("stationary_unattended_frames") is not None
                        and row.get("stationary_unattended", False))
                    or (config.get("stationary_observed_frames") is not None
                        and row.get("stationary_observed", False))):
                if state in ("H", "A"):
                    pre_dead_team = state
                state = "D"
                fast_candidate, fast_votes, fast_first = None, 0, None
                pending, pending_first, votes, gap = None, None, 0, 0
                labels[frame] = "D"
                reasons[frame] = ("sustained_out_of_bounds" if outside_run >= config["out_of_bounds_frames"]
                                  else "stationary_set_piece" if row["stationary_set_piece"]
                                  else "stationary_unattended" if row.get("stationary_unattended", False)
                                  else "stationary_observed")
                continue

            # An observed out-of-bounds frame cannot support player control.
            if row["outside"]:
                candidate = None
            if (state == 'D' and config.get('restart_min_ball_speed_mps') is not None
                    and (row.get('ball_speed_mps') is None
                         or row['ball_speed_mps'] < config['restart_min_ball_speed_mps'])):
                candidate = None
            fast_frames = config.get('opponent_restart_control_frames')
            if (state == 'D' and fast_frames is not None
                    and pre_dead_team in ('H', 'A')
                    and candidate in ('H', 'A') and candidate != pre_dead_team
                    and row.get('ball_speed_mps') is not None
                    and row['ball_speed_mps'] >= config['opponent_restart_min_ball_speed_mps']):
                if candidate == fast_candidate:
                    fast_votes += 1
                else:
                    fast_candidate, fast_votes, fast_first = candidate, 1, frame
            else:
                fast_candidate, fast_votes, fast_first = None, 0, None
            if candidate is not None and candidate != state:
                if candidate != pending:
                    pending, votes, gap = candidate, 0, 0
                    pending_first = frame
                votes += 1
                gap = 0
                needed = (config.get('restart_control_frames', config['control_frames'])
                          if state == 'D' else config['control_frames'])
                fast_ready = state == 'D' and fast_frames is not None and fast_votes >= fast_frames
                if votes >= needed or fast_ready:
                    confirmed_first = fast_first if fast_ready else pending_first
                    state = candidate
                    if config.get("control_backfill", False):
                        for confirmed_frame in range(confirmed_first, frame):
                            labels[confirmed_frame] = candidate
                            reasons[confirmed_frame] = "control_backfilled"
                    pending, votes = None, 0
                    pending_first = None
                    fast_candidate, fast_votes, fast_first = None, 0, None
                    reason = "control_confirmed"
                else:
                    reason = "control_pending"
            elif candidate is not None and candidate == state:
                pending, pending_first, votes, gap = None, None, 0, 0
                reason = "control_held"
            else:
                if pending is not None:
                    gap += 1
                    if gap > config["evidence_gap_frames"]:
                        pending, pending_first, votes, gap = None, None, 0, 0
                reason = "missing_ball" if not row["ball_seen"] else "contested_or_loose"

            labels[frame] = state or "X"
            reasons[frame] = "awaiting_restart" if state == "D" else reason

    return labels, reasons
