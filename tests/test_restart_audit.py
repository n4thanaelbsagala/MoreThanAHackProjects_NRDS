import unittest

from model.restart_audit import summarize_restarts


class RestartAuditTests(unittest.TestCase):
    def test_changed_team_and_delayed_release(self):
        reference = list('HHDDDAAAA')
        labels = list('HHDDDDHAA')
        result = summarize_restarts(reference, labels, [(1, 0, 8)], 1)
        self.assertEqual(result['events']['reference_restarts'], 1)
        self.assertEqual(result['first_live_delay_frames']['mean'], 1)
        self.assertEqual(result['reference_team_changed']['predicted_previous_team'], 1)

    def test_unknown_boundary_and_half_are_excluded(self):
        reference = list('HDDAXDDA')
        labels = list('HDDAXDDA')
        result = summarize_restarts(reference, labels, [(1, 0, 3), (2, 4, 7)], 1)
        self.assertEqual(result['events']['reference_restarts'], 1)


if __name__ == '__main__':
    unittest.main()
