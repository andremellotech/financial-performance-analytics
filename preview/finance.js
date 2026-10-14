(function(global){
  "use strict";
  const cents=r=>Math.round(Number(r.amount_brl)*100);
  function aggregate(rows){
    if(!rows.length)return {revenue:null,expenses:null,result:null,margin:null};
    let revenue=0,expenses=0;
    for(const r of rows)r.category_id==="REV"?revenue+=cents(r):expenses-=cents(r);
    return {revenue:revenue/100,expenses:expenses/100,result:(revenue-expenses)/100,margin:revenue?(revenue-expenses)/revenue:null};
  }
  function summarize(rows,year,area=null){
    if(!rows.some(r=>Number(r.month.slice(0,4))===year))throw new Error("Ano sem dados.");
    if(area&&!rows.some(r=>r.area_id===area))throw new Error("Área desconhecida.");
    const selected=rows.filter(r=>Number(r.month.slice(0,4))===year&&(!area||r.area_id===area));
    const budget=aggregate(selected.filter(r=>r.scenario==="Orçado")),actual=aggregate(selected.filter(r=>r.scenario==="Realizado"));
    const variance=actual.result!==null&&budget.result!==null?Math.round((actual.result-budget.result)*100)/100:null;
    const prior=aggregate(rows.filter(r=>Number(r.month.slice(0,4))===year-1&&(!area||r.area_id===area)&&r.scenario==="Realizado")).result;
    return {year,area_id:area,budget,actual,variance,variance_pct:budget.result?variance/Math.abs(budget.result):null,
      prior_result:prior,yoy_pct:prior?(actual.result-prior)/Math.abs(prior):null};
  }
  function monthly(rows,year,area=null){
    return Array.from({length:12},(_,i)=>{
      const selected=rows.filter(r=>r.month===year+"-"+String(i+1).padStart(2,"0")+"-01"&&(!area||r.area_id===area));
      const budget=aggregate(selected.filter(r=>r.scenario==="Orçado")),actual=aggregate(selected.filter(r=>r.scenario==="Realizado"));
      return {month:i+1,budget,actual,variance:Math.round((actual.result-budget.result)*100)/100};
    });
  }
  function drivers(rows,year,area=null){
    const ids=["REV","DIR","PES","TEC","COM","ADM"];
    return ids.map(id=>{
      const selected=rows.filter(r=>Number(r.month.slice(0,4))===year&&r.category_id===id&&(!area||r.area_id===area));
      const budget=selected.filter(r=>r.scenario==="Orçado").reduce((s,r)=>s+cents(r),0);
      const actual=selected.filter(r=>r.scenario==="Realizado").reduce((s,r)=>s+cents(r),0);
      return {category_id:id,budget:budget/100,actual:actual/100,variance:(actual-budget)/100};
    });
  }
  function checkCut(cut){if(!Number.isInteger(cut)||cut<1||cut>12)throw new Error('Mês de referência inválido.');}
  function period(rows,year,cut,area=null){
    checkCut(cut);summarize(rows,year,area);
    return {year,cutoff:cut,area_id:area,month:summarize(rows.filter(r=>Number(r.month.slice(5,7))===cut),year,area),
      ytd:summarize(rows.filter(r=>Number(r.month.slice(5,7))<=cut),year,area)};
  }
  function projection(rows,year,cut,area=null){
    checkCut(cut);const annual=summarize(rows,year,area);
    const selected=rows.filter(r=>Number(r.month.slice(0,4))===year&&(!area||r.area_id===area));
    const actual=selected.filter(r=>r.scenario==='Realizado'&&Number(r.month.slice(5,7))<=cut);
    const remaining=selected.filter(r=>r.scenario==='Orçado'&&Number(r.month.slice(5,7))>cut);
    const sum=(source,id)=>source.filter(r=>r.category_id===id).reduce((s,r)=>s+cents(r),0);
    const categories=['REV','DIR','PES','TEC','COM','ADM'].map(id=>{
      const b=sum(selected.filter(r=>r.scenario==='Orçado'),id),a=sum(actual,id),p=sum(remaining,id);
      return {category_id:id,budget:b/100,actual_to_date:a/100,remaining:p/100,eac:(a+p)/100,variance:(a+p-b)/100};
    });
    const zero={revenue:0,expenses:0,result:0,margin:null},eac=aggregate(actual.concat(remaining));
    const variance=Math.round((eac.result-annual.budget.result)*100)/100,costs=categories.filter(c=>c.category_id!=='REV');
    return {year,cutoff:cut,area_id:area,budget:annual.budget,actual_to_date:actual.length?aggregate(actual):{...zero},remaining:remaining.length?aggregate(remaining):{...zero},eac,
      variance,variance_pct:annual.budget.result?variance/Math.abs(annual.budget.result):null,
      expense_variance:Math.round((annual.budget.expenses-eac.expenses)*100)/100,
      expense_savings:Math.round(costs.reduce((s,c)=>s+Math.max(c.variance,0),0)*100)/100,
      expense_overruns:Math.round(costs.reduce((s,c)=>s+Math.max(-c.variance,0),0)*100)/100,categories};
  }
  function scenarioProjection(rows,year,cut,area=null,revenueChange=0,expenseChange=0){
    for(const rate of [revenueChange,expenseChange])if(typeof rate!=='number'||!Number.isFinite(rate)||rate< -1||rate>1)throw new Error('Premissas devem estar entre -100% e 100%.');
    const p=projection(rows,year,cut,area),selected=rows.filter(r=>Number(r.month.slice(0,4))===year&&(!area||r.area_id===area)),future=[],schedule=[];
    for(let month=1;month<=12;month++){
      const current=selected.filter(r=>Number(r.month.slice(5,7))===month),budget=current.filter(r=>r.scenario==='Orçado'),projected=[];
      if(month>cut)for(const id of ['REV','DIR','PES','TEC','COM','ADM']){
        const source=budget.filter(r=>r.category_id===id).reduce((s,r)=>s+cents(r),0),rate=id==='REV'?revenueChange:expenseChange;
        const amount=Math.sign(source)*Math.round(Math.abs(source)*(1+rate)+1e-8);
        projected.push({category_id:id,amount_brl:(amount/100).toFixed(2)});
      }
      future.push(...projected);
      schedule.push({month,budget:aggregate(budget),active:aggregate(month<=cut?current.filter(r=>r.scenario==='Realizado'):projected),origin:month<=cut?'Realizado':'Projetado'});
    }
    const actual=selected.filter(r=>r.scenario==='Realizado'&&Number(r.month.slice(5,7))<=cut),zero={revenue:0,expenses:0,result:0,margin:null};
    p.remaining=future.length?aggregate(future):{...zero};p.eac=aggregate(actual.concat(future));
    for(const c of p.categories){const remaining=future.filter(r=>r.category_id===c.category_id).reduce((s,r)=>s+cents(r),0),total=Math.round(c.actual_to_date*100)+remaining;c.remaining=remaining/100;c.eac=total/100;c.variance=(total-Math.round(c.budget*100))/100;}
    const costs=p.categories.filter(c=>c.category_id!=='REV');
    p.variance=Math.round((p.eac.result-p.budget.result)*100)/100;p.variance_pct=p.budget.result?p.variance/Math.abs(p.budget.result):null;
    p.expense_variance=Math.round((p.budget.expenses-p.eac.expenses)*100)/100;p.expense_savings=Math.round(costs.reduce((s,c)=>s+Math.max(c.variance,0),0)*100)/100;p.expense_overruns=Math.round(costs.reduce((s,c)=>s+Math.max(-c.variance,0),0)*100)/100;
    return {...p,revenue_change:revenueChange,expense_change:expenseChange,monthly:schedule};
  }
  const api={summarize,monthly,drivers,period,projection,scenarioProjection};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;else global.Finance=api;
})(typeof globalThis!=="undefined"?globalThis:this);
