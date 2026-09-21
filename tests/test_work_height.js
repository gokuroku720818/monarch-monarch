// Regression against the shipped game functions: the command screen must not
// accept or select a bank outside the native -2..+3 cardinal work range.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const source=name=>{let m=html.match(new RegExp(`function ${name}\\([^\\n]*`));assert(m,`missing shipped ${name}`);return m[0]};
const native=html.match(/function originalActionAdjacent\(u,target\)\{[\s\S]*?\n \}/);
assert(native,'native action range missing');
const originalActionAdjacent=Function('return ('+native[0]+')')();
const DIR8=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
function setup(kind, heights, v=33,z=2){
 const cell={x:16,y:7,z,v}, tile=new Map([[`16,7,${z}`,v]]);
 if(v===40)tile.set('16,7,3',41);
 const TEST={route:(u,x,y,z)=>heights.has(`${Math.floor(x)},${Math.floor(y)}`)?[]:null,
            originalActionAdjacent,tileAt:(x,y,z)=>tile.get(`${x},${y},${z}`)||0,
            fortressTargetAt:()=>null,canBuildBaseAt:()=>false,getCellPower:()=>100,getResources:()=>[1000,1000,1000,1000]};
 const cellTop=(x,y)=>heights.has(`${x},${y}`)?{z:heights.get(`${x},${y}`)}:null;
 const bestAdjacentRoute=Function('TEST','cellTop','DIR8','return ('+source('bestAdjacentRoute')+')')(TEST,cellTop,DIR8);
 const armWork=Function('return ('+source('armWork')+')')();
 const issueSpecificWork=Function('TEST','bestAdjacentRoute','armWork','return ('+source('issueSpecificWork')+')')(TEST,bestAdjacentRoute,armWork);
 const bridgeOrderStand=()=>null;
 const units=[];
 const commandAvailability=Function('TEST','units','bestAdjacentRoute','bridgeOrderStand','return ('+source('commandAvailability')+')')(TEST,units,bestAdjacentRoute,bridgeOrderStand);
 const unit={f:0,alive:true,type:'soldier',strength:500,x:14.5,y:7.5,z:5,actionCode:1,unitWord:1};
 return{unit,cell,issueSpecificWork,commandAvailability,TEST};
}
const cases=[['clear',33,2],['clear',53,2],['destroyBase',30,2],['destroyBridge',59,2],['destroyFence',41,3],['destroyFence',40,4],['seal',112,2]];
for(const [kind,tile,z] of cases){
 const targetZ=tile===40?3:z;
 const reachableZ=targetZ+2,impossibleZ=targetZ+3;
 const f=setup(kind,new Map([['15,7',impossibleZ],['17,7',reachableZ]]),tile,z);
 assert.equal(f.commandAvailability(f.unit,f.cell)[kind],true,`${kind}/${tile}: valid opposite bank enables menu`);
 assert.equal(f.issueSpecificWork(f.unit,kind,f.cell,'auto'),true,`${kind}/${tile}: command accepted`);
 assert.equal(f.unit.target.x,17.5,`${kind}/${tile}: must choose working bank, not closer invalid bank`);
 assert.equal(f.TEST.originalActionAdjacent({x:f.unit.target.x,y:f.unit.target.y,z:f.unit.target.z},{x:16,y:7,z:targetZ}),true,`${kind}/${tile}: selected stand is in native height range`);
 const bad=setup(kind,new Map([['15,7',impossibleZ],['17,7',impossibleZ+1]]),tile,z);
 assert.equal(bad.commandAvailability(bad.unit,bad.cell)[kind],false,`${kind}/${tile}: no reachable work stand disables menu`);
 assert.equal(bad.issueSpecificWork(bad.unit,kind,bad.cell,'auto'),false,`${kind}/${tile}: reject unworkable command`);
 assert.equal(bad.unit.actionCode,1,`${kind}/${tile}: failed order leaves old command intact`);
}
console.log('PASS native height filtering of 7 work cases and invalid-order preservation');
