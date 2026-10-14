const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const F=require('../preview/finance.js'),data=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/dashboard.json'),'utf8'));
assert.equal(typeof F.scenarioProjection,'function','Falta forecast com premissas');
for(const ref of data.projection_reference) {
  const p=F.scenarioProjection(data.rows,ref.year,ref.cutoff,ref.area_id);
  assert.deepEqual(p.eac,ref.eac);
}
const before=JSON.stringify(data.rows),base=F.projection(data.rows,2025,9);
const p=F.scenarioProjection(data.rows,2025,9,null,.05,-.03);
assert.deepEqual(p.actual_to_date,base.actual_to_date);
assert(p.eac.revenue>base.eac.revenue&&p.eac.expenses<base.eac.expenses);
assert.equal(JSON.stringify(data.rows),before);
assert.deepEqual(F.scenarioProjection(data.rows,2025,12,null,.05,-.03).eac,F.summarize(data.rows,2025).actual);
for(const rate of [NaN,Infinity,null,true,-1.01,1.01,'5']) assert.throws(()=>F.scenarioProjection(data.rows,2025,9,null,rate,0));
for(const ref of data.scenario_reference||[]) {
  const value=F.scenarioProjection(data.rows,ref.year,ref.cutoff,ref.area_id,ref.revenue_change,ref.expense_change);
  for(const key of ['revenue','expenses','result','margin']) assert(ref.eac[key]===null?value.eac[key]===null:Math.abs(value.eac[key]-ref.eac[key])<1e-8);
  for(const key of ['revenue','expenses','result']) assert(Math.abs(value.monthly.reduce((s,m)=>s+m.active[key],0)-value.eac[key])<.001);
}
console.log('Forecast: premissas, fonte preservada, histórico e reconciliação dos cenários válidos.');
const vm=require('node:vm'),context={Finance:F};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../preview/advanced.js'),'utf8'),context);
assert.doesNotThrow(()=>context.AdvancedReport.render('monthly',data,2025,9,null,{name:'Base',revenue:1.01,expenses:0}),'Visão mensal deve ignorar premissas de forecast inválidas');
