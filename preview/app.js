(()=>{
  const data=JSON.parse(document.getElementById("dataset").textContent),F=window.Finance;
  const $=id=>document.getElementById(id),names=Object.fromEntries(data.areas.map(a=>[a.area_id,a.area_name]));
  const cats=Object.fromEntries(data.categories.map(c=>[c.category_id,c.category_name]));
  const money=n=>n===null?"—":new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL",maximumFractionDigits:0}).format(n);
  const pct=n=>n===null?"—":new Intl.NumberFormat("pt-BR",{style:"percent",maximumFractionDigits:1}).format(n);
  const mil=n=>n===null?"—":new Intl.NumberFormat("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1}).format(n/1000);
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const sign=n=>n===null?"":n<0?"bad":n>0?"good":"";
  const months=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
  let view="executive";
  const cases={Base:{revenue:0,expenses:0},Otimista:{revenue:5,expenses:-3},Conservativo:{revenue:-5,expenses:3}};
  function selectCase(){const c=cases[$('forecast-case').value];$('revenue-change').value=c.revenue;$('expense-change').value=c.expenses;render();}
  $("cutoff").innerHTML=months.map((m,i)=>'<option value="'+(i+1)+'"'+(i===8?' selected':'')+'>'+m+'</option>').join('');
  $("year").innerHTML=data.years.map(y=>'<option value="'+y+'"'+(y===2025?" selected":"")+">"+y+"</option>").join("");
  $("area").innerHTML='<option value="">Todas as áreas</option>'+data.areas.map(a=>'<option value="'+a.area_id+'">'+esc(a.area_name)+"</option>").join("");
  const card=(label,value,note="",color="")=>'<div class="card"><div class="label">'+label+'</div><div class="value '+color+'">'+value+'</div><div class="note">'+note+"</div></div>";
  function lineChart(monthly){
    const w=690,h=284,L=60,R=15,T=16,B=44,max=Math.ceil(Math.max(...monthly.flatMap(m=>[m.actual.result,m.budget.result]),0)/50000)*50000||1,min=Math.min(0,...monthly.flatMap(m=>[m.actual.result,m.budget.result]));
    const x=i=>L+i*(w-L-R)/11,y=v=>h-B-(v-min)/(max-min)*(h-B-T);
    let out='<svg viewBox="0 0 '+w+" "+h+'" role="img" aria-label="Resultado mensal orçado e realizado">';
    for(let i=0;i<=4;i++){let v=min+(max-min)*i/4;out+='<line x1="'+L+'" x2="'+(w-R)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="#e9eef4"/><text x="'+(L-9)+'" y="'+(y(v)+4)+'" text-anchor="end" fill="#718198" font-size="10">'+esc((v/1000).toFixed(0))+"</text>";}
    monthly.forEach((m,i)=>out+='<text x="'+x(i)+'" y="'+(h-15)+'" text-anchor="middle" fill="#718198" font-size="10">'+months[i]+"</text>");
    for(const [scenario,color,dash] of [["budget","#8c9cb2","5 4"],["actual","#3157c5",""]]){
      out+='<polyline points="'+monthly.map((m,i)=>x(i)+","+y(m[scenario].result)).join(" ")+'" fill="none" stroke="'+color+'" stroke-width="2.5" stroke-dasharray="'+dash+'"/>';
      monthly.forEach((m,i)=>out+='<circle cx="'+x(i)+'" cy="'+y(m[scenario].result)+'" r="3" fill="'+color+'"><title>'+months[i]+": "+esc(money(m[scenario].result))+"</title></circle>");
    }return out+"</svg>";
  }
  function areaBars(year,area){
    const rows=data.areas.filter(a=>!area||a.area_id===area).map(a=>({...a,s:F.summarize(data.rows,year,a.area_id)}));
    const max=Math.max(...rows.map(a=>Math.max(a.s.actual.result,a.s.budget.result)),1);
    return rows.map(a=>'<div class="area-row"><div class="area-top"><b>'+esc(a.area_name)+'</b><b>'+money(a.s.actual.result)+'</b></div><div class="bar-track"><div class="bar-fill" style="width:'+Math.max(0,a.s.actual.result/max*100)+'%"></div></div><div class="small" style="margin-top:5px">Orçado '+money(a.s.budget.result)+' · <span class="'+sign(a.s.variance)+'">'+pct(a.s.variance_pct)+" de desvio</span></div></div>").join("");
  }
  function driverChart(drivers){
    const max=Math.max(...drivers.map(d=>Math.abs(d.variance)),1);
    return '<div class="drivers">'+drivers.map(d=>'<div class="driver"><span>'+esc(cats[d.category_id])+'</span><div class="driver-track"><div class="driver-bar" style="left:'+(d.variance<0?50-Math.abs(d.variance)/max*48:50)+'%;width:'+Math.abs(d.variance)/max*48+'%;background:'+(d.variance<0?"#af3b45":"#237447")+'"></div></div><span class="driver-value '+sign(d.variance)+'">'+money(d.variance)+"</span></div>").join("")+"</div>";
  }
  function monthlyTable(monthly,s){
    const rows=[['Receita realizada',m=>m.actual.revenue,s.actual.revenue,'money'],['Gastos realizados',m=>m.actual.expenses,s.actual.expenses,'money'],['Resultado orçado',m=>m.budget.result,s.budget.result,'money'],['Resultado realizado',m=>m.actual.result,s.actual.result,'money'],['Desvio do resultado',m=>m.variance,s.variance,'variance'],['Margem realizada',m=>m.actual.margin,s.actual.margin,'pct']];
    return '<section class="panel table-panel"><h3>Comparativo mensal</h3><p class="sub">R$ mil, arredondados a uma casa decimal. O total da margem usa os totais do período.</p><div class="table-scroll" tabindex="0" role="region" aria-label="Comparativo mensal rolável"><table class="matrix"><thead><tr><th scope="col">Indicador</th>'+months.map(m=>'<th scope="col">'+m+'</th>').join('')+'<th scope="col" class="total-col">Total</th></tr></thead><tbody>'+rows.map(([label,fn,total,type])=>'<tr class="'+(label==='Resultado realizado'?'result-row':'')+'"><th scope="row">'+label+'</th>'+monthly.map(m=>{const v=fn(m);return '<td class="'+(type==='variance'?'variance-cell '+sign(v):'')+'" title="'+esc(type==='pct'?pct(v):money(v))+'">'+(type==='pct'?pct(v):mil(v))+'</td>';}).join('')+'<td class="total-col '+(type==='variance'?sign(total):'')+'" title="'+esc(type==='pct'?pct(total):money(total))+'">'+(type==='pct'?pct(total):mil(total))+'</td></tr>').join('')+'</tbody></table></div></section>';
  }
  function attention(s,monthly,drivers){
    const worst=[...drivers].sort((a,b)=>a.variance-b.variance)[0],month=[...monthly].sort((a,b)=>a.variance-b.variance)[0];
    const state=s.variance<0?'abaixo':'acima',conclusion=s.variance===0?'Resultado em linha com o orçamento':money(Math.abs(s.variance))+' '+state+' do orçamento';
    return '<aside class="panel attention"><h3>Pontos de atenção</h3><p class="sub">Leitura calculada para o recorte selecionado</p><div class="attention-total '+sign(s.variance)+'">'+conclusion+'</div><div class="attention-item"><span>01</span><div><b>'+esc(worst.variance<0?cats[worst.category_id]:'Categorias')+'</b><p>'+(worst.variance<0?'Maior impacto desfavorável: '+money(worst.variance)+'.':'Nenhuma categoria com desvio desfavorável.')+'</p></div></div><div class="attention-item"><span>02</span><div><b>'+esc(month.variance<0?months[month.month-1]+' concentra o maior desvio':'Comparação mensal')+'</b><p>'+(month.variance<0?money(month.variance)+' frente ao orçamento do mês.':'Nenhum mês abaixo do orçamento.')+'</p></div></div><div class="annual"><span>Resultado em '+(s.year-1)+'</span><b>'+money(s.prior_result)+'</b><small>Variação anual</small><strong class="'+sign(s.yoy_pct)+'">'+pct(s.yoy_pct)+'</strong></div></aside>';
  }
  function render(){
    const year=Number($("year").value),area=$("area").value||null,s=F.summarize(data.rows,year,area),monthly=F.monthly(data.rows,year,area),drivers=F.drivers(data.rows,year,area);
    const worst=[...drivers].sort((a,b)=>a.variance-b.variance)[0];
    const advanced=['buildup','drivers','monthly','forecast'].includes(view),cut=Number($('cutoff').value);
    $('month-control').hidden=!advanced;
    const scenarioViews=['buildup','drivers','forecast'].includes(view);
    $('scenario-controls').hidden=!scenarioViews;
    const intro='<div class="intro"><div><h2>'+({executive:"Visão executiva",budget:"Orçado × realizado",buildup:"Build-up de gastos",drivers:"Motivadores do resultado",monthly:"Visão mensal",forecast:"Projeção / EAC",areas:"Áreas e categorias"}[view])+'</h2><p>'+year+' · '+esc(area?names[area]:'Todas as áreas')+(advanced?' · referência '+months[cut-1]:' · resultado operacional simplificado')+'</p></div><span class="badge">'+(advanced&&view!=='monthly'?'Projeção hipotética':'Caso de portfólio')+'</span></div>';
    if(advanced){
      const revenue=Number($('revenue-change').value),expenses=Number($('expense-change').value);
      if(scenarioViews&&($('revenue-change').value===''||$('expense-change').value===''||!Number.isFinite(revenue)||!Number.isFinite(expenses)||Math.abs(revenue)>100||Math.abs(expenses)>100)){
        $('content').innerHTML=intro+'<div class="panel" role="alert">Preencha as duas premissas com números entre −100% e 100%.</div>';return;
      }
      $('content').innerHTML=intro+window.AdvancedReport.render(view,data,year,cut,area,{name:$('forecast-case').value,revenue:revenue/100,expenses:expenses/100});return;
    }
    const executiveCards=card("Receita realizada",money(s.actual.revenue),"Orçado: "+money(s.budget.revenue))+card("Gastos realizados",money(s.actual.expenses),"Orçado: "+money(s.budget.expenses))+card("Resultado realizado",money(s.actual.result),pct(s.variance_pct)+" frente ao orçamento",sign(s.variance))+card("Margem realizada",pct(s.actual.margin),"Orçada: "+pct(s.budget.margin));
    const budgetCards=card("Resultado orçado",money(s.budget.result),"Referência do período")+card("Resultado realizado",money(s.actual.result),"Receitas menos gastos")+card("Desvio do resultado",money(s.variance),"Realizado − orçado",sign(s.variance))+card("Desvio percentual",pct(s.variance_pct),"Base: resultado orçado absoluto",sign(s.variance));
    let content=intro+'<div class="cards">'+(view==="executive"?executiveCards:budgetCards)+"</div>";
    if(view==="executive"){
      content+='<div class="grid"><section class="panel chart-panel"><h3>Evolução do resultado</h3><p class="sub">Resultado mensal em R$ mil · orçamento como referência</p>'+lineChart(monthly)+'<div class="legend"><span><i class="dot" style="background:#8c9cb2"></i>Orçado</span><span><i class="dot" style="background:#3157c5"></i>Realizado</span></div></section>'+attention(s,monthly,drivers)+'</div>';
    }else if(view==="budget"){
      content+='<div class="grid"><section class="panel chart-panel"><h3>Orçamento e resultado mensal</h3><p class="sub">Valores em R$ mil · comparação com a mesma base de meses</p>'+lineChart(monthly)+'<div class="legend"><span><i class="dot" style="background:#8c9cb2"></i>Orçado</span><span><i class="dot" style="background:#3157c5"></i>Realizado</span></div></section>'+attention(s,monthly,drivers)+'</div>';
    }else{
      content+='<div class="grid equal"><section class="panel"><h3>Impactos no resultado</h3><p class="sub">Contribuição de cada categoria ao desvio, em reais</p>'+driverChart(drivers)+'</section><section class="panel"><h3>Comparação das áreas</h3><p class="sub">Resultado realizado e referência orçada</p>'+areaBars(year,area)+'</section></div>';
      content+='<div class="panel table-panel"><h3>Detalhamento por categoria</h3><p class="sub">Receitas positivas e despesas negativas · valores em reais</p><div class="table-scroll"><table><thead><tr><th>Categoria</th><th>Orçado</th><th>Realizado</th><th>Impacto no resultado</th></tr></thead><tbody>'+drivers.map(d=>'<tr><td>'+esc(cats[d.category_id])+'</td><td>'+money(d.budget)+'</td><td>'+money(d.actual)+'</td><td class="'+sign(d.variance)+'">'+money(d.variance)+'</td></tr>').join('')+'<tr class="total"><td>Resultado</td><td>'+money(s.budget.result)+'</td><td>'+money(s.actual.result)+'</td><td class="'+sign(s.variance)+'">'+money(s.variance)+'</td></tr></tbody></table></div></div>';
    }
    const state=s.variance<0?"abaixo":"acima";
    if(view==='areas')content+='<div class="insight"><strong>Leitura do período</strong>'+(s.variance===0?'O resultado ficou em linha com o orçamento.':'O resultado ficou '+money(Math.abs(s.variance))+' '+state+' do orçamento.')+' '+(worst.variance<0?esc(cats[worst.category_id])+' foi a categoria com maior contribuição desfavorável: '+money(worst.variance)+'.':'As categorias não apresentaram desvios desfavoráveis.')+'</div>';
    if(view!=="areas")content+=monthlyTable(monthly,s);
    content+='<details><summary>Como os indicadores são calculados</summary><p>Os dados são fictícios. Receitas têm sinal positivo; custos e despesas, negativo. O resultado é a soma dos valores. Gastos são exibidos em magnitude positiva. A margem divide resultado por receita; percentuais sem denominador ou histórico comparável aparecem como —. O resultado não inclui impostos ou resultado financeiro.</p></details>';
    $("content").innerHTML=content;
  }
  document.querySelectorAll("nav button").forEach(button=>button.addEventListener("click",()=>{
    view=button.dataset.view;document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-selected",String(b===button)));render();
  }));
  $('forecast-case').addEventListener('change',selectCase);
  for(const [id,key] of [['revenue-change','revenue'],['expense-change','expenses']])$(id).addEventListener('change',()=>{cases[$('forecast-case').value][key]=$(id).value===''?'':Number($(id).value);render();});
  $('reset-cases').addEventListener('click',()=>{Object.assign(cases,{Base:{revenue:0,expenses:0},Otimista:{revenue:5,expenses:-3},Conservativo:{revenue:-5,expenses:3}});selectCase();});
  $("year").addEventListener("change",render);$("area").addEventListener("change",render);$("cutoff").addEventListener("change",render);render();
})();
