"""Map public SkillCorner tracking to the existing inference evidence contract.

This adapter is for cross-match diagnostics. SkillCorner uses 10 fps broadcast
tracking in pitch metres and supplies automatic possession fields. These are
provider references, not verified ground truth or challenge submission labels.
"""

import json
import math
import hashlib
import csv
from collections import Counter

from model.inference import infer


def scale_config(config, target_fps):
    """Preserve 25 fps threshold durations when applying the model at another fps."""
    if target_fps <= 0:
        raise ValueError("target_fps must be positive")
    scaled = dict(config)
    for name in ("control_frames", "evidence_gap_frames", "out_of_bounds_frames",
                 "set_piece_stationary_frames", "stationary_unattended_frames",
                 "stationary_observed_frames", "opponent_restart_control_frames"):
        if name in scaled:
            scaled[name] = max(0 if name == "evidence_gap_frames" else 1,
                               round(config[name] * target_fps / 25))
    if config.get("opponent_restart_control_frames") is not None:
        scaled["opponent_restart_control_frames"] = max(
            2, round(config["opponent_restart_control_frames"] * target_fps / 25))
    return scaled


def _point(record):
    x, y = record.get("x"), record.get("y")
    if x is None or y is None:
        return None
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("non-numeric tracking coordinate")
    return (x, y) if math.isfinite(x) and math.isfinite(y) else None


def load_match(metadata_path, tracking_path, config):
    """Return evidence, inclusive period blocks, provider H/A references and metadata.

    Reject gaps and metadata/row disagreement instead of shifting frames. Finite
    extrapolated positions are accepted, as in the named source file; the provider's
    `is_detected` field remains available for the audit but is not a label.
    """
    with open(metadata_path) as handle:
        match = json.load(handle)
    home = match["home_team"]["id"]
    away = match["away_team"]["id"]
    length, width = match["pitch_length"], match["pitch_width"]
    if home == away or length <= 0 or width <= 0:
        raise ValueError("invalid match team or pitch metadata")
    player_team = {player["id"]: player["team_id"] for player in match["players"]}
    periods = match["match_periods"]
    blocks = [(period["period"], period["start_frame"], period["end_frame"])
              for period in periods]
    if not blocks or any(first < 0 or last < first for _, first, last in blocks):
        raise ValueError("invalid match periods")
    if any(blocks[i][0] <= blocks[i-1][0] or blocks[i][1] <= blocks[i-1][2]
           for i in range(1, len(blocks))):
        raise ValueError("overlapping or unordered match periods")
    side_by_id = {home: "H", away: "A"}
    evidence, reference = [], []
    tolerance = config.get("pitch_tolerance", 0.0)
    with open(tracking_path) as handle:
        for expected, line in enumerate(handle):
            row = json.loads(line)
            if row["frame"] != expected:
                raise ValueError("frame mismatch at tracking row {}".format(expected))
            expected_period = next((half for half, first, last in blocks
                                    if first <= expected <= last), None)
            if row["period"] != expected_period:
                raise ValueError("period mismatch at frame {}".format(expected))
            poss = row["possession"]
            side = {None: None, "home team": "H", "away team": "A"}.get(
                poss["group"], "invalid")
            if side == "invalid":
                raise ValueError("unknown provider possession group")
            player_id = poss["player_id"]
            if player_id is not None and (side is None or
                                          side_by_id.get(player_team.get(player_id)) != side):
                raise ValueError("possession player team mismatch at frame {}".format(expected))
            reference.append(side)
            ball = _point(row["ball_data"])
            outside = ball is not None and (abs(ball[0]) > length * (0.5 + tolerance)
                                            or abs(ball[1]) > width * (0.5 + tolerance))
            closest = {"H": math.inf, "A": math.inf}
            seen = 0
            for player in row["player_data"]:
                xy = _point(player)
                if xy is None:
                    continue
                player_side = side_by_id.get(player_team.get(player["player_id"]))
                if player_side is None:
                    raise ValueError("unknown tracked player team at frame {}".format(expected))
                seen += 1
                if ball is not None:
                    closest[player_side] = min(closest[player_side], math.dist(xy, ball))
            candidate = None
            if ball is not None and not outside:
                winner = "H" if closest["H"] < closest["A"] else "A"
                loser = "A" if winner == "H" else "H"
                if (closest[winner] <= config["control_distance_m"]
                        and closest[loser] - closest[winner] >= config["opponent_margin_m"]):
                    candidate = winner
            normalized = ((ball[0] / length + 0.5, ball[1] / width + 0.5)
                          if ball is not None else None)
            evidence.append({"candidate": candidate, "outside": outside,
                             "ball_seen": ball is not None, "ball_xy": normalized,
                             "players_seen": seen, "stationary_set_piece": False,
                             "nearest_distance_m": closest})
    missing_terminal = blocks[-1][2] + 1 - len(evidence)
    if missing_terminal > 1:
        raise ValueError("tracking ends before last period end frame")
    if missing_terminal == 1:
        blocks[-1] = (blocks[-1][0], blocks[-1][1], len(evidence) - 1)
    match["_tracking_audit"] = {"missing_terminal_frames": max(0, missing_terminal)}
    return evidence, blocks, reference, match


def compare_labels(labels, reference):
    """Count model agreement on provider H/A frames; exclude missing references."""
    if len(labels) != len(reference):
        raise ValueError("prediction/reference length mismatch")
    confusion = {team: {label: 0 for label in "HADX"} for team in "HA"}
    for prediction, target in zip(labels, reference):
        if prediction not in ("H", "A", "D", "X"):
            raise ValueError("invalid model label")
        if target in ("H", "A"):
            confusion[target][prediction] += 1
        elif target is not None:
            raise ValueError("invalid provider reference")
    eligible = sum(sum(row.values()) for row in confusion.values())
    covered = sum(confusion[team][label] for team in "HA" for label in "HA")
    matches = confusion["H"]["H"] + confusion["A"]["A"]
    return {"reference_team_frames": eligible,
            "reference_missing_frames": len(reference) - eligible,
            "team_prediction_frames": covered,
            "matching_team_frames": matches,
            "agreement_all_reference": matches / eligible if eligible else None,
            "agreement_when_team_predicted": matches / covered if covered else None,
            "team_prediction_coverage": covered / eligible if eligible else None,
            "confusion": confusion}


def load_phase_reference(path, match, frame_count, audit=None):
    """Map provider in-play phase intervals to H/A; gaps remain unknown.

    SkillCorner phase CSV end frames are exclusive, unlike match-period end
    frames. A missing phase does not prove dead ball or missing play.
    """
    reference = [None] * frame_count
    sides = {match["home_team"]["id"]: "H", match["away_team"]["id"]: "A"}
    periods = {period["period"]: (period["start_frame"], period["end_frame"])
               for period in match["match_periods"]}
    if audit is not None:
        audit.update({"excluded_cross_period_phases": 0,
                      "excluded_cross_period_frames": 0})
    with open(path, newline="") as handle:
        for phase in csv.DictReader(handle):
            if int(phase["match_id"]) != match["id"]:
                raise ValueError("phase match ID mismatch")
            period = int(phase["period"])
            start, end = int(phase["frame_start"]), int(phase["frame_end"])
            team = sides.get(int(phase["team_in_possession_id"]))
            if period not in periods or team is None:
                raise ValueError("unknown phase period or team")
            period_start, period_last = periods[period]
            if start >= end:
                raise ValueError("invalid phase range")
            if start < period_start or end > period_last + 1:
                # Some provider rows extend through a half break. Exclude the
                # entire ambiguous phase, recording the omission explicitly.
                if audit is not None:
                    audit["excluded_cross_period_phases"] += 1
                    audit["excluded_cross_period_frames"] += end - start
                continue
            for frame in range(start, end):
                if reference[frame] is not None:
                    raise ValueError("overlapping phases at frame {}".format(frame))
                reference[frame] = team
    return reference


def evaluate_match(metadata_path, tracking_path, phase_path, config):
    """Return aggregate provider agreement for one closed external match."""
    evidence, blocks, reference, match = load_match(metadata_path, tracking_path, config)
    if match["status"] != "closed":
        raise ValueError("external match is not closed")
    labels, _ = infer(evidence, blocks, scale_config(config, 10))
    instant = [row["candidate"] or "X" for row in evidence]
    phase_audit = {}
    phase_reference = load_phase_reference(phase_path, match, len(evidence),
                                           audit=phase_audit)
    transitions = sum(labels[frame] != labels[frame - 1]
                      and labels[frame] in ("H", "A")
                      and labels[frame - 1] in ("H", "A")
                      for _, first, last in blocks
                      for frame in range(first + 1, last + 1))

    def digest(path):
        sha = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                sha.update(chunk)
        return sha.hexdigest()

    return {"id": match["id"], "date": match["date_time"].split("T")[0],
            "home": match["home_team"]["name"], "away": match["away_team"]["name"],
            "fps": 10, "frames": len(evidence), "period_blocks": blocks,
            "metadata_sha256": digest(metadata_path), "tracking_sha256": digest(tracking_path),
            "phase_sha256": digest(phase_path),
            "phase_audit": phase_audit,
            "tracking_audit": match["_tracking_audit"],
            "ball_position_frames": sum(row["ball_seen"] for row in evidence),
            "player_position_frames": sum(row["players_seen"] > 0 for row in evidence),
            "home_away_transitions": transitions,
            "temporal_labels": dict(Counter(labels)),
            "temporal": compare_labels(labels, reference),
            "instantaneous_proximity": compare_labels(instant, reference),
            "live_phase": compare_labels(labels, phase_reference),
            "instantaneous_live_phase": compare_labels(instant, phase_reference)}
