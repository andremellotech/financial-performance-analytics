import json
from pathlib import Path
from jsonschema import Draft7Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]

def validate_powerbi(output_dir):
    resources=[];schemas={}
    schema_root=ROOT/"docs/schemas"
    for file in schema_root.rglob("*.json"):
        obj=json.loads(file.read_text(encoding="utf-8"));uri=obj["$id"]
        file_uri="https://developer.microsoft.com/json-schemas/"+file.relative_to(schema_root).as_posix()
        schemas[file_uri]=obj;resources.append((file_uri,Resource.from_contents(obj)))
        if uri==file_uri:schemas[uri]=obj
    registry=Registry().with_resources(resources)
    out=Path(output_dir)
    for file in out.rglob("*"):
        if file.suffix not in (".json",".pbip",".pbism",".pbir"):continue
        obj=json.loads(file.read_text(encoding="utf-8"))
        uri=obj.get("$schema")
        if uri not in schemas:raise ValueError(f"Schema não encontrado: {file}: {uri}")
        errors=list(Draft7Validator(schemas[uri],registry=registry).iter_errors(obj))
        if errors:raise ValueError(f"{file}: {errors[0].message}")
    project=json.loads((out/"FinancialPerformance.pbip").read_text(encoding="utf-8"))
    report=out/project["artifacts"][0]["report"]["path"]
    model=(report/json.loads((report/"definition.pbir").read_text(encoding="utf-8"))["datasetReference"]["byPath"]["path"]).resolve()
    if not (model/"definition.pbism").exists():raise ValueError("Referência de modelo inválida.")
    from build_powerbi import TABLES, MEASURES, AUX_COLUMNS
    for file in report.glob("definition/pages/*/visuals/*/visual.json"):
        obj=json.loads(file.read_text(encoding="utf-8"))
        for role in obj["visual"].get("query",{}).get("queryState",{}).values():
            for p in role["projections"]:
                key,value=next(iter(p["field"].items()))
                table=value["Expression"]["SourceRef"]["Entity"];prop=value["Property"]
                valid=MEASURES if key=="Measure" and table=="Financas" else AUX_COLUMNS[table] if table in AUX_COLUMNS else [c[1] for c in TABLES[table][1]]
                if prop not in valid:raise ValueError(f"Campo desconhecido: {table}.{prop}")
    print("Esquemas Microsoft e referências de campos válidos.")

if __name__=="__main__":validate_powerbi(ROOT/"powerbi")
