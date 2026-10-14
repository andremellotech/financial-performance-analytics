import sys,unittest
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import finance
from generate_data import generate_rows

class ProjectionTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for month,values in [(1,[("REV","Orçado","100.00"),("PES","Orçado","-60.00"),("REV","Realizado","90.00"),("PES","Realizado","-65.00")]),(2,[("REV","Orçado","200.00"),("PES","Orçado","-100.00"),("REV","Realizado","999.00"),("PES","Realizado","-999.00")])]:
            rows.extend(dict(month=f'2025-{month:02d}-01',area_id='ANA',category_id=c,scenario=s,amount_brl=v) for c,s,v in values)
        return rows
    def projection(self,*args):
        self.assertTrue(callable(getattr(finance,'projection_summary',None)),'Falta o cálculo do EAC')
        return finance.projection_summary(*args)
    def test_known_eac_and_signed_category_impacts(self):
        p=self.projection(self.fixture(),2025,1,'ANA')
        self.assertEqual(p['actual_to_date']['result'],25)
        self.assertEqual(p['remaining']['result'],100)
        self.assertEqual(p['eac']['revenue'],290)
        self.assertEqual(p['eac']['expenses'],165)
        self.assertEqual(p['eac']['result'],125)
        self.assertAlmostEqual(p['eac']['margin'],125/290)
        self.assertEqual(p['variance'],-15)
        self.assertEqual(sum(c['variance'] for c in p['categories']),-15)
        self.assertEqual(p['expense_savings'],0)
        self.assertEqual(p['expense_overruns'],5)
        self.assertEqual(p['expense_variance'],-5)
    def test_future_actuals_never_leak_into_projection(self):
        rows=generate_rows();expected=self.projection(rows,2025,9)
        changed=deepcopy(rows)
        for r in changed:
            if r['month']>'2025-09-01' and r['scenario']=='Realizado':r['amount_brl']='0.00'
        actual=self.projection(changed,2025,9)
        for key in ('eac','remaining','categories','variance'):
            self.assertEqual(actual[key],expected[key])
    def test_december_is_actual_and_categories_reconcile_all_cuts(self):
        rows=generate_rows()
        for year in (2024,2025):
            for area in (None,'ANA','ENG','OPS'):
                for month in range(1,13):
                    p=self.projection(rows,year,month,area)
                    self.assertAlmostEqual(sum(c['eac'] for c in p['categories']),p['eac']['result'],places=2)
                    self.assertAlmostEqual(p['expense_savings']-p['expense_overruns'],p['expense_variance'],places=2)
                self.assertEqual(p['eac'],finance.summarize(rows,year,area)['actual'])
                self.assertEqual(p['remaining']['result'],0)
    def test_invalid_cuts_and_zero_denominators(self):
        self.projection(self.fixture(),2025,1)
        for cut in (0,13,1.5,True):
            with self.assertRaises(ValueError):finance.projection_summary(self.fixture(),2025,cut)
        with self.assertRaises(ValueError):finance.projection_summary(self.fixture(),2026,1)
        rows=self.fixture()
        for r in rows:
            if r['category_id']=='REV':r['amount_brl']='0.00'
        self.assertIsNone(self.projection(rows,2025,1)['eac']['margin'])
    def test_month_and_ytd_have_separate_scopes(self):
        self.assertTrue(callable(getattr(finance,'period_summary',None)),'Falta o recorte mensal/acumulado')
        m=finance.period_summary(self.fixture(),2025,2,'ANA')
        self.assertEqual(m['month']['budget']['result'],100)
        self.assertEqual(m['month']['actual']['result'],0)
        self.assertEqual(m['ytd']['actual']['result'],25)
        self.assertEqual(m['ytd']['budget']['result'],140)
