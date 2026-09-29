// V189 regression: lm_win.exe 0x442606..0x4427f6 reconstructs same-column elevator z edges.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
function functionSource(name){
  const marker='function '+name+'(',start=html.indexOf(marker);
  assert.notEqual(start,-1,'missing '+name);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail('unterminated '+name);
}
const tiles=new Map(),x=11,y=27;
tiles.set(x+','+y+',8',120);
for(let z=9;z<=13;z++)tiles.set(x+','+y+','+z,123);
for(let z=14;z<=15;z++)tiles.set(x+','+y+','+z,122);
tiles.set(x+','+y+',16',121);
const tileAt=(x,y,z)=>tiles.get(x+','+y+','+z)||0;
const vk=(x,y,z)=>x+','+y+','+z;
const DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
const CARD=[0,2,4,6];
const resolveStep=()=>null;
const commanderBlocksRoute=()=>false;
const helper=html.includes('function originalVerticalRouteSteps(')?functionSource('originalVerticalRouteSteps'):'';
const src=functionSource('route');
const route=new Function('vk','DIRS','CARD','resolveStep','commanderBlocksRoute','tileAt',helper+';'+src+';return route;')(vk,DIRS,CARD,resolveStep,commanderBlocksRoute,tileAt);
const u={x:x+.5,y:y+.5,z:8,dir:4};
const p=route(u,x+.5,y+.5,16);
assert.ok(p,'native elevator column must produce a route');
assert.deepEqual(p.map(q=>[q.x,q.y,q.z]),Array.from({length:8},(_,i)=>[x,y,9+i]));
assert.deepEqual(p.map(q=>q.dir),[255,255,255,255,255,255,255,255]);
console.log('PASS native elevator route traverses z=8..16 vertically');
