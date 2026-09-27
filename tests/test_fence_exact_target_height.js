// V184 regression: Action 10 must keep the exact normalized fence core z.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
function shipped(name){
  const start=html.indexOf(`function ${name}(`);assert.notEqual(start,-1,`missing ${name}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){if(html[i]==='{')depth++;else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1)}
  assert.fail(`unterminated ${name}`);
}
function branch(startText){
  const start=html.indexOf(startText);assert.notEqual(start,-1,`missing branch ${startText}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){if(html[i]==='{')depth++;else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1)}
  assert.fail('unterminated branch');
}
const tiles=new Map([
  ['7,13,3',41],['7,13,4',40],
  ['7,13,38',41],['7,13,39',40]
]);
const powers=new Map([['7,13,3',200],['7,13,38',1]]);
const tileAt=(x,y,z)=>tiles.get(`${x},${y},${z}`)||0;
const cellPower={has:k=>powers.has(k),get:k=>powers.get(k)};
const vk=(x,y,z)=>`${x},${y},${z}`;
const surfaceH=new Int16Array(32*32);surfaceH.fill(-1);surfaceH[13*32+7]=39;
const TEST={
  tileAt,
  route:()=>[],
  originalActionAdjacent:(u,t)=>Math.abs(Math.floor(u.x)-Math.floor(t.x))+Math.abs(Math.floor(u.y)-Math.floor(t.y))===1&&Math.round(t.z)-Math.round(u.z)>=-2&&Math.round(t.z)-Math.round(u.z)<=3
};
const cellTop=(x,y)=>x===6&&y===13?{z:38}:null;
const DIR8=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
const bestAdjacentRoute=new Function('TEST','cellTop','DIR8',`return (${shipped('bestAdjacentRoute')})`)(TEST,cellTop,DIR8);
const armWork=new Function(`return (${shipped('armWork')})`)();
const issueSpecificWork=new Function('TEST','bestAdjacentRoute','armWork',`return (${shipped('issueSpecificWork')})`)(TEST,bestAdjacentRoute,armWork);
const u={f:0,alive:true,type:'soldier',strength:500,x:5.5,y:13.5,z:38,actionCode:3,state:3,unitWord:3,manualOrder:'defend'};
const clicked={x:7,y:13,z:39,v:40};
assert.equal(issueSpecificWork(u,'destroyFence',clicked,'auto'),true,'high cap destruction order accepted');
assert.equal(u.actionTarget.z,38,'upper-half click must normalize once to high core z=38');
tiles.delete('7,13,38');tiles.delete('7,13,39');powers.delete('7,13,38');surfaceH[13*32+7]=4;
const lowBefore=[tileAt(7,13,3),tileAt(7,13,4),powers.get('7,13,3')];
const destructibleCoreAt=new Function('surfaceH','tileAt','cellPower','vk',`return (${shipped('destructibleCoreAt')})`)(surfaceH,tileAt,cellPower,vk);
const originalActionAdjacent=TEST.originalActionAdjacent;
const finishWorkAction=(unit)=>{unit.actionCode=1;unit.actionTarget=null;unit.manualOrder=null;unit.finished=true};
const prepareOriginalWorkFacing=()=>true;
const attackDestructible=()=>{throw new Error('must not attack another-height fence')};
const src=branch('if(u.actionCode===10&&u.actionTarget)');
const run=new Function('u','destructibleCoreAt','finishWorkAction','originalActionAdjacent','prepareOriginalWorkFacing','attackDestructible','tileAt',`for(let __once=0;__once<1;__once++)${src};return u;`);
run(u,destructibleCoreAt,finishWorkAction,originalActionAdjacent,prepareOriginalWorkFacing,attackDestructible,tileAt);
assert.deepEqual([tileAt(7,13,3),tileAt(7,13,4),powers.get('7,13,3')],lowBefore,'low fence must remain untouched');
assert.equal(u.finished,true,'destroy action must finish once the exact stored high target disappears');
assert.equal(u.actionTarget,null,'finished action must not retarget low fence');
console.log('PASS exact-z fence destruction: normalized high target finishes without same-column retarget');
