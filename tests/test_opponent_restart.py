"""Focused safeguards for the optional opposite-team restart confirmation."""
import unittest

from model.inference import infer
from model.external_skillcorner import scale_config
from tests.test_inference import evidence


CFG = dict(control_frames=4, evidence_gap_frames=0, out_of_bounds_frames=2,
           control_backfill=True, opponent_restart_control_frames=2,
           opponent_restart_min_ball_speed_mps=.2)


class OpponentRestartTests(unittest.TestCase):
    def test_fast_opposite_team_requires_motion_and_new_control(self):
        rows = [evidence('H') for _ in range(4)]
        rows += [evidence(stationary_set_piece=True)]
        rows += [evidence('A', ball_speed_mps=0) for _ in range(2)]
        rows += [evidence('A', ball_speed_mps=1) for _ in range(2)]
        labels, _ = infer(rows, [(1, 0, 8)], CFG)
        self.assertEqual(labels, ['H']*4 + ['D']*3 + ['A']*2)

    def test_previous_team_does_not_get_fast_restore(self):
        rows = [evidence('H') for _ in range(4)]
        rows += [evidence(stationary_set_piece=True)]
        rows += [evidence('H', ball_speed_mps=1) for _ in range(2)]
        labels, _ = infer(rows, [(1, 0, 6)], CFG)
        self.assertEqual(labels, ['H']*4 + ['D']*3)

    def test_half_boundary_clears_previous_team(self):
        rows = [evidence('H') for _ in range(4)]
        rows += [evidence(stationary_set_piece=True)]
        rows += [evidence('A', ball_speed_mps=1) for _ in range(2)]
        labels, _ = infer(rows, [(1, 0, 4), (2, 5, 6)], CFG)
        self.assertEqual(labels[-2:], ['X', 'X'])

    def test_gap_breaks_fast_confirmation(self):
        rows = [evidence('H') for _ in range(4)]
        rows += [evidence(stationary_set_piece=True)]
        rows += [evidence('A', ball_speed_mps=1), evidence(ball_seen=False),
                 evidence('A', ball_speed_mps=1)]
        labels, _ = infer(rows, [(1, 0, 7)], CFG)
        self.assertEqual(labels[-3:], ['D']*3)

    def test_duration_scales_to_external_fps(self):
        self.assertEqual(scale_config(CFG, 10)['opponent_restart_control_frames'], 2)


if __name__ == '__main__':
    unittest.main()
