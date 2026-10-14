import sys, unittest
from pathlib import Path
from copy import deepcopy
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import finance
from generate_data import generate_rows

class ScenarioTests(unittest.TestCase):
    def forecast(self, *args):
        self.assertTrue(callable(getattr(finance, 'scenario_projection', None)), 'Falta forecast com premissas')
        return finance.scenario_projection(*args)

    def test_base_and_december_preserve_existing_eac(self):
        rows = generate_rows()
        for cut in (1, 9, 12):
            base = self.forecast(rows, 2025, cut)
            self.assertEqual(base['eac'], finance.projection_summary(rows, 2025, cut)['eac'])
        adjusted = self.forecast(rows, 2025, 12, None, .05, -.03)
        self.assertEqual(adjusted['eac'], finance.summarize(rows, 2025)['actual'])

    def test_only_future_budget_is_adjusted_and_sources_are_preserved(self):
        rows = generate_rows(); before = deepcopy(rows)
        base = finance.projection_summary(rows, 2025, 9)
        p = self.forecast(rows, 2025, 9, None, .05, -.03)
        self.assertEqual(p['actual_to_date'], base['actual_to_date'])
        self.assertGreater(p['eac']['revenue'], base['eac']['revenue'])
        self.assertLess(p['eac']['expenses'], base['eac']['expenses'])
        self.assertEqual(rows, before)
        for r in rows:
            if r['scenario'] == 'Realizado' and r['month'] > '2025-09-01': r['amount_brl'] = '0.00'
        self.assertEqual(self.forecast(rows, 2025, 9, None, .05, -.03)['eac'], p['eac'])

    def test_months_categories_and_variance_reconcile_all_cases(self):
        rows = generate_rows()
        for year in (2024, 2025):
            for area in (None, 'ANA', 'ENG', 'OPS'):
                for cut in range(1, 13):
                    for revenue, expenses in ((0, 0), (.05, -.03), (-.05, .03)):
                        p = self.forecast(rows, year, cut, area, revenue, expenses)
                        for key in ('revenue', 'expenses', 'result'):
                            self.assertAlmostEqual(sum(m['active'][key] for m in p['monthly']), p['eac'][key], places=2)
                        self.assertAlmostEqual(sum(c['eac'] for c in p['categories']), p['eac']['result'], places=2)
                        self.assertAlmostEqual(p['expense_savings'] - p['expense_overruns'], p['expense_variance'], places=2)

    def test_invalid_and_zero_inputs(self):
        rows = generate_rows(); self.forecast(rows, 2025, 9)
        for rate in (float('nan'), float('inf'), None, True, -1.01, 1.01, '5'):
            with self.assertRaises(ValueError): finance.scenario_projection(rows, 2025, 9, None, rate, 0)
        for r in rows:
            if r['category_id'] == 'REV': r['amount_brl'] = '0.00'
        self.assertIsNone(self.forecast(rows, 2025, 9, None, .05, -.03)['eac']['margin'])
