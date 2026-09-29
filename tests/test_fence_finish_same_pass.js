// V188 regression: native Action 10 return 0 finishes the work in the same dispatcher pass.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');

function branchSource(startText){
  const start=html.indexOf(startText);assert.notEqual(start,-1,`missing ${startText}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail('unterminated branch');
}
const tiles=new Map([['7,13,38',41],['7,13,39',40]]);
const tileAt=(x,y,z)=>tiles.get(`${x},${y},${z}`)||0;
const u={alive:true,type:'soldier',actionCode:10,actionTarget:{x:7,y:13,z:38},atk:0};
const originalActionAdjacent=()=>true;
const prepareOriginalWorkFacing=()=>true;
let finishCalls=0;
const finishWorkAction=unit=>{finishCalls++;unit.actionCode=1;unit.actionTarget=null;return 1};
const attackDestructible=()=>{tiles.delete('7,13,38');tiles.delete('7,13,39');return true};
const src=branchSource('if(u.actionCode===10&&u.actionTarget)');
const run=new Function('u','tileAt','originalActionAdjacent','prepareOriginalWorkFacing','attackDestructible','finishWorkAction',
  `for(let __once=0;__once<1;__once++)${src};return u;`);
run(u,tileAt,originalActionAdjacent,prepareOriginalWorkFacing,attackDestructible,finishWorkAction);
assert.equal(tileAt(7,13,38),0,'DF0 removal must remove selected core');
assert.equal(finishCalls,1,'removal must finish Action 10 in the same dispatcher pass');
assert.equal(u.actionCode,1);
assert.equal(u.actionTarget,null);
console.log('PASS fence final removal finishes Action 10 in the same dispatcher pass');
