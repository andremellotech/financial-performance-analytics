"""Gera a base fictícia determinística. Uso: python scripts/generate_data.py"""
import argparse
import csv
import json
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from finance import AREAS, CATEGORIES, MONTHS, FIELDS, validate_rows, summarize, monthly_summary, category_variances

ROOT = Path(__file__).resolve().parents[1]
SEASONALITY = [.90,.94,1.00,1.02,1.05,1.01,.98,1.00,1.06,1.10,1.12,.96]
RATIOS = {"DIR":.22,"PES":.30,"TEC":.07,"COM":.055,"ADM":.065}

def money(value):
    return f"{Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP):.2f}"

def generate_rows(seed=42):
    rng=random.Random(seed);rows=[]
    for month in MONTHS:
        year=int(month[:4]);m=int(month[5:7])
        for area,base in {"ANA":230000,"ENG":320000,"OPS":180000}.items():
            planned=base*(1.12 if year==2025 else 1)*SEASONALITY[m-1]
            revenue_factor=1+rng.uniform(-.025,.025)
            if year==2025 and area=="ENG" and 6<=m<=10:revenue_factor-=.12
            if year==2025 and area=="ANA" and 7<=m<=9:revenue_factor-=.08
            if year==2025 and area=="OPS":revenue_factor-=.015
            for category in CATEGORIES:
                budget=planned if category=="REV" else -planned*RATIOS[category]
                if category=="REV":actual=planned*revenue_factor
                elif category=="DIR":actual=budget*revenue_factor*(1+rng.uniform(-.02,.025))
                else:
                    multiplier=1+rng.uniform(-.02,.03)
                    if year==2025 and category=="TEC" and m>=3:multiplier+=.18
                    if year==2025 and category=="PES" and area=="ENG" and m>=7:multiplier+=.08
                    if year==2025 and category=="COM" and area=="ANA" and m>=10:multiplier+=.20
                    actual=budget*multiplier
                for scenario,value in (("Orçado",budget),("Realizado",actual)):
                    rows.append(dict(month=month,area_id=area,category_id=category,scenario=scenario,amount_brl=money(value)))
    return rows

def dimensions():
    calendar=[];current=date(2024,1,1)
    names=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    while current<=date(2025,12,31):
        calendar.append(dict(date=current.isoformat(),year=current.year,month=current.month,month_name=names[current.month-1],year_month=current.strftime("%Y-%m"),year_month_order=current.year*100+current.month))
        current+=timedelta(days=1)
    return {"areas":[dict(area_id=k,area_name=v) for k,v in AREAS.items()],
            "categories":[dict(category_id=k,category_name=v,nature="Receita" if k=="REV" else "Despesa",sort_order=i) for i,(k,v) in enumerate(CATEGORIES.items(),1)],"calendar":calendar}

def write_csv(path,rows,fields=None):
    with path.open("w",encoding="utf-8",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=fields or list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def build_data(output):
    output.mkdir(parents=True,exist_ok=True)
    rows=generate_rows();validate_rows(rows);dims=dimensions()
    write_csv(output/"fact_finance.csv",rows,FIELDS)
    for key,name in (("areas","dim_area"),("categories","dim_category"),("calendar","dim_calendar")):
        write_csv(output/f"{name}.csv",dims[key])
    from refresh_dashboard import refresh_dashboard
    refresh_dashboard(output)
    print(f"Base válida: {len(rows)} registros; {len(dims['calendar'])} datas.")

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=ROOT/"data")
    build_data(parser.parse_args().output)
