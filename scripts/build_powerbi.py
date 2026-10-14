"""Gera o modelo TMDL e o relatório PBIR a partir da base validada."""
import base64
import json
from pathlib import Path
from finance import load_rows, validate_rows
ROOT=Path(__file__).resolve().parents[1]
SCHEMA="https://developer.microsoft.com/json-schemas/"
MEASURES={
 "Receita realizada":'CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Realizado", Categorias[CategoriaId] = "REV")',
 "Receita orçada":'CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Orçado", Categorias[CategoriaId] = "REV")',
 "Gastos realizados":'-CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Realizado", Categorias[Natureza] = "Despesa")',
 "Gastos orçados":'-CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Orçado", Categorias[Natureza] = "Despesa")',
 "Resultado realizado":'CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Realizado")',
 "Resultado orçado":'CALCULATE(SUM(Financas[Valor]), Financas[Cenario] = "Orçado")',
 "Margem realizada":'DIVIDE([Resultado realizado], [Receita realizada])',
 "Margem orçada":'DIVIDE([Resultado orçado], [Receita orçada])',
 "Desvio do resultado":'[Resultado realizado] - [Resultado orçado]',
 "Desvio percentual":'DIVIDE([Desvio do resultado], ABS([Resultado orçado]))',
 "Resultado ano anterior":'IF(HASONEVALUE(Calendario[Ano]), CALCULATE([Resultado realizado], DATEADD(Calendario[Data], -1, YEAR)))',
 "Variação anual":'VAR Anterior = [Resultado ano anterior] RETURN IF(NOT ISBLANK(Anterior), DIVIDE([Resultado realizado] - Anterior, ABS(Anterior)))',
}
TABLES={
 "Financas":("fact_finance.csv",[("month","Data","dateTime"),("area_id","AreaId","string"),("category_id","CategoriaId","string"),("scenario","Cenario","string"),("amount_brl","Valor","decimal")]),
 "Areas":("dim_area.csv",[("area_id","AreaId","string"),("area_name","Area","string")]),
 "Categorias":("dim_category.csv",[("category_id","CategoriaId","string"),("category_name","Categoria","string"),("nature","Natureza","string"),("sort_order","Ordem","int64")]),
 "Calendario":("dim_calendar.csv",[("date","Data","dateTime"),("year","Ano","int64"),("month","Mes","int64"),("month_name","NomeMes","string"),("year_month","AnoMes","string"),("year_month_order","OrdemAnoMes","int64")]),
}

from eac_dax import EXTRA_MEASURES,AUX_COLUMNS,cutoff_query
MEASURES.update(EXTRA_MEASURES)

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding="utf-8")
def dump(path,obj):
    write(path,json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
def schema(kind,version):
    return SCHEMA+f"fabric/item/report/definition/{kind}/{version}/schema.json"
def literal(value):
    return {"expr":{"Literal":{"Value":value}}}
def field(table,name,measure=False):
    return {("Measure" if measure else "Column"):{"Expression":{"SourceRef":{"Entity":table}},"Property":name}}
def projection(table,name,measure=False):
    return {"field":field(table,name,measure),"queryRef":f"{table}.{name}","nativeQueryRef":name}

def query_source(data_dir,filename,columns):
    encoded=base64.b64encode((data_dir/filename).read_bytes()).decode()
    types={"string":"type text","int64":"Int64.Type","dateTime":"type date","decimal":"Currency.Type"}
    casts=", ".join('{'+json.dumps(src)+", "+types[typ]+"}" for src,_,typ in columns)
    renames=", ".join('{'+json.dumps(src)+", "+json.dumps(dest)+"}" for src,dest,_ in columns)
    checks=""
    if filename=="fact_finance.csv":
        checks='''    Keys = {"month", "area_id", "category_id", "scenario"},
    ValidRows = List.AllTrue(List.Transform(Table.ToRecords(Typed), each
        Date.Day([month]) = 1 and List.Contains({2024, 2025}, Date.Year([month])) and
        List.Contains({"ANA", "ENG", "OPS"}, [area_id]) and
        List.Contains({"REV", "DIR", "PES", "TEC", "COM", "ADM"}, [category_id]) and
        List.Contains({"Orçado", "Realizado"}, [scenario]) and
        [amount_brl] <> null and Number.Round([amount_brl], 2) = [amount_brl] and
        (if [category_id] = "REV" then [amount_brl] >= 0 else [amount_brl] <= 0))),
    Checked = if Table.RowCount(Typed) = 864 and Table.RowCount(Table.Distinct(Typed, Keys)) = 864 and ValidRows
        then Typed else error "Base inválida: confira cobertura, chaves, cenários e sinais.",
'''
    else:
        count=len(load_rows(data_dir/filename))
        checks=f'''    ExpectedRaw = Csv.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64), [Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    ExpectedTyped = Table.TransformColumnTypes(Table.PromoteHeaders(ExpectedRaw, [PromoteAllScalars=true]), {{{casts}}}, "en-US"),
    MatchingRows = List.Count(List.Intersect({{Table.ToRows(Typed), Table.ToRows(ExpectedTyped)}})),
    Checked = if Table.RowCount(Typed) = {count} and Table.RowCount(Table.Distinct(Typed)) = {count} and MatchingRows = {count}
        then Typed else error "Dimensão inválida: confira cobertura, chaves, rótulos e atributos.",
'''
    return f'''let
    BinarySource = if Text.Length(pDataFolder) = 0 then Binary.FromText("{encoded}", BinaryEncoding.Base64)
        else File.Contents(Text.TrimEnd(pDataFolder, {{"/", "\\"}}) & "/{filename}"),
    Raw = Csv.Document(BinarySource, [Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{{casts}}}, "en-US"),
{checks}    Renamed = Table.RenameColumns({"Checked" if checks else "Typed"}, {{{renames}}})
in
    Renamed'''

def table_tmdl(table,query,columns):
    parts=[f"table {table}"]
    if table=="Calendario":parts+=["\tdataCategory: Time"]
    if table=="Financas":
        for name,expr in MEASURES.items():
            fmt="0" if name=='Mês de referência' else "0.0%;-0.0%;0.0%" if ("Margem" in name or "percentual" in name or name=="Variação anual") else '"R$" #,0.00;-"R$" #,0.00;"R$" 0.00'
            parts += [f"\tmeasure '{name}' = {expr}",f"\t\tformatString: {fmt}",'\t\tdisplayFolder: Indicadores',""]
    for src,name,typ in columns:
        parts += [f"\tcolumn {name}",f"\t\tdataType: {typ}",f"\t\tsourceColumn: {name}",f"\t\tsummarizeBy: {'sum' if name=='Valor' else 'none'}"]
        if typ=="dateTime":parts+=["\t\tformatString: dd/MM/yyyy"]
        if table=="Calendario" and name=="Data":parts+=["\t\tisKey"]
        if name=="NomeMes":parts+=["\t\tsortByColumn: Mes"]
        if table=='Categorias' and name=='Categoria':parts+=["\t\tsortByColumn: Ordem"]
        if name=="AnoMes":parts+=["\t\tsortByColumn: OrdemAnoMes"]
        parts.append("")
    parts += [f"\tpartition {table} = m","\t\tmode: import","\t\tsource ="]+["\t\t\t"+line for line in query.splitlines()]
    return "\n".join(parts)+"\n"

def visual(name,kind,x,y,w,h,roles,title=None):
    obj={"$schema":schema("visualContainer","2.9.0"),"name":name,
         "position":{"x":x,"y":y,"z":1000,"width":w,"height":h,"tabOrder":1000},
         "visual":{"visualType":kind,"query":{"queryState":{r:{"projections":p} for r,p in roles.items()}}}}
    v=obj["visual"]
    v["visualContainerObjects"]={"background":[{"properties":{"show":literal("true"),"color":{"solid":{"color":literal("'#FFFFFF'")}}}}],
        "padding":[{"properties":{p:literal("10D") for p in ("top","bottom","left","right")}}]}
    if title:v["visualContainerObjects"]["title"]=[{"properties":{"show":literal("true"),"text":literal("'"+title+"'"),"fontSize":literal("13D")}}]
    if kind=="slicer":
        v["objects"]={"data":[{"properties":{"mode":literal("'Dropdown'")}}],
                       "header":[{"properties":{"show":literal("true"),"text":literal("'"+title+"'")}}]}
        v["syncGroup"]={"groupName":name,"fieldChanges":True,"filterChanges":True}
        if name=="filter_year":
            column={"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"Ano"}}
            v["objects"]["general"]=[{"properties":{"filter":{"filter":{"Version":2,"From":[{"Name":"c","Entity":"Calendario","Type":0}],
                "Where":[{"Condition":{"In":{"Expressions":[column],"Values":[[{"Literal":{"Value":"2025L"}}]]}}}]}}}}]
        if name=='filter_cutoff':
            column={"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"NomeMes"}}
            v['objects']['general']=[{'properties':{'filter':{'filter':{'Version':2,'From':[{'Name':'c','Entity':'Corte','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[column],'Values':[[{'Literal':{'Value':"'Set'"}}]]}}}]}}}}]
        if name in ('filter_year','filter_cutoff'):v['objects']['selection']=[{'properties':{'singleSelect':literal('true')}}]
        v["visualContainerObjects"].pop("title",None)
    if kind=="cardVisual":
        v["objects"]={"value":[{"selector":{"id":"default"},"properties":{"fontSize":literal("24D")}}],
                      "label":[{"selector":{"id":"default"},"properties":{"fontSize":literal("11D")}}]}
    if kind=="pivotTable":
        for role in ("Rows","Columns"):
            for p in v["query"]["queryState"].get(role,{}).get("projections",[]):p["active"]=True
        v["objects"]={"columnHeaders":[{"properties":{"fontSize":literal("10D"),"backColor":{"solid":{"color":literal("'#182D51'")}},"fontColor":{"solid":{"color":literal("'#FFFFFF'")}}}}],"rowHeaders":[{"properties":{"fontSize":literal("10D"),"stepped":literal("false")}}],"values":[{"properties":{"fontSize":literal("10D")}}],"grid":[{"properties":{"rowPadding":literal("2D")}}]}
    if kind in ("lineChart","clusteredColumnChart","clusteredBarChart"):
        v["objects"]={"dataPoint":[{"selector":{"metadata":p["queryRef"]},"properties":{"fill":{"solid":{"color":literal("'"+("#9AA5B6" if 'orçado' in p["queryRef"] else "#3157C5")+"'")}}}} for p in roles.get("Y",[])]}
    if kind=='waterfallChart':
        v['objects']={'sentimentColors':[{'properties':{k:{'solid':{'color':literal("'"+c+"'")}} for k,c in [('increaseFill','#3157C5'),('decreaseFill','#AF3B45'),('totalFill','#182D51')]}}]}
    if roles.get('Category'):
        v['query']['sortDefinition']={'sort':[{'field':roles['Category'][0]['field'],'direction':'Ascending'}],'isDefaultSort':True}
    return obj

def only_expenses(item):
    col={'Column':{'Expression':{'SourceRef':{'Source':'c'}},'Property':'Natureza'}}
    item['filterConfig']={'filters':[{'name':item['name']+'_expenses','field':field('Categorias','Natureza'),'type':'Categorical',
        'filter':{'Version':2,'From':[{'Name':'c','Entity':'Categorias','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[col],'Values':[[{'Literal':{'Value':"'Despesa'"}}]]}}}]}}]}
    return item

def textbox(name,text,x,y,w,h,size=12):
    return {"$schema":schema("visualContainer","2.9.0"),"name":name,"position":{"x":x,"y":y,"z":1000,"width":w,"height":h,"tabOrder":1000},
        "visual":{"visualType":"textbox","objects":{"general":[{"properties":{"paragraphs":[{"horizontalTextAlignment":"left","textRuns":[{"value":text,"textStyle":{"fontFamily":"Segoe UI","fontSize":str(size)+"pt","color":"#182D51" if size>12 else "#65748B","fontWeight":"bold" if size>12 else "normal"}}]}]}}]},"visualContainerObjects":{"background":[{"properties":{"show":literal("false")}}]}}}

def build_powerbi(data_dir,output_dir):
    data_dir=Path(data_dir);out=Path(output_dir)
    from validate_data import validate_dataset
    validate_dataset(data_dir)
    sem=out/"FinancialPerformance.SemanticModel";rep=out/"FinancialPerformance.Report"
    dump(out/"FinancialPerformance.pbip",{"$schema":SCHEMA+"fabric/pbip/pbipProperties/1.0.0/schema.json","version":"1.0","artifacts":[{"report":{"path":rep.name}}],"settings":{"enableAutoRecovery":True}})
    dump(sem/"definition.pbism",{"$schema":SCHEMA+"fabric/item/semanticModel/definitionProperties/1.0.0/schema.json","version":"4.2","settings":{"qnaEnabled":False}})
    write(sem/"definition/database.tmdl","database\n\tcompatibilityLevel: 1604\n")
    write(sem/"definition/model.tmdl","model Model\n\tculture: pt-BR\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\n"+"\n".join(f"ref table {t}" for t in (*TABLES,'Corte'))+"\n")
    write(sem/"definition/expressions.tmdl",'expression pDataFolder = "" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]\n')
    rel=[]
    for table,key in (("Areas","AreaId"),("Categorias","CategoriaId"),("Calendario","Data")):
        rel += [f"relationship rel_{table}",f"\tfromColumn: Financas.{key}",f"\ttoColumn: {table}.{key}","\tcrossFilteringBehavior: oneDirection",""]
    write(sem/"definition/relationships.tmdl","\n".join(rel))
    for table,(file,columns) in TABLES.items():
        query=query_source(data_dir,file,columns)
        write(sem/f"definition/tables/{table}.tmdl",table_tmdl(table,query,columns))
        write(out/f"queries/{table}.pq",query+"\n")
    write(out/"queries/pDataFolder.pq",'"" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]\n')
    cut_query=cutoff_query()
    write(sem/'definition/tables/Corte.tmdl',table_tmdl('Corte',cut_query,[('Mes','Mes','int64'),('NomeMes','NomeMes','string')]))
    write(out/'queries/Corte.pq',cut_query+'\n')
    write(out/"measures.dax","// Medidas da tabela Financas; dados fictícios em BRL.\n\n"+"\n\n".join(f"{k} = {v}" for k,v in MEASURES.items())+"\n")
    dump(rep/"definition.pbir",{"$schema":SCHEMA+"fabric/item/report/definitionProperties/2.0.0/schema.json","version":"4.0","datasetReference":{"byPath":{"path":"../"+sem.name}}})
    definition=rep/"definition"
    dump(definition/"version.json",{"$schema":schema("versionMetadata","1.0.0"),"version":"2.0.0"})
    dump(definition/"report.json",{"$schema":schema("report","1.0.0"),"layoutOptimization":"None",
         "themeCollection":{"baseTheme":{"name":"CY24SU10","reportVersionAtImport":"3.0.0","type":"SharedResources"}}})
    from report_pages import build_pages
    build_pages(definition)

if __name__=="__main__":build_powerbi(ROOT/"data",ROOT/"powerbi")
