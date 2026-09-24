// Regression: direct bridge order must obey the same completed-bridge gate as commandAvailability/workBridge.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
function shipped(name) {
  const start = html.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `Missing shipped function: ${name}`);
  const open = html.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < html.length; i++) {
    if (html[i] === '{') depth++;
    else if (html[i] === '}' && --depth === 0) return html.slice(start, i + 1);
  }
  assert.fail(`Unterminated shipped function: ${name}`);
}
assert.match(
  html.slice(html.indexOf('function workBridge(u,target)'), html.indexOf('function fenceCoreAt')),
  /missing<=0\)return false/,
  'Native-derived bridge worker refuses DF100 completed bridge work'
);

function scenario({tile = 58, power = 100, z = 3, bank = 3, resource = 5000, upper = 0} = {}) {
  const cell = {x: 16, y: 7, z, v: tile};
  const tiles = new Map([[`16,7,${z}`, tile]]);
  if (upper) tiles.set(`16,7,${z+1}`, upper);
  const TEST = {
    tileAt: (x,y,zz) => tiles.get(`${x},${y},${zz}`) || 0,
    route: () => [],
    getResources: () => [resource,5000,5000,5000],
    getCellPower: (x,y,zz) => x===16 && y===7 && zz===z ? power : 0,
    originalActionAdjacent: (u,target) =>
      Math.abs(Math.floor(u.x)-target.x)+Math.abs(Math.floor(u.y)-target.y)===1 &&
      target.z-Math.round(u.z)>=-2 && target.z-Math.round(u.z)<=3,
    fortressTargetAt: () => null,
  };
  const units = [];
  const cellTop = (x,y) => x===15 && y===7 ? {z:bank} : null;
  const DIR8 = [[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
  const bestAdjacentRoute = new Function('TEST','cellTop','DIR8', `return (${shipped('bestAdjacentRoute')})`)(TEST,cellTop,DIR8);
  const bridgeOrderStand = new Function('TEST','bestAdjacentRoute', `return (${shipped('bridgeOrderStand')})`)(TEST,bestAdjacentRoute);
  const armWork = new Function(`return (${shipped('armWork')})`)();
  const issueBridge = new Function('bridgeOrderStand','armWork', `return (${shipped('issueBridge')})`)(bridgeOrderStand,armWork);
  const availability = new Function('TEST','units','bestAdjacentRoute','bridgeOrderStand',
    `return (${shipped('commandAvailability')})`)(TEST,units,bestAdjacentRoute,bridgeOrderStand);
  const unit = {f:0,alive:true,type:'soldier',x:14.5,y:7.5,z:bank,strength:400,
    actionCode:3,state:3,unitWord:3,manualOrder:'defend'};
  return {cell,unit,availability,issueBridge};
}

{
  const q = scenario({tile:58,power:100});
  assert.equal(q.availability(q.unit,q.cell).bridge,false,'Menu correctly hides bridge work for DF100');
  assert.equal(q.issueBridge(q.unit,q.cell,'auto'),false,'Direct order must reject completed bridge DF100');
  assert.equal(q.unit.actionCode,3,'Rejected completed bridge must preserve previous action');
  assert.equal(q.unit.manualOrder,'defend','Rejected completed bridge must preserve manual order');
}
{
  const q = scenario({tile:58,power:70});
  assert.equal(q.availability(q.unit,q.cell).bridge,true,'Damaged completed bridge remains repairable');
  assert.equal(q.issueBridge(q.unit,q.cell,'auto'),true,'Damaged completed bridge order remains accepted');
}
{
  const q = scenario({tile:69,power:50});
  assert.equal(q.issueBridge(q.unit,q.cell,'auto'),true,'Damaged bridge tile remains repairable');
}
{
  const q = scenario({tile:83,power:0,z:2,bank:3});
  assert.equal(q.issueBridge(q.unit,q.cell,'auto'),true,'Water remains a valid new bridge target');
}
console.log('PASS bridge command validity: DF100 rejected; repair and new construction preserved');
