import json,re,sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from validate_data import validate_dataset
from generate_data import build_data
ROOT=Path(__file__).resolve().parents[1]
NS={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

class PackageTests(unittest.TestCase):
    def test_dimensions_are_validated(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);build_data(folder);validate_dataset(folder)
            text=(folder/"dim_area.csv").read_text(encoding="utf-8")
            (folder/"dim_area.csv").write_text(text.replace("ANA","BAD"),encoding="utf-8")
            with self.assertRaises(ValueError):validate_dataset(folder)
    def test_xlsx_cached_values_formulas_and_controls(self):
        ref=json.loads((ROOT/"data/dashboard.json").read_text(encoding="utf-8"))["reference"][4]
        with zipfile.ZipFile(ROOT/"excel/FinancialPerformance.xlsx") as z:
            self.assertIsNone(z.testzip())
            sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
            for cell,key in (("C7","revenue"),("C8","expenses"),("C9","result"),("C10","margin")):
                node=sheet.find(".//s:c[@r='"+cell+"']",NS)
                self.assertIsNotNone(node.find("s:f",NS))
                self.assertAlmostEqual(float(node.find("s:v",NS).text),ref["actual"][key],places=6)
            self.assertEqual(len(sheet.findall(".//s:dataValidation",NS)),3)
            self.assertEqual(len([n for n in z.namelist() if re.search(r"/charts/chart\d+\.xml$",n)]),4)
    def test_projection_and_buildup_workbook_outputs(self):
        ref=next(r for r in json.loads((ROOT/'data/dashboard.json').read_text(encoding='utf-8'))['projection_reference'] if r['year']==2025 and r['cutoff']==9 and r['area_id'] is None)
        with zipfile.ZipFile(ROOT/'excel/FinancialPerformance.xlsx') as z:
            workbook=ET.fromstring(z.read('xl/workbook.xml'))
            self.assertEqual([s.attrib['name'] for s in workbook.findall('s:sheets/s:sheet',NS)],['Painel','Build-up','Projeção','Base'])
            projection=ET.fromstring(z.read('xl/worksheets/sheet3.xml'));buildup=ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
            def value(sheet,cell):
                node=sheet.find(".//s:c[@r='"+cell+"']",NS)
                self.assertIsNotNone(node.find('s:f',NS),cell)
                return float(node.find('s:v',NS).text)
            for cell,key in [('C7','revenue'),('C8','expenses'),('C9','result'),('C10','margin')]:self.assertAlmostEqual(value(projection,cell),ref['eac'][key],places=6)
            self.assertAlmostEqual(value(buildup,'D7'),ref['eac']['expenses'],places=2)
            self.assertAlmostEqual(value(buildup,'E7'),ref['expense_variance'],places=2)
            for i,cat in enumerate(ref['categories'],27):
                for col,key in [('B','budget'),('C','actual_to_date'),('D','remaining'),('E','eac'),('F','variance')]:self.assertAlmostEqual(value(projection,f'{col}{i}'),cat[key],places=2)
    def test_preview_is_self_contained_and_readme_links_exist(self):
        text=(ROOT/"preview/index.html").read_text(encoding="utf-8")
        self.assertNotIn("__DATA__",text)
        self.assertNotRegex(text,r"<script[^>]+src=")
        self.assertNotRegex(text,r"<link[^>]+href=")
        self.assertIn('"synthetic": true',text)
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)",readme):
            if not link.startswith(("https:","#")):self.assertTrue((ROOT/link).exists(),link)
    def test_workbook_forecast_assumptions_drive_future_months(self):
        with zipfile.ZipFile(ROOT/'excel/FinancialPerformance.xlsx') as z:
            sheet=ET.fromstring(z.read('xl/worksheets/sheet3.xml'))
            self.assertIsNotNone(sheet.find(".//s:dataValidation[@sqref='L37']",NS),'Falta seletor de cenário')
            for cell in ('L40','L46'):
                node=sheet.find(".//s:c[@r='"+cell+"']",NS)
                self.assertIsNotNone(node,'Falta premissa ativa')
                self.assertIsNotNone(node.find('s:f',NS))
            for cell,driver in (('K57','$L$40'),('K58','$L$46')):
                node=sheet.find(".//s:c[@r='"+cell+"']",NS)
                self.assertIsNotNone(node,'Falta cálculo futuro por categoria/mês')
                self.assertIn(driver,node.find('s:f',NS).text)
