const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const Finance=require("../preview/finance.js");
const data=JSON.parse(fs.readFileSync(path.join(__dirname,"../data/dashboard.json"),"utf8"));
for(const ref of data.reference){
  const s=Finance.summarize(data.rows,ref.year,ref.area_id);
  for(const scenario of ["budget","actual"])
    for(const key of ["revenue","expenses","result","margin"]){
      const expected=ref[scenario][key],value=s[scenario][key];
      assert(expected===null?value===null:Math.abs(value-expected)<.000001);
    }
  for(const key of ["variance","variance_pct","prior_result","yoy_pct"]){
    assert(ref[key]===null?s[key]===null:Math.abs(s[key]-ref[key])<.000001);
  }
}
assert.throws(()=>Finance.summarize(data.rows,2026));
assert.throws(()=>Finance.summarize(data.rows,2025,"BAD"));
const zero=data.rows.map(r=>({...r,amount_brl:r.scenario==="Orçado"||r.category_id==="REV"?"0.00":r.amount_brl}));
assert.equal(Finance.summarize(zero,2025).variance_pct,null);
assert.equal(Finance.summarize(zero,2025).actual.margin,null);
const monthly=Finance.monthly(data.rows,2025,null);
assert.equal(monthly.length,12);
assert(Math.abs(monthly.reduce((s,m)=>s+m.actual.result,0)-Finance.summarize(data.rows,2025).actual.result)<.01);
const drivers=Finance.drivers(data.rows,2025,null);
assert(Math.abs(drivers.reduce((s,d)=>s+d.variance,0)-Finance.summarize(data.rows,2025).variance)<.01);
console.log("Prévia: 8 filtros reconciliados, casos zero e decomposição do desvio válidos.");
assert.equal(typeof Finance.projection,'function','Falta o cálculo do EAC em JavaScript');
assert.equal(typeof Finance.period,'function','Falta o recorte mensal/acumulado');
for(const ref of data.projection_reference){
  const p=Finance.projection(data.rows,ref.year,ref.cutoff,ref.area_id);
  for(const scenario of ['budget','actual_to_date','remaining','eac'])for(const key of ['revenue','expenses','result','margin'])
    assert(ref[scenario][key]===null?p[scenario][key]===null:Math.abs(p[scenario][key]-ref[scenario][key])<.000001);
  for(const key of ['variance','variance_pct','expense_variance','expense_savings','expense_overruns'])
    assert(ref[key]===null?p[key]===null:Math.abs(p[key]-ref[key])<.000001);
  p.categories.forEach((c,i)=>{for(const key of ['budget','actual_to_date','remaining','eac','variance'])assert(Math.abs(c[key]-ref.categories[i][key])<.000001);});
}
for(const ref of data.period_reference){
  const p=Finance.period(data.rows,ref.year,ref.cutoff,ref.area_id);
  for(const part of ['month','ytd'])for(const scenario of ['budget','actual'])for(const key of ['revenue','expenses','result','margin'])
    assert(ref[part][scenario][key]===null?p[part][scenario][key]===null:Math.abs(p[part][scenario][key]-ref[part][scenario][key])<.000001);
}
for(const cut of [0,13,1.5,true])assert.throws(()=>Finance.projection(data.rows,2025,cut));
const future=data.rows.map(r=>({...r,amount_brl:r.month>'2025-09-01'&&r.scenario==='Realizado'?'0.00':r.amount_brl}));
assert.deepEqual(Finance.projection(future,2025,9).eac,Finance.projection(data.rows,2025,9).eac);
console.log('EAC: 96 recortes e 24 resumos mensais reconciliados; sem realizado futuro na projeção.');
