// Regression gate: execute the real workBridge() source shipped in index.html.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const source = html.match(/function workBridge\(u,target\)\{[\s\S]*?\n \}/)?.[0];
assert.ok(source, 'Shipped workBridge function must be present');
function fixture(unitZ, waterZ = 2) {
  const tiles = new Map([[`16,7,${waterZ}`, 87]]);
  const funds = [5000, 5000, 5000, 5000];
  const adjacent = (u, target) =>
    Math.abs(Math.floor(u.x) - target.x) + Math.abs(Math.floor(u.y) - target.y) === 1 &&
    target.z - Math.round(u.z) >= -2 && target.z - Math.round(u.z) <= 3;
  const tileAt = (x, y, z) => tiles.get(`${x},${y},${z}`) || 0;
  const setWorldTile = (x, y, z, value) => tiles.set(`${x},${y},${z}`, value);
  const workBridge = new Function('originalActionAdjacent', 'tileAt', 'factionResource', 'setWorldTile',
    `return (${source});`)(adjacent, tileAt, funds, setWorldTile);
  const u = { alive: true, type: 'soldier', f: 0, x: 15.5, y: 7.5, z: unitZ, originalFrameFlags: 0 };
  const target = { x: 16, y: 7, z: waterZ };
  return { u, target, tiles, funds, workBridge };
}
{
  const f = fixture(5); // The deck is z=3 (reachable), although water z=2 is out of range.
  assert.equal(f.workBridge(f.u, f.target), true, 'A valid deck-height order must place a scaffold');
  assert.equal(f.tiles.get('16,7,3'), 80, 'Scaffold must be one level above water');
  assert.equal(f.target.z, 3, 'Subsequent work must target the deck');
  assert.equal(f.funds[0], 4980, 'Original 20 resource cost remains unchanged');
}
{
  const f = fixture(6); // Deck itself is 3 levels down: genuinely unreachable.
  assert.equal(f.workBridge(f.u, f.target), false, 'Unreachable deck must remain forbidden');
  assert.equal(f.funds[0], 5000, 'A failed order cannot consume resources');
}
{
  const f = fixture(2);
  assert.equal(f.workBridge(f.u, f.target), true, 'Ordinary adjacent bridge remains functional');
}
// The action dispatcher must also use deck height, otherwise it never calls workBridge.
assert.ok(html.includes('else if(originalActionAdjacent(u,{x:a.x,y:a.y,z:(t>=83&&t<=110)?a.z+1:a.z}))'),
  'Action 5 dispatcher must use the bridge deck height');
console.log('PASS: bridge command and work share deck height; original cost and reach preserved');
