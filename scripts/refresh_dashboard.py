"""Atualiza os dados derivados a partir dos CSV atuais, sem gerar outra base."""
import json
from pathlib import Path
from finance import AREAS,summarize,monthly_summary,category_variances,projection_summary,period_summary,scenario_projection
from validate_data import validate_dataset
ROOT=Path(__file__).resolve().parents[1]
def refresh_dashboard(folder=ROOT/"data"):
    folder=Path(folder);rows=validate_dataset(folder)
    from generate_data import dimensions
    dims=dimensions()
    payload={"rows":rows,"areas":dims["areas"],"categories":dims["categories"],"years":[2024,2025],
             "reference":[summarize(rows,y,a) for y in (2024,2025) for a in (None,*AREAS)],
             "monthly":monthly_summary(rows,2025),"drivers":category_variances(rows),"synthetic":True,
             "projection_reference":[projection_summary(rows,y,m,a) for y in (2024,2025) for a in (None,*AREAS) for m in range(1,13)],
             "period_reference":[period_summary(rows,y,m,a) for y in (2024,2025) for a in (None,*AREAS) for m in (1,9,12)],
             "scenario_reference":[scenario_projection(rows,y,m,a,rev,cost) for y in (2024,2025) for a in (None,*AREAS) for m in range(1,13) for rev,cost in ((0,0),(.05,-.03),(-.05,.03))]}
    (folder/"dashboard.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload
if __name__=="__main__":
    refresh_dashboard()
    print("Dados derivados atualizados a partir dos CSV atuais.")
