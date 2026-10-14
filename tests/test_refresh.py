import json,re,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from generate_data import build_data,write_csv
from finance import load_rows,summarize
from build_preview import build_preview
import build_docs
ROOT=Path(__file__).resolve().parents[1]

class RefreshTests(unittest.TestCase):
    def test_preview_refresh_reads_changed_valid_csv(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_data(root/"data")
            shutil.copytree(ROOT/"preview",root/"preview")
            shutil.copytree(ROOT/"scripts/templates",root/"scripts/templates")
            rows=load_rows(root/"data/fact_finance.csv")
            row=next(r for r in rows if r["month"]=="2025-01-01" and r["area_id"]=="ANA" and r["category_id"]=="REV" and r["scenario"]=="Realizado")
            row["amount_brl"]="100000.00";write_csv(root/"data/fact_finance.csv",rows)
            build_preview(root)
            html=(root/"preview/index.html").read_text(encoding="utf-8")
            payload=json.loads(re.search(r'<script id="dataset" type="application/json">(.*?)</script>',html,re.S)[1])
            self.assertEqual(summarize(payload["rows"],2025)["actual"]["revenue"],summarize(rows,2025)["actual"]["revenue"])
    def test_docs_handle_zero_revenue_and_zero_variance(self):
        for case in ("zero_revenue","zero_variance"):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
                root=Path(d);build_data(root/"data")
                rows=load_rows(root/"data/fact_finance.csv")
                budgets={(r["month"],r["area_id"],r["category_id"]):r["amount_brl"] for r in rows if r["scenario"]=="Orçado"}
                for row in rows:
                    if case=="zero_revenue" and row["category_id"]=="REV":row["amount_brl"]="0.00"
                    if case=="zero_variance" and row["scenario"]=="Realizado":row["amount_brl"]=budgets[(row["month"],row["area_id"],row["category_id"])]
                write_csv(root/"data/fact_finance.csv",rows)
                with patch.object(build_docs,"ROOT",root):build_docs.build_docs()
                text=(root/"docs/findings.md").read_text(encoding="utf-8")
                self.assertNotIn("None",text)
                self.assertNotRegex(text.lower(),r"\bnan\b")
                if case=="zero_revenue":self.assertIn("—",text)
                else:self.assertIn("zero",text)
