"""Regras financeiras de referência, independentes de Power BI e Excel."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import csv

AREAS = {"ANA": "Analytics", "ENG": "Engenharia", "OPS": "Operações"}
CATEGORIES = {"REV": "Receita de serviços", "DIR": "Custos diretos", "PES": "Pessoal",
              "TEC": "Tecnologia", "COM": "Comercial", "ADM": "Administrativo"}
SCENARIOS = ("Orçado", "Realizado")
MONTHS = [f"{y}-{m:02d}-01" for y in (2024, 2025) for m in range(1, 13)]
FIELDS = ["month", "area_id", "category_id", "scenario", "amount_brl"]

def load_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))

def validate_rows(rows):
    expected = {(m,a,c,s) for m in MONTHS for a in AREAS for c in CATEGORIES for s in SCENARIOS}
    seen = set()
    for index, row in enumerate(rows, 2):
        if set(row) != set(FIELDS):
            raise ValueError(f"Linha {index}: colunas incompatíveis.")
        key = tuple(row[f] for f in FIELDS[:4])
        if key not in expected:
            raise ValueError(f"Linha {index}: mês, área, categoria ou cenário desconhecido: {key}.")
        if key in seen:
            raise ValueError(f"Linha {index}: chave duplicada: {key}.")
        seen.add(key)
        try:
            value = Decimal(row["amount_brl"])
        except (InvalidOperation, TypeError):
            raise ValueError(f"Linha {index}: valor inválido.") from None
        if not value.is_finite() or value.as_tuple().exponent != -2:
            raise ValueError(f"Linha {index}: use um valor finito com duas casas decimais.")
        if (row["category_id"] == "REV" and value < 0) or (row["category_id"] != "REV" and value > 0):
            raise ValueError(f"Linha {index}: sinal incompatível com a categoria.")
    if seen != expected:
        raise ValueError(f"Cobertura incompleta: faltam {len(expected - seen)} combinações.")

def _scenario(rows):
    if not rows:
        return {"revenue": None, "expenses": None, "result": None, "margin": None}
    revenue = sum((Decimal(r["amount_brl"]) for r in rows if r["category_id"] == "REV"), Decimal(0))
    expenses = -sum((Decimal(r["amount_brl"]) for r in rows if r["category_id"] != "REV"), Decimal(0))
    result = revenue - expenses
    return {"revenue": float(revenue), "expenses": float(expenses), "result": float(result),
            "margin": float(result / revenue) if revenue else None}

def summarize(rows, year=None, area_id=None):
    if area_id is not None and area_id not in AREAS:
        raise ValueError(f"Área desconhecida: {area_id}")
    available = {int(r["month"][:4]) for r in rows}
    if year is not None and year not in available:
        raise ValueError(f"Ano sem dados: {year}")
    selected = [r for r in rows if (year is None or int(r["month"][:4]) == year)
                and (area_id is None or r["area_id"] == area_id)]
    budget = _scenario([r for r in selected if r["scenario"] == "Orçado"])
    actual = _scenario([r for r in selected if r["scenario"] == "Realizado"])
    variance = round(actual["result"] - budget["result"], 2) if actual["result"] is not None and budget["result"] is not None else None
    prior = None
    if year is not None:
        prior = _scenario([r for r in rows if int(r["month"][:4]) == year-1
                           and (area_id is None or r["area_id"] == area_id) and r["scenario"] == "Realizado"])["result"]
    return {"year": year, "area_id": area_id, "budget": budget, "actual": actual, "variance": variance,
            "variance_pct": variance / abs(budget["result"]) if budget["result"] else None,
            "prior_result": prior, "yoy_pct": (actual["result"]-prior)/abs(prior) if prior else None}

def monthly_summary(rows, year, area_id=None):
    result = []
    for month in range(1,13):
        current = [r for r in rows if r["month"] == f"{year}-{month:02d}-01"
                   and (area_id is None or r["area_id"] == area_id)]
        # Full-year source is retained for valid filter checks; month metrics use only matching rows.
        s = summarize(current, year, area_id)
        s["month"] = f"{year}-{month:02d}"
        result.append(s)
    return result

def category_variances(rows, year=2025, area_id=None):
    result=[]
    for key,label in CATEGORIES.items():
        values={}
        for scenario in SCENARIOS:
            values[scenario]=sum((Decimal(r["amount_brl"]) for r in rows
                                 if int(r["month"][:4])==year and r["category_id"]==key
                                 and r["scenario"]==scenario and (area_id is None or r["area_id"]==area_id)),Decimal(0))
        result.append({"category_id":key,"label":label,"budget":float(values["Orçado"]),
                       "actual":float(values["Realizado"]),"variance":float(values["Realizado"]-values["Orçado"])})
    return result

def _check_cut(month):
    if type(month) is not int or not 1<=month<=12:
        raise ValueError("Mês de referência deve ser um inteiro de 1 a 12.")

def period_summary(rows,year,month,area_id=None):
    _check_cut(month);summarize(rows,year,area_id)
    return {"year":year,"cutoff":month,"area_id":area_id,
        "month":summarize([r for r in rows if int(r['month'][5:7])==month],year,area_id),
        "ytd":summarize([r for r in rows if int(r['month'][5:7])<=month],year,area_id)}

def projection_summary(rows,year,cutoff,area_id=None):
    """EAC hipotético: realizado até corte + orçamento restante; sem olhar realizado futuro."""
    _check_cut(cutoff);annual=summarize(rows,year,area_id)
    selected=[r for r in rows if int(r['month'][:4])==year and (area_id is None or r['area_id']==area_id)]
    actual=[r for r in selected if r['scenario']=='Realizado' and int(r['month'][5:7])<=cutoff]
    remaining=[r for r in selected if r['scenario']=='Orçado' and int(r['month'][5:7])>cutoff]
    zero={"revenue":0.0,"expenses":0.0,"result":0.0,"margin":None}
    categories=[]
    for key,label in CATEGORIES.items():
        def total(source):return sum((Decimal(r['amount_brl']) for r in source if r['category_id']==key),Decimal(0))
        b=total([r for r in selected if r['scenario']=='Orçado']);a=total(actual);p=total(remaining)
        categories.append({"category_id":key,"label":label,"budget":float(b),"actual_to_date":float(a),"remaining":float(p),"eac":float(a+p),"variance":float(a+p-b)})
    eac=_scenario(actual+remaining);variance=round(eac['result']-annual['budget']['result'],2)
    costs=[c for c in categories if c['category_id']!='REV']
    return {"year":year,"cutoff":cutoff,"area_id":area_id,"budget":annual['budget'],
        "actual_to_date":_scenario(actual) if actual else dict(zero),"remaining":_scenario(remaining) if remaining else dict(zero),"eac":eac,
        "variance":variance,"variance_pct":variance/abs(annual['budget']['result']) if annual['budget']['result'] else None,
        "expense_variance":round(annual['budget']['expenses']-eac['expenses'],2),
        "expense_savings":round(sum(max(c['variance'],0) for c in costs),2),
        "expense_overruns":round(sum(max(-c['variance'],0) for c in costs),2),"categories":categories}

def scenario_projection(rows, year, cutoff, area_id=None, revenue_change=0, expense_change=0):
    """Ajusta somente o orçamento futuro; arredonda cada categoria/mês ao centavo."""
    for rate in (revenue_change, expense_change):
        if type(rate) not in (int, float) or not Decimal(str(rate)).is_finite() or not -1 <= rate <= 1:
            raise ValueError('Premissas devem ser números entre -100% e 100%.')
    p = projection_summary(rows, year, cutoff, area_id)
    selected = [r for r in rows if int(r['month'][:4]) == year and (area_id is None or r['area_id'] == area_id)]
    future = []
    monthly = []
    for month in range(1, 13):
        current = [r for r in selected if int(r['month'][5:7]) == month]
        budget = [r for r in current if r['scenario'] == 'Orçado']
        projected = []
        if month > cutoff:
            for key in CATEGORIES:
                amount = sum((Decimal(r['amount_brl']) for r in budget if r['category_id'] == key), Decimal(0))
                factor = 1 + Decimal(str(revenue_change if key == 'REV' else expense_change))
                projected.append({'category_id': key, 'amount_brl': str((amount * factor).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))})
            future.extend(projected)
        active = _scenario([r for r in current if r['scenario'] == 'Realizado'] if month <= cutoff else projected)
        monthly.append({'month': month, 'budget': _scenario(budget), 'active': active, 'origin': 'Realizado' if month <= cutoff else 'Projetado'})
    zero = {'revenue': 0.0, 'expenses': 0.0, 'result': 0.0, 'margin': None}
    actual = [r for r in selected if r['scenario'] == 'Realizado' and int(r['month'][5:7]) <= cutoff]
    p['remaining'] = _scenario(future) if future else dict(zero)
    p['eac'] = _scenario(actual + future)
    for c in p['categories']:
        remaining = sum((Decimal(r['amount_brl']) for r in future if r['category_id'] == c['category_id']), Decimal(0))
        total = Decimal(str(c['actual_to_date'])) + remaining
        c.update(remaining=float(remaining), eac=float(total), variance=float(total - Decimal(str(c['budget']))))
    p['variance'] = round(p['eac']['result'] - p['budget']['result'], 2)
    p['variance_pct'] = p['variance'] / abs(p['budget']['result']) if p['budget']['result'] else None
    p['expense_variance'] = round(p['budget']['expenses'] - p['eac']['expenses'], 2)
    costs = [c for c in p['categories'] if c['category_id'] != 'REV']
    p['expense_savings'] = round(sum(max(c['variance'], 0) for c in costs), 2)
    p['expense_overruns'] = round(sum(max(-c['variance'], 0) for c in costs), 2)
    p.update(revenue_change=revenue_change, expense_change=expense_change, monthly=monthly)
    return p
