// V187 regression: original Action 8 repeat planning excludes the acting faction's own production base.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');

function shipped(name){
  const start=html.indexOf(`function ${name}(`);
  assert.notEqual(start,-1,`missing shipped ${name}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail(`unterminated shipped ${name}`);
}

const source=shipped('repeatCandidateFromStand');

function scenario(tile,faction=0){
  const CARD=[0,2,4,6];
  const DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
  const surfaceH=new Int16Array(32*32);surfaceH.fill(-1);
  const surfaceChip=new Uint8Array(32*32);
  surfaceH[10*32+9]=2;
  surfaceChip[10*32+9]=tile;
  const units=[];
  const isBuildableSurface=()=>false;
  const ownBaseNearby=()=>false;
  const fenceCoreAt=()=>null;
  const tileAt=()=>0;
  const fortressTargetAt=()=>null;
  const factionCastleHP=[400,400,400,400];
  const fn=new Function(
    'CARD','DIRS','surfaceH','surfaceChip','units','isBuildableSurface','ownBaseNearby','fenceCoreAt','tileAt','fortressTargetAt','factionCastleHP',
    `return (${source})`
  )(CARD,DIRS,surfaceH,surfaceChip,units,isBuildableSurface,ownBaseNearby,fenceCoreAt,tileAt,fortressTargetAt,factionCastleHP);
  const u={f:faction,alive:true,type:'soldier',strength:100,x:10.5,y:10.5,z:2};
  return fn(u,'destroyBase',{x:10,y:10,z:2});
}

assert.equal(scenario(29,0),null,'faction 0 must skip own tile 29');
assert.deepEqual(
  scenario(30,0),
  {action:8,x:9,y:10,z:2,standX:10,standY:10,standZ:2},
  'enemy production base remains a valid Action 8 repeat target'
);
assert.equal(scenario(32,3),null,'faction 3 must skip own tile 32');
console.log('PASS continue destroy-base excludes own production base and keeps enemy target');
