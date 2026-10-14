import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_powerbi import build_powerbi
from validate_powerbi import validate_powerbi

class PowerBITests(unittest.TestCase):
    def test_native_project_and_bindings(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)
            build_powerbi(root/"data",output)
            validate_powerbi(output)
            report=output/"FinancialPerformance.Report/definition"
            pages=json.loads((report/"pages/pages.json").read_text(encoding="utf-8"))
            self.assertEqual(pages["pageOrder"],["executive","budget","buildup","drivers","monthly","forecast","areas"])
            visuals=list(report.glob("pages/*/visuals/*/visual.json"))
            self.assertGreaterEqual(len(visuals),15)
            for visual in visuals:
                obj=json.loads(visual.read_text(encoding="utf-8"))
                self.assertLessEqual(obj["position"]["x"]+obj["position"]["width"],1280)
                self.assertLessEqual(obj["position"]["y"]+obj["position"]["height"],720)
            self.assertIn("DIVIDE", (output/"measures.dax").read_text(encoding="utf-8"))
            self.assertIn("DATEADD", (output/"measures.dax").read_text(encoding="utf-8"))
            self.assertNotIn("C:\\Users", "".join(p.read_text(encoding="utf-8") for p in output.rglob("*.tmdl")))
