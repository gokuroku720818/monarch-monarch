// Exercise the shipped touch adapter, extracted verbatim from the full game.
// No browser installation needed for the GitHub Actions regression gate.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(process.argv[2] || 'index.html','utf8');
const start=html.indexOf(" game.style.touchAction='none';");
const end=html.indexOf(" game.addEventListener('contextmenu'",start);
assert.ok(start>=0&&end>start,'Touch adapter not found');
const adapter=html.slice(start,end);
function mockTarget(){const handlers=new Map();return {
 style:{},addEventListener:(type,fn)=>{const a=handlers.get(type)||[];a.push(fn);handlers.set(type,a)},
 dispatchEvent:(e)=>{for(const fn of handlers.get(e.type)||[])fn(e)},
 getBoundingClientRect:()=>({left:0,top:0,right:500,bottom:500})
}}
const game=mockTarget(),window=mockTarget(),mouse=[];
const dispatchGame=game.dispatchEvent.bind(game);
game.dispatchEvent=(e)=>{if(e.type.startsWith('mouse'))mouse.push(e.type);dispatchGame(e)};
const sandbox={game,window,MouseEvent:function(type,opts){this.type=type;Object.assign(this,opts)},
 cancelAbandonedRange:()=>{},Array};
vm.createContext(sandbox);
vm.runInContext(adapter,sandbox);
const event=(type,id)=>({type,touches:type==='touchend'?[]:[{identifier:id}],changedTouches:[{identifier:id,clientX:10,clientY:10}],preventDefault:()=>{}});
function fire(target,type,id){target.dispatchEvent(event(type,id))}
fire(game,'touchstart',101);
window.dispatchEvent({type:'blur'});
fire(game,'touchstart',202);
fire(window,'touchmove',202);
fire(window,'touchend',202);
assert.deepEqual(mouse,['mousedown','mousedown','mousemove','mouseup'],'stale first finger must not block new marquee after blur');
console.log('PASS: mobile touch adapter recovers after blur and lost touchend');
