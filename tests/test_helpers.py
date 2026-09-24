import unittest
import numpy as np
from portfolio_management.utils.helpers import compute_simulation_metrics, convert_time_steps_to_dates

class TestSimulationMetrics(unittest.TestCase):
    def test_metrics_on_known_values(self):
        finals = np.arange(901, 1101, dtype=float)  # 200 outcomes: 99 below 1000, one equal, 100 above
        m = compute_simulation_metrics(finals, 1000)
        self.assertAlmostEqual(m['mean'], finals.mean())
        self.assertAlmostEqual(m['median'], np.median(finals))
        self.assertAlmostEqual(m['prob_loss'], 99 / 200 * 100)
        self.assertAlmostEqual(m['var_95'], 1000 - np.percentile(finals, 5))
        self.assertGreaterEqual(m['cvar_95'], m['var_95'], "CVaR averages the tail, so it is at least VaR")

    def test_constant_outcomes_do_not_divide_by_zero(self):
        m = compute_simulation_metrics(np.full(50, 1000.0), 1000)
        self.assertEqual(m['sharpe'], 0.0)
        self.assertEqual(m['prob_loss'], 0.0)

    def test_convert_time_steps_to_dates(self):
        self.assertEqual(convert_time_steps_to_dates('2024-01-30', [0, 1, 2]), ['2024-01-30', '2024-01-31', '2024-02-01'])

if __name__ == '__main__':
    unittest.main()
