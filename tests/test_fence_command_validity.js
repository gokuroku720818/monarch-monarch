// Execute shipped command UI and order functions; compare to workFence constraints.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
function shipped(name){const m=html.match(new RegExp(`function ${name}\\([^\\n]*`));assert(m,`Missing ${name}`);return m[0]}
assert.match(html.slice(html.indexOf('function workFence(u,target)'),html.indexOf('function workVegetation(u,target)')), /missing<=0\)return false/);
function scenario({tile=1,z=2,power=100,upper=null,below=null,bank=3}={}){
 const cell={x:16,y:7,z,v:tile},tiles=new Map([[`16,7,${z}`,tile]]);
 if(upper!=null)tiles.set(`16,7,${z+1}`,upper);
 if(below!=null)tiles.set(`16,7,${z-1}`,below);
 const TEST={
  tileAt:(x,y,zz)=>tiles.get(`${x},${y},${zz}`)||0,
  route:()=>[],
  getCellPower:(x,y,zz)=>x===16&&y===7&&zz===(tile%2===0&&tile>=40?z-1:z)?power:0,
  originalActionAdjacent:(u,target)=>Math.abs(Math.floor(u.x)-target.x)+Math.abs(Math.floor(u.y)-target.y)===1&&target.z-Math.round(u.z)>=-2&&target.z-Math.round(u.z)<=3
 };
 const cellTop=(x,y)=>x===15&&y===7?{z:bank}:null,DIR8=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
 const bestAdjacentRoute=new Function('TEST','cellTop','DIR8',`return (${shipped('bestAdjacentRoute')})`)(TEST,cellTop,DIR8);
 const armWork=new Function(`return (${shipped('armWork')})`)();
 const issueFence=new Function('TEST','bestAdjacentRoute','armWork',`return (${shipped('issueFence')})`)(TEST,bestAdjacentRoute,armWork);
 const availability=new Function('TEST','units','bestAdjacentRoute','bridgeOrderStand',`return (${shipped('commandAvailability')})`)(TEST,[],bestAdjacentRoute,()=>null);
 const unit={f:0,alive:true,type:'soldier',x:14.5,y:7.5,z:bank,strength:400,actionCode:3,state:3,unitWord:3,manualOrder:'defend'};
 return {cell,unit,TEST,availability,issueFence};
}
function rejected(options,why){const q=scenario(options);assert.equal(q.availability(q.unit,q.cell).fence,false,`Menu enables ${why}`);assert.equal(q.issueFence(q.unit,q.cell,'auto'),false,`Order accepts ${why}`);assert.equal(q.unit.actionCode,3);assert.equal(q.unit.manualOrder,'defend')}
rejected({tile:41,z:3,power:200},'full core DF200');
rejected({tile:40,z:4,below:41,power:200},'full upper half DF200');
rejected({tile:1,z:46,bank:46},'z construction limit');
rejected({tile:1,z:2,upper:33},'occupied core');
{
 const q=scenario({tile:1,z:2}),orig=q.TEST.tileAt;
 q.TEST.tileAt=(x,y,z)=>x===16&&y===7&&z===4?33:orig(x,y,z);
 assert.equal(q.availability(q.unit,q.cell).fence,false,'occupied upper half enables menu');
 assert.equal(q.issueFence(q.unit,q.cell,'auto'),false,'occupied upper half accepts order');
}
rejected({tile:40,z:4,below:0,power:0},'orphan upper half');
for(const [name,options,z] of [['damaged core',{tile:41,z:3,power:120},3],['damaged upper half',{tile:40,z:4,below:41,power:120},3],['new fence',{tile:1,z:2,power:0},3]]){
 const q=scenario(options);
 assert.equal(q.availability(q.unit,q.cell).fence,true,`${name} unavailable`);
 assert.equal(q.issueFence(q.unit,q.cell,'auto'),true,`${name} order failed`);
 assert.equal(q.unit.actionTarget.z,z,`${name} wrong work height`);
}
console.log('PASS fence workability: complete/orphan/blocked/boundary rejected; repair and construction preserved');
