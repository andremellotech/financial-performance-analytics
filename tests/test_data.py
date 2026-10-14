import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generate_data import generate_rows, dimensions
from finance import validate_rows, summarize, monthly_summary

class DataTests(unittest.TestCase):
    def test_complete_reproducible_data(self):
        rows = generate_rows()
        self.assertEqual(rows, generate_rows())
        self.assertEqual(len(rows), 864)
        validate_rows(rows)
        dims = dimensions()
        self.assertEqual(len(dims["calendar"]), 731)
        self.assertEqual(len(dims["areas"]), 3)
        self.assertEqual(len(dims["categories"]), 6)
        self.assertEqual(dims["calendar"][0]["date"], "2024-01-01")
        self.assertEqual(dims["calendar"][-1]["date"], "2025-12-31")
    def test_invalid_data_is_rejected(self):
        for mutation in ("duplicate", "scenario", "area", "month", "amount"):
            rows = deepcopy(generate_rows())
            if mutation == "duplicate": rows[-1] = dict(rows[0])
            if mutation == "scenario": rows[0]["scenario"] = "Outro"
            if mutation == "area": rows[0]["area_id"] = "UNKNOWN"
            if mutation == "month": rows.pop()
            if mutation == "amount": rows[0]["amount_brl"] = "NaN"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_rows(rows)

class FinanceTests(unittest.TestCase):
    def fixture(self):
        return [
            dict(month="2025-01-01", area_id="ANA", category_id=cat, scenario=sc, amount_brl=amount)
            for cat, sc, amount in [("REV","Orçado","100.00"),("PES","Orçado","-60.00"),
                                    ("REV","Realizado","90.00"),("PES","Realizado","-65.00")]
        ]
    def test_known_result_and_expense_sign(self):
        s = summarize(self.fixture(), 2025, "ANA")
        self.assertEqual(s["budget"]["result"], 40)
        self.assertEqual(s["actual"]["result"], 25)
        self.assertEqual(s["actual"]["expenses"], 65)
        self.assertEqual(s["variance"], -15)
        self.assertAlmostEqual(s["variance_pct"], -.375)
        self.assertAlmostEqual(s["actual"]["margin"], 25/90)
    def test_zero_denominators_and_missing_prior(self):
        rows = self.fixture()
        for row in rows:
            if row["scenario"] == "Orçado": row["amount_brl"] = "0.00"
            if row["category_id"] == "REV": row["amount_brl"] = "0.00"
        s = summarize(rows, 2025)
        self.assertIsNone(s["variance_pct"])
        self.assertIsNone(s["actual"]["margin"])
        self.assertIsNone(s["yoy_pct"])
        self.assertIsNone(summarize(generate_rows(), 2024)["yoy_pct"])
    def test_filter_and_monthly_reconciliation(self):
        rows = generate_rows()
        for year in (2024, 2025):
            total = summarize(rows, year)
            self.assertAlmostEqual(total["actual"]["result"], sum(summarize(rows, year, a)["actual"]["result"] for a in ("ANA","ENG","OPS")), places=2)
            self.assertAlmostEqual(total["actual"]["result"], sum(m["actual"]["result"] for m in monthly_summary(rows, year)), places=2)
        self.assertIsNotNone(summarize(rows, 2025, "ANA")["yoy_pct"])
    def test_unknown_filter_does_not_look_like_zero(self):
        with self.assertRaises(ValueError):
            summarize(generate_rows(), 2026)
        with self.assertRaises(ValueError):
            summarize(generate_rows(), 2025, "BAD")
