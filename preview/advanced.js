(function(global){
  'use strict';
  const months=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const labels={REV:'Receita de serviços',DIR:'Custos diretos',PES:'Pessoal',TEC:'Tecnologia',COM:'Comercial',ADM:'Administrativo'};
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const money=n=>n===null?'—':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(n);
  const mil=n=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:0}).format(n/1000);
  const pct=n=>n===null?'—':new Intl.NumberFormat('pt-BR',{style:'percent',maximumFractionDigits:1}).format(n);
  const sign=n=>n<0?'bad':n>0?'good':'';
  const card=(label,value,note,color='')=>'<section class="card"><div class="label">'+label+'</div><div class="value '+color+'">'+value+'</div><div class="note">'+note+'</div></section>';
  const head=(title,sub)=>'<h3>'+title+'</h3><p class="sub">'+sub+'</p>';
  const legend='<div class="legend"><span><i class="dot" style="background:#3157c5"></i>Realizado até corte</span><span><i class="dot" style="background:#bf842c"></i>Projetado pelas premissas</span><span><i class="dot" style="background:#8c9cb2"></i>Orçado</span></div>';
  const method=()=>'<details class="method"><summary>Premissa da projeção e sinais</summary><p>EAC é a estimativa de fechamento: realizado de janeiro até o mês de referência + orçamento dos meses restantes ajustado pelas premissas selecionadas. Base com 0% mantém o orçamento futuro. Os percentuais iniciais são ilustrativos, não tendências estimadas. O exemplo usa dados fictícios e não utiliza valores realizados após o corte para estimar o futuro. Gastos aparecem em magnitude positiva no Build-up. Desvio favorável de gastos = orçado − EAC; desvio do resultado = EAC − orçado. Carryover e risco de não execução não são estimados nesta base.</p></details>';
  function costTable(p){
    const costs=p.categories.filter(c=>c.category_id!=='REV');
    return '<section class="panel table-panel">'+head('Detalhamento do Build-up','Gastos em reais, apresentados positivos. Desvio positivo é favorável.')+'<div class="table-scroll"><table><thead><tr><th>Categoria</th><th>Orçado anual</th><th>Realizado até '+months[p.cutoff-1]+'</th><th>Projetado restante</th><th>EAC</th><th>Desvio favorável</th></tr></thead><tbody>'+costs.map(c=>'<tr><td>'+labels[c.category_id]+'</td><td>'+money(-c.budget)+'</td><td>'+money(-c.actual_to_date)+'</td><td>'+money(-c.remaining)+'</td><td>'+money(-c.eac)+'</td><td class="'+sign(c.variance)+'">'+money(c.variance)+'</td></tr>').join('')+'<tr class="total"><td>Total de gastos</td><td>'+money(p.budget.expenses)+'</td><td>'+money(p.actual_to_date.expenses)+'</td><td>'+money(p.remaining.expenses)+'</td><td>'+money(p.eac.expenses)+'</td><td class="'+sign(p.expense_variance)+'">'+money(p.expense_variance)+'</td></tr></tbody></table></div></section>';
  }
  function waterfall(p){
    const costs=p.categories.filter(c=>c.category_id!=='REV'),bars=costs.map(c=>({label:labels[c.category_id],a:-c.actual_to_date,f:-c.remaining}));
    bars.push({label:'Total EAC',a:p.actual_to_date.expenses,f:p.remaining.expenses,total:true});
    const w=920,h=350,L=65,R=20,T=28,B=59,max=Math.max(p.eac.expenses,p.budget.expenses,1)*1.15,span=(w-L-R)/bars.length,bw=span*.58;
    const y=v=>h-B-v/max*(h-T-B);let cumulative=0;
    let svg='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Cascata de gastos por categoria, com realizado e projetado separados">';
    for(let i=0;i<=4;i++){let v=max*i/4;svg+='<line x1="'+L+'" x2="'+(w-R)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="#e3e8f0"/><text x="'+(L-9)+'" y="'+(y(v)+4)+'" text-anchor="end" fill="#65748b" font-size="11">'+mil(v)+'</text>';}
    svg+='<line x1="'+L+'" x2="'+(w-R)+'" y1="'+y(p.budget.expenses)+'" y2="'+y(p.budget.expenses)+'" stroke="#8c9cb2" stroke-width="1.5" stroke-dasharray="6 4"/>';
    bars.forEach((b,i)=>{
      const base=b.total?0:cumulative,x=L+i*span+(span-bw)/2,top=base+b.a+b.f;
      svg+='<rect x="'+x+'" y="'+y(base+b.a)+'" width="'+bw+'" height="'+(y(base)-y(base+b.a))+'" fill="#3157c5"><title>'+esc(b.label)+' realizado: '+money(b.a)+'</title></rect>';
      svg+='<rect x="'+x+'" y="'+y(top)+'" width="'+bw+'" height="'+(y(base+b.a)-y(top))+'" fill="#bf842c"><title>'+esc(b.label)+' projetado: '+money(b.f)+'</title></rect>';
      svg+='<text x="'+(x+bw/2)+'" y="'+(y(top)-8)+'" text-anchor="middle" font-size="11" font-weight="600" fill="#26344c">'+mil(b.a+b.f)+'</text><text x="'+(x+bw/2)+'" y="'+(h-B+22)+'" text-anchor="middle" font-size="11" fill="#26344c">'+esc(b.label)+'</text>';
      if(i<costs.length-1)svg+='<line x1="'+(x+bw)+'" x2="'+(x+span)+'" y1="'+y(top)+'" y2="'+y(top)+'" stroke="#9caac0" stroke-dasharray="3 3"/>';
      if(!b.total)cumulative=top;
    });
    return '<div class="chart-scroll" tabindex="0">'+svg+'</svg></div>'+legend;
  }
  function projectionChart(monthly,cut){
    const vals=monthly.flatMap((m,i)=>[m.budget.result,m.active.result]);
    const min=Math.min(0,...vals),max=Math.max(1,...vals)*1.12,w=780,h=280,L=59,R=16,T=20,B=40;
    const x=i=>L+i*(w-L-R)/11,y=v=>h-B-(v-min)/(max-min)*(h-T-B);
    let out='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Resultado mensal: realizado até referência e projeção dos meses restantes">';
    for(let i=0;i<=4;i++){const v=min+(max-min)*i/4;out+='<line x1="'+L+'" x2="'+(w-R)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="#e3e8f0"/><text x="'+(L-8)+'" y="'+(y(v)+4)+'" text-anchor="end" font-size="10" fill="#65748b">'+mil(v)+'</text>';}
    monthly.forEach((m,i)=>out+='<text x="'+x(i)+'" y="'+(h-14)+'" text-anchor="middle" font-size="10" fill="#65748b">'+months[i]+'</text>');
    out+='<polyline fill="none" stroke="#8c9cb2" stroke-dasharray="5 4" stroke-width="2" points="'+monthly.map((m,i)=>x(i)+','+y(m.budget.result)).join(' ')+'"/>';
    out+='<polyline fill="none" stroke="#3157c5" stroke-width="2.5" points="'+monthly.slice(0,cut).map((m,i)=>x(i)+','+y(m.active.result)).join(' ')+'"/>';
    if(cut<12)out+='<polyline fill="none" stroke="#bf842c" stroke-width="2.5" stroke-dasharray="5 3" points="'+monthly.slice(cut-1).map((m,j)=>x(j+cut-1)+','+y(m.active.result)).join(' ')+'"/>';
    monthly.forEach((m,i)=>{let v=m.active.result;out+='<circle cx="'+x(i)+'" cy="'+y(v)+'" r="3" fill="'+(i<cut?'#3157c5':'#bf842c')+'"><title>'+months[i]+': '+money(v)+' ('+(i<cut?'Realizado':'Projetado')+')</title></circle>';});
    return out+'</svg>'+legend;
  }
  function forecastTable(monthly,p){
    return '<section class="panel table-panel">'+head('Composição da estimativa mensal','Meses após '+months[p.cutoff-1]+' usam orçamento ajustado pelas premissas. Valores em reais.')+'<div class="table-scroll"><table><thead><tr><th>Mês</th><th>Origem</th><th>Resultado orçado</th><th>Resultado EAC</th><th>Desvio</th><th>Receita EAC</th><th>Gastos EAC</th></tr></thead><tbody>'+monthly.map((m,i)=>{const v=m.active,d=v.result-m.budget.result;return '<tr><td>'+months[i]+'</td><td><span class="origin '+(i<p.cutoff?'actual-origin':'forecast-origin')+'">'+(i<p.cutoff?'Realizado':'Projetado')+'</span></td><td>'+money(m.budget.result)+'</td><td>'+money(v.result)+'</td><td class="'+sign(d)+'">'+money(d)+'</td><td>'+money(v.revenue)+'</td><td>'+money(v.expenses)+'</td></tr>';}).join('')+'<tr class="total"><td>Total</td><td>EAC</td><td>'+money(p.budget.result)+'</td><td>'+money(p.eac.result)+'</td><td class="'+sign(p.variance)+'">'+money(p.variance)+'</td><td>'+money(p.eac.revenue)+'</td><td>'+money(p.eac.expenses)+'</td></tr></tbody></table></div></section>';
  }
  function premise(id,year,cut,area){
    if(year===2025){
      if(id==='TEC'&&cut>=3)return 'A simulação inclui gasto adicional de tecnologia desde março.';
      if(id==='PES'&&cut>=7&&(!area||area==='ENG'))return 'A simulação inclui aumento de pessoal em Engenharia desde julho.';
      if(id==='COM'&&cut>=10&&(!area||area==='ANA'))return 'A simulação inclui gasto comercial adicional em Analytics no último trimestre.';
    }
    return id==='DIR'?'Os custos diretos acompanham a receita na simulação.':'Variações determinísticas previstas nas premissas da base fictícia.';
  }
  function driverList(list,color,year,cut,area){
    if(!list.length)return '<p class="empty-state">Nenhuma categoria neste grupo para o recorte.</p>';
    return list.map(c=>'<article class="cause"><div><b>'+labels[c.category_id]+'</b><strong class="'+color+'">'+money(Math.abs(c.variance))+'</strong></div><p><span>Premissa da simulação:</span> '+premise(c.category_id,year,cut,area)+'</p></article>').join('');
  }
  function monthBars(s){
    const rows=[['Receita','revenue'],['Gastos','expenses'],['Resultado','result']],w=760,h=237,L=100,R=125;
    const values=rows.flatMap(([label,k])=>[s.budget[k],s.actual[k]]),min=Math.min(0,...values),max=Math.max(1,...values),x=v=>L+(v-min)/(max-min)*(w-L-R);
    let out='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Receita, gastos e resultado orçados e realizados do mês">';
    out+='<line x1="'+x(0)+'" x2="'+x(0)+'" y1="8" y2="220" stroke="#ced6e4"/>';
    rows.forEach(([label,k],i)=>{const y=20+i*72;out+='<text x="0" y="'+(y+17)+'" fill="#26344c" font-size="13">'+label+'</text>';for(const [sc,dy,color] of [['budget',0,'#9aa5b6'],['actual',25,'#3157c5']]){let v=s[sc][k];out+='<rect x="'+Math.min(x(0),x(v))+'" y="'+(y+dy)+'" width="'+Math.abs(x(v)-x(0))+'" height="16" fill="'+color+'"/><text x="'+(w-2)+'" y="'+(y+dy+13)+'" text-anchor="end" fill="#26344c" font-size="11">'+money(v)+'</text>';}});
    return out+'</svg><div class="legend"><span><i class="dot" style="background:#9aa5b6"></i>Orçado</span><span><i class="dot" style="background:#3157c5"></i>Realizado</span></div>';
  }
  function render(view,data,year,cut,area,scenario={name:"Base",revenue:0,expenses:0}){
    const F=global.Finance,monthly=F.monthly(data.rows,year,area);
    const p=view==='monthly'?null:F.scenarioProjection(data.rows,year,cut,area,scenario.revenue,scenario.expenses);
    if(view==='buildup')return '<div class="cards">'+card('Gastos orçados',money(p.budget.expenses),'Referência anual')+card('Realizado até '+months[cut-1],money(p.actual_to_date.expenses),'Gastos acumulados')+card('Projetado restante',money(p.remaining.expenses),'Orçamento futuro ajustado')+card('Gastos EAC',money(p.eac.expenses),'Realizado + projetado')+'</div><div class="grid"><section class="panel">'+head('Build-up por categoria','R$ mil / a linha tracejada representa o orçamento anual')+waterfall(p)+'</section><aside class="panel attention">'+head('Leitura do fechamento','Estimativa hipotética de gastos')+'<div class="attention-total '+sign(p.expense_variance)+'">'+(p.expense_variance===0?'Gastos em linha com o orçamento':money(Math.abs(p.expense_variance))+(p.expense_variance<0?' acima do orçamento':' abaixo do orçamento'))+'</div><div class="metric-line"><span>Economias por categoria</span><b class="good">'+money(p.expense_savings)+'</b></div><div class="metric-line"><span>Aumentos por categoria</span><b class="bad">'+money(p.expense_overruns)+'</b></div><p class="small">Economias − aumentos = desvio favorável de gastos. Em dezembro, a parcela projetada é zero.</p></aside></div>'+costTable(p)+method();
    if(view==='drivers'){
      const costs=p.categories.filter(c=>c.category_id!=='REV'),bad=costs.filter(c=>c.variance<0).sort((a,b)=>a.variance-b.variance),good=costs.filter(c=>c.variance>0).sort((a,b)=>b.variance-a.variance),rev=p.categories[0];
      return '<div class="cards">'+card('Aumentos de gastos',money(p.expense_overruns),'Categorias acima do orçamento','bad')+card('Economias de gastos',money(p.expense_savings),'Categorias abaixo do orçamento','good')+card('Impacto da receita',money(rev.variance),'Receita EAC − receita orçada',sign(rev.variance))+card('Desvio do resultado',money(p.variance),'Receita e gastos combinados',sign(p.variance))+'</div><div class="grid equal"><section class="panel">'+head('Pressão de gastos','Impactos desfavoráveis, do maior para o menor')+driverList(bad,'bad',year,cut,area)+'</section><section class="panel">'+head('Economias','Impactos favoráveis por categoria')+driverList(good,'good',year,cut,area)+'<div class="reconciliation"><b>Conciliação do resultado</b><p>Impacto da receita '+money(rev.variance)+' + impacto dos gastos '+money(p.expense_variance)+' = '+money(p.variance)+'.</p></div></section></div>'+costTable(p)+method();
    }
    if(view==='monthly'){
      const period=F.period(data.rows,year,cut,area),s=period.month,ytd=period.ytd,d=F.drivers(data.rows.filter(r=>Number(r.month.slice(5,7))===cut),year,area);
      return '<div class="cards">'+card('Receita do mês',money(s.actual.revenue),'Orçada '+money(s.budget.revenue))+card('Gastos do mês',money(s.actual.expenses),'Orçados '+money(s.budget.expenses))+card('Resultado do mês',money(s.actual.result),'Desvio '+money(s.variance),sign(s.variance))+card('Margem do mês',pct(s.actual.margin),'Orçada '+pct(s.budget.margin))+'</div><div class="grid"><section class="panel">'+head('Comparação do mês','Valores em reais / mesmo mês e mesma área')+monthBars(s)+'</section><aside class="panel attention">'+head('Acumulado até '+months[cut-1],'Janeiro até o mês de referência')+'<div class="metric-line"><span>Resultado orçado YTD</span><b>'+money(ytd.budget.result)+'</b></div><div class="metric-line"><span>Resultado realizado YTD</span><b>'+money(ytd.actual.result)+'</b></div><div class="metric-line"><span>Desvio acumulado</span><b class="'+sign(ytd.variance)+'">'+money(ytd.variance)+'</b></div><p class="small">Margem acumulada '+pct(ytd.actual.margin)+'. YTD corresponde ao acumulado do ano.</p></aside></div><section class="panel table-panel">'+head('Categorias do mês','Valores com sinal financeiro / receitas positivas e despesas negativas')+'<div class="table-scroll"><table><thead><tr><th>Categoria</th><th>Orçado</th><th>Realizado</th><th>Desvio favorável</th></tr></thead><tbody>'+d.map(c=>'<tr><td>'+labels[c.category_id]+'</td><td>'+money(c.budget)+'</td><td>'+money(c.actual)+'</td><td class="'+sign(c.variance)+'">'+money(c.variance)+'</td></tr>').join('')+'<tr class="total"><td>Resultado do mês</td><td>'+money(s.budget.result)+'</td><td>'+money(s.actual.result)+'</td><td class="'+sign(s.variance)+'">'+money(s.variance)+'</td></tr></tbody></table></div></section><details><summary>Recorte mensal e acumulado</summary><p>O mês mostra apenas '+months[cut-1]+'. O acumulado usa janeiro até '+months[cut-1]+', com o mesmo ano e área. Percentuais usam os respectivos totais; não somam margens mensais.</p></details>';
    }
    return '<div class="cards">'+card('Resultado orçado',money(p.budget.result),'Referência do ano')+card('Resultado EAC',money(p.eac.result),'Estimativa de fechamento')+card('Desvio EAC',money(p.variance),pct(p.variance_pct)+' frente ao orçamento',sign(p.variance))+card('Margem EAC',pct(p.eac.margin),'Resultado EAC / receita EAC')+'</div><div class="grid"><section class="panel chart-panel">'+head('Resultado realizado e projetado','R$ mil / projeção hipotética após '+months[cut-1])+projectionChart(p.monthly,cut)+'</section><aside class="panel attention">'+head('Composição do EAC','Cenário '+esc(scenario.name)+' / receita '+pct(scenario.revenue)+' / gastos '+pct(scenario.expenses))+'<div class="metric-line"><span>Resultado realizado até corte</span><b>'+money(p.actual_to_date.result)+'</b></div><div class="metric-line"><span>Resultado projetado restante</span><b>'+money(p.remaining.result)+'</b></div><div class="metric-line"><span>Resultado EAC</span><b>'+money(p.eac.result)+'</b></div><p class="small">Receita EAC '+money(p.eac.revenue)+'. Gastos EAC '+money(p.eac.expenses)+'. O realizado futuro permanece fora desta estimativa.</p></aside></div>'+forecastTable(p.monthly,p)+method();
  }
  global.AdvancedReport={render};
})(typeof globalThis!=='undefined'?globalThis:this);
