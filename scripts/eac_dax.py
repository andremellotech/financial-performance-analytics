"""Medidas de corte mensal e EAC hipotético; sem novo cenário na base original."""
AUX_COLUMNS={'Corte':['Mes','NomeMes']}
EXTRA_MEASURES={'Mês de referência':'SELECTEDVALUE(Corte[Mes], 9)'}
for label,base,condition in [
 ('Receita realizada até corte','Receita realizada','<='),('Gastos realizados até corte','Gastos realizados','<='),('Resultado realizado até corte','Resultado realizado','<='),
 ('Receita orçada restante','Receita orçada','>'),('Gastos orçados restantes','Gastos orçados','>'),('Resultado orçado restante','Resultado orçado','>'),
 ('Receita do mês','Receita realizada','='),('Gastos do mês','Gastos realizados','='),('Resultado do mês','Resultado realizado','='),('Resultado orçado do mês','Resultado orçado','='),('Resultado orçado até corte','Resultado orçado','<=')]:
 EXTRA_MEASURES[label]=f'VAR CorteMes = [Mês de referência] RETURN IF(HASONEVALUE(Calendario[Ano]), COALESCE(CALCULATE([{base}], KEEPFILTERS(Calendario[Mes] {condition} CorteMes)), 0))'
EXTRA_MEASURES.update({
 'Receita EAC':'[Receita realizada até corte] + [Receita orçada restante]',
 'Gastos EAC':'[Gastos realizados até corte] + [Gastos orçados restantes]',
 'Resultado EAC':'[Resultado realizado até corte] + [Resultado orçado restante]',
 'Margem EAC':'DIVIDE([Resultado EAC], [Receita EAC])',
 'Desvio EAC':'IF(NOT ISBLANK([Resultado EAC]), [Resultado EAC] - [Resultado orçado])',
 'Desvio EAC percentual':'DIVIDE([Desvio EAC], ABS([Resultado orçado]))',
 'Desvio de gastos EAC':'IF(NOT ISBLANK([Gastos EAC]), [Gastos orçados] - [Gastos EAC])',
 'Impacto da receita EAC':'IF(NOT ISBLANK([Receita EAC]), [Receita EAC] - [Receita orçada])',
 'Economias de gastos':'IF(HASONEVALUE(Calendario[Ano]), SUMX(FILTER(VALUES(Categorias[CategoriaId]), Categorias[CategoriaId] <> "REV"), MAX([Desvio de gastos EAC], 0)))',
 'Aumentos de gastos':'IF(HASONEVALUE(Calendario[Ano]), SUMX(FILTER(VALUES(Categorias[CategoriaId]), Categorias[CategoriaId] <> "REV"), MAX(-[Desvio de gastos EAC], 0)))',
 'Margem do mês':'DIVIDE([Resultado do mês], [Receita do mês])',
 'Desvio do mês':'IF(NOT ISBLANK([Resultado do mês]), [Resultado do mês] - [Resultado orçado do mês])'})

def cutoff_query():
 names=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
 return '#table(type table [Mes = Int64.Type, NomeMes = text], {'+', '.join('{'+str(i+1)+', "'+m+'"}' for i,m in enumerate(names))+'})'
