"""Sete perspectivas nativas com corte mensal independente do calendário."""
from build_powerbi import visual,textbox,projection,literal,schema,dump,only_expenses,MEASURES
PAGES=[('executive','Visão executiva'),('budget','Orçado × realizado'),('buildup','Build-up'),('drivers','Motivadores'),('monthly','Visão mensal'),('forecast','Projeção / EAC'),('areas','Áreas e categorias')]
METRICS={
 'executive':['Receita realizada','Gastos realizados','Resultado realizado','Margem realizada'],
 'budget':['Resultado orçado','Resultado realizado','Desvio do resultado','Desvio percentual'],
 'areas':['Resultado orçado','Resultado realizado','Desvio do resultado','Desvio percentual'],
 'buildup':['Gastos orçados','Gastos realizados até corte','Gastos orçados restantes','Gastos EAC'],
 'drivers':['Aumentos de gastos','Economias de gastos','Impacto da receita EAC','Desvio EAC'],
 'monthly':['Receita do mês','Gastos do mês','Resultado do mês','Margem do mês'],
 'forecast':['Resultado orçado','Resultado EAC','Desvio EAC','Margem EAC']}
def measures(names):return [projection('Financas',m,True) for m in names]
def chart(name,kind,frame,table,column,names,title):
 return visual(name,kind,*frame,{'Category':[projection(table,column)],'Y':measures(names)},title)
def detail(name,y,h,table,column,names,title):
 return visual(name,'pivotTable',24,y,1232,h,{'Rows':[projection(table,column)],'Values':measures(names)},title)
def cards(name,frame,names,title):return visual(name,'cardVisual',*frame,{'Data':measures(names)},title)
def build_pages(definition):
 dump(definition/'pages/pages.json',{'$schema':schema('pagesMetadata','1.0.0'),'pageOrder':[p[0] for p in PAGES],'activePageName':'executive'})
 for pid,title in PAGES:
  page=definition/f'pages/{pid}';advanced=pid in ('buildup','drivers','monthly','forecast')
  dump(page/'page.json',{'$schema':schema('page','2.0.0'),'name':pid,'displayName':title,'displayOption':'FitToPage','width':1280,'height':720,
   'objects':{'background':[{'properties':{'color':{'solid':{'color':literal("'#F3F5F9'")}},'transparency':literal('0D')}}]}})
  note='EAC hipotético = realizado até referência + orçamento restante / Dados fictícios' if advanced else 'Dados fictícios / BRL / Resultado operacional simplificado'
  if pid=='monthly':note='Mês selecionado e acumulado de janeiro até referência / Dados fictícios'
  items=[textbox('page_title',title,24,12,560 if advanced else 690,42,20),visual('filter_year','slicer',792,10,148,54,{'Values':[projection('Calendario','Ano')]},'Ano'),visual('filter_area','slicer',956,10,300,54,{'Values':[projection('Areas','Area')]},'Área'),textbox('scope_note',note,24,692,1232,24,10)]
  if advanced:items.append(visual('filter_cutoff','slicer',604,10,170,54,{'Values':[projection('Corte','NomeMes')]},'Mês de referência'))
  for i,m in enumerate(METRICS[pid]):items.append(cards(f'kpi_{i}',(24+i*312,76,296,106),[m],None))
  left=(24,198,808,240);right=(850,198,406,240)
  if pid=='executive':
   items += [chart('monthly','lineChart',(24,198,808,192),'Calendario','AnoMes',['Resultado orçado','Resultado realizado'],'Evolução do resultado · R$'),cards('attention',(850,198,406,90),['Desvio do resultado','Desvio percentual'],'Pontos de atenção · orçamento'),cards('annual_comparison',(850,300,406,90),['Resultado ano anterior','Variação anual'],'Comparação anual')]
  elif pid=='budget':
   items += [chart('comparison','lineChart',(24,198,808,192),'Calendario','AnoMes',['Resultado orçado','Resultado realizado'],'Orçado × realizado · R$'),chart('drivers','clusteredBarChart',(850,198,406,192),'Categorias','Categoria',['Desvio do resultado'],'Impactos no resultado · R$')]
  elif pid=='areas':
   items += [chart('area_comparison','clusteredBarChart',(658,198,598,228),'Areas','Area',['Resultado orçado','Resultado realizado'],'Resultado por área · R$'),chart('category_comparison','clusteredBarChart',(24,198,610,228),'Categorias','Categoria',['Desvio do resultado'],'Impactos no resultado · R$')]
  elif pid=='buildup':
   items += [only_expenses(chart('composition','waterfallChart',left,'Categorias','Categoria',['Gastos EAC'],'Cascata de gastos EAC por categoria · R$')),cards('spending_gap',right,['Desvio de gastos EAC','Economias de gastos','Aumentos de gastos'],'Pontos de atenção · gastos')]
  elif pid=='drivers':
   items += [only_expenses(chart('expense_impacts','clusteredBarChart',left,'Categorias','Categoria',['Desvio de gastos EAC'],'Impactos de gastos · positivo favorável')),cards('result_gap',right,['Impacto da receita EAC','Desvio de gastos EAC','Desvio EAC'],'Conciliação do resultado')]
  elif pid=='monthly':
   items += [chart('month_categories','clusteredBarChart',left,'Categorias','Categoria',['Resultado orçado do mês','Resultado do mês'],'Categorias do mês · valores com sinal'),cards('ytd',right,['Resultado orçado até corte','Resultado realizado até corte'],'Resultado acumulado até referência')]
  else:
   items += [chart('eac_curve','lineChart',left,'Calendario','AnoMes',['Resultado orçado','Resultado EAC'],'Resultado mensal: realizado até corte + orçamento restante'),cards('eac_composition',right,['Resultado realizado até corte','Resultado orçado restante','Resultado EAC'],'Composição do resultado EAC')]
  if pid in ('executive','budget'):
   items.append(detail('monthly_detail',406,278,'Calendario','AnoMes',['Resultado orçado','Resultado realizado','Desvio do resultado','Desvio percentual','Margem realizada'],'Comparativo mensal · R$ e %'))
  elif pid=='areas':
   items.append(detail('category_detail',442,242,'Categorias','Categoria',['Resultado orçado','Resultado realizado','Desvio do resultado'],'Detalhamento por categoria · valores com sinal'))
  elif pid in ('buildup','drivers'):
   items.append(only_expenses(detail('eac_cost_detail',454,230,'Categorias','Categoria',['Gastos orçados','Gastos realizados até corte','Gastos orçados restantes','Gastos EAC','Desvio de gastos EAC'],'Build-up de gastos · valores positivos')))
  elif pid=='monthly':
   items.append(detail('month_detail',454,230,'Categorias','Categoria',['Resultado orçado do mês','Resultado do mês','Desvio do mês'],'Categorias do mês · valores com sinal'))
  else:
   items.append(detail('eac_month_detail',454,230,'Calendario','AnoMes',['Resultado orçado','Resultado EAC','Desvio EAC','Margem EAC'],'Estimativa mensal · R$ e %'))
  for obsolete in ('kpis','area_result'):
   old=page/f'visuals/{obsolete}/visual.json'
   if old.exists():old.unlink();old.parent.rmdir()
  for item in items:dump(page/f"visuals/{item['name']}/visual.json",item)
 print(f'Power BI: 7 páginas, {len(MEASURES)} medidas e seletor de mês de referência gerados.')
