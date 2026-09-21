// Test the shipped order functions, not a reimplementation of their logic.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
function shipped(name) {
  const match = html.match(new RegExp(`function ${name}\\([^\\n]*`));
  assert.ok(match, `Missing shipped ${name}`);
  return match[0];
}
const bestSource = shipped('bestAdjacentRoute');
const orderSource = shipped('issueFence');
const armSource = shipped('armWork');
const availabilitySource=shipped('commandAvailability');

function fixture(heights, tile = 1, cellZ = 2) {
  const cell = {x: 16, y: 7, z: cellZ, v: tile};
  const tiles = new Map([[`16,7,${cellZ}`, tile]]);
  if(tile === 40) tiles.set('16,7,3', 41);
  const TEST = {
    tileAt: (x,y,z) => tiles.get(`${x},${y},${z}`) || 0,
    route: (u,x,y,z) => heights.has(`${Math.floor(x)},${Math.floor(y)}`) ? [] : null,
    originalActionAdjacent: (u,t) => Math.abs(Math.floor(u.x)-t.x) + Math.abs(Math.floor(u.y)-t.y) === 1 && t.z-Math.round(u.z)>=-2 && t.z-Math.round(u.z)<=3
  };
  const cellTop = (x,y) => {
    const z = heights.get(`${x},${y}`);
    return z == null ? null : {z};
  };
  const DIR8 = [[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
  const bestAdjacentRoute = new Function('TEST','cellTop','DIR8',`return (${bestSource});`)(TEST,cellTop,DIR8);
  const armWork = new Function(`return (${armSource});`)();
  const issueFence = new Function('TEST','bestAdjacentRoute','armWork',`return (${orderSource});`)(TEST,bestAdjacentRoute,armWork);
  const commandAvailability = new Function('units','TEST','bestAdjacentRoute','bridgeOrderStand',`return (${availabilitySource});`)([],TEST,bestAdjacentRoute,()=>null);
  const unit = {f:0,alive:true,type:'soldier',strength:500,x:14.5,y:7.5,z:5,actionCode:1,unitWord:1};
  return {unit,cell,issueFence,commandAvailability,TEST};
}
{
  // Construction is at z=3: left bank z=6 cannot work (-3), right bank z=5 can (-2).
  const f=fixture(new Map([['15,7',6],['17,7',5]]));
  assert.equal(f.commandAvailability(f.unit,f.cell).fence,true,'Reachable bank enables fence command');
  assert.equal(f.issueFence(f.unit,f.cell,'auto'),true);
  assert.deepEqual(f.unit.target,{x:17.5,y:7.5,z:5},'Order must choose an actually reachable working position');
  assert.equal(f.unit.actionTarget.z,3,'Fence action target is at the construction height');
  assert.equal(f.TEST.originalActionAdjacent(f.unit,f.unit.actionTarget),false,'Unit is not yet beside the work cell');
}
{
  const f=fixture(new Map([['15,7',6],['17,7',7]]));
  assert.equal(f.commandAvailability(f.unit,f.cell).fence,false,'Unreachable bank must not enable fence command');
  assert.equal(f.issueFence(f.unit,f.cell,'auto'),false,'No bank can reach fence at z=3');
  assert.equal(f.unit.actionCode,1,'Rejected order must not overwrite the current action');
}
{
  const f=fixture(new Map([['15,7',5]]),41,3);
  assert.equal(f.issueFence(f.unit,f.cell,'auto'),true,'Existing fence still has a valid work command');
  assert.equal(f.unit.actionTarget.z,3);
}
{
  const f=fixture(new Map([['15,7',5]]),40,4);
  assert.equal(f.issueFence(f.unit,f.cell,'auto'),true,'Top half of fence resolves to lower core');
  assert.equal(f.unit.actionTarget.z,3);
}
console.log('PASS: fence orders choose reachable work stands and reject unreachable construction');
