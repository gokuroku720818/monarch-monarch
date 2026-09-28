// V186 regression: original continue-build planning selects the next base target before the 100-resource spend, then waits on Action 4 if funding is short.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');

function shipped(name){
  const start=html.indexOf(`function ${name}(`);
  assert.notEqual(start,-1,`missing ${name}`);
  const open=html.indexOf('{',start);
  let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail(`unterminated ${name}`);
}

function candidate(resource){
  const factionResource=[resource,0,0,0],CARD=[0,2,4,6],DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
  const surfaceH=new Int16Array(32*32);surfaceH.fill(-1);
  const surfaceChip=new Uint8Array(32*32);
  surfaceH[10*32+11]=2;surfaceChip[10*32+11]=1;
  const fn=new Function('factionResource','CARD','DIRS','surfaceH','surfaceChip','units','isBuildableSurface','ownBaseNearby','fenceCoreAt','tileAt','fortressTargetAt','factionCastleHP',
    `return (${shipped('repeatCandidateFromStand')})`)(
      factionResource,CARD,DIRS,surfaceH,surfaceChip,[],t=>t===1,()=>false,()=>null,()=>0,()=>null,[0,0,0,0]
    );
  return fn({f:0,alive:true,type:'soldier',strength:50,x:10.5,y:10.5,z:2},'base',{x:10,y:10,z:2});
}

assert.deepEqual(candidate(99),{action:4,x:11,y:10,z:2,standX:10,standY:10,standZ:2},
  'Original repeat planner selects the next base target even below 100 resource');

const branch=html.match(/if\(u\.actionCode===4&&u\.actionTarget&&originalActionAdjacent\(u,u\.actionTarget\)\)\{[^\n]+/);
assert.ok(branch,'missing shipped Action 4 branch');

let finished=0,attempted=0;
const factionResource=[99,0,0,0];
const u={f:0,alive:true,actionCode:4,actionTarget:{x:11,y:10,z:2},workMode:'continue',workFamily:'base'};
const originalActionAdjacent=()=>true,prepareOriginalWorkFacing=()=>true;
const tryBuildBase=()=>{attempted++;return false};
const finishWorkAction=()=>{finished++;u.actionCode=1;return 1};
const run=new Function('u','factionResource','originalActionAdjacent','prepareOriginalWorkFacing','tryBuildBase','finishWorkAction',
  `for(let __once=0;__once<1;__once++){${branch[0]}};return u.actionCode;`);

run(u,factionResource,originalActionAdjacent,prepareOriginalWorkFacing,tryBuildBase,finishWorkAction);
assert.equal(attempted,0,'Funding shortage should wait before invoking the build worker');
assert.equal(finished,0,'Funding shortage must not finish/retarget the current Action 4');
assert.equal(u.actionCode,4,'Funding shortage keeps Action 4 active for a later retry');

console.log('PASS base continue funding wait: low funds still target; Action 4 waits without finishing');
