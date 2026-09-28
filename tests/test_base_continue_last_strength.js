// V185 regression: original continue-build planning must not stop at strength 1.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
function shipped(name){
  const start=html.indexOf(`function ${name}(`);assert.notEqual(start,-1,`missing ${name}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail(`unterminated ${name}`);
}
const source=shipped('repeatCandidateFromStand');
function scenario(strength,resource=100){
  const factionResource=[resource,0,0,0];
  const CARD=[0,2,4,6];
  const DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
  const surfaceH=new Int16Array(32*32);surfaceH.fill(-1);
  const surfaceChip=new Uint8Array(32*32);
  surfaceH[10*32+11]=2;surfaceChip[10*32+11]=1;
  const units=[];
  const isBuildableSurface=t=>t===1;
  const ownBaseNearby=()=>false;
  const fenceCoreAt=()=>null;
  const tileAt=()=>0;
  const fortressTargetAt=()=>null;
  const factionCastleHP=[0,0,0,0];
  const fn=new Function('factionResource','CARD','DIRS','surfaceH','surfaceChip','units','isBuildableSurface','ownBaseNearby','fenceCoreAt','tileAt','fortressTargetAt','factionCastleHP',`return (${source})`)(
    factionResource,CARD,DIRS,surfaceH,surfaceChip,units,isBuildableSurface,ownBaseNearby,fenceCoreAt,tileAt,fortressTargetAt,factionCastleHP
  );
  return fn({f:0,alive:true,type:'soldier',strength,x:10.5,y:10.5,z:2},'base',{x:10,y:10,z:2});
}
assert.deepEqual(scenario(1),{action:4,x:11,y:10,z:2,standX:10,standY:10,standZ:2},'strength 1 must still find the final base target in continue mode');
assert.equal(scenario(0),null,'strength 0 cannot plan another base');
console.log('PASS continue-base final-strength planning: strength 1 allowed; strength 0 rejected');
