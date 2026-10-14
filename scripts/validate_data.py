from pathlib import Path
from finance import load_rows,validate_rows,summarize
ROOT=Path(__file__).resolve().parents[1]
def validate_dataset(folder):
    folder=Path(folder);rows=load_rows(folder/"fact_finance.csv");validate_rows(rows)
    from generate_data import dimensions
    dims=dimensions()
    for key,name in (("areas","dim_area"),("categories","dim_category"),("calendar","dim_calendar")):
        actual=load_rows(folder/(name+".csv"));expected=dims[key];fields=list(expected[0])
        if any(set(row)!=set(fields) for row in actual):
            raise ValueError(f"{name}: colunas incompatíveis.")
        expected_keys={tuple(str(row[f]) for f in fields) for row in expected}
        actual_keys={tuple(str(row[f]) for f in fields) for row in actual}
        if len(actual)!=len(expected) or actual_keys!=expected_keys:
            raise ValueError(f"{name}: cobertura, chaves ou rótulos incompatíveis.")
    return rows
if __name__=="__main__":
    rows=validate_dataset(ROOT/"data")
    s=summarize(rows,2025)
    print(f"864 registros válidos. Resultado realizado 2025: R$ {s['actual']['result']:,.2f}; desvio: R$ {s['variance']:,.2f}")
