import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createResident} from './characters.js';

const residents=JSON.parse(execFileSync('python',['-c','import json; from world import HotelWorld; print(json.dumps(HotelWorld().residents))'],{encoding:'utf8'}));
const palette=Object.fromEntries([...readFileSync('voxel-scene.js','utf8').matchAll(/(\w+):(0x[\da-f]+)/g)].map(m=>[m[1],Number(m[2])]));
class Blocks { constructor(){this.boxes=[];} box(...a){assert.equal(a.length,7);assert.ok(a.every(Number.isFinite));assert.ok(a.slice(3,6).every(n=>n>0));this.boxes.push(a);} finish(){return this.boxes;} }
class Group {constructor(){this.userData={};this.children=[];}add(x){this.children.push(x);}}
const geometries=new Set(),portraits=new Set();
assert.equal(new Set(residents.map(r=>r.character)).size,41);
for(const r of residents){const g=createResident(r.character,Blocks,palette,{Group});assert.equal(g.userData.character,r.character);geometries.add(JSON.stringify(g.children));portraits.add(createHash('sha256').update(readFileSync(`assets/cast-${r.character}.png`)).digest('hex'));}
assert.equal(geometries.size,41,'Every resident needs distinct geometry');
assert.equal(portraits.size,41,'Every resident needs a distinct portrait');

const ctx=vm.createContext({});vm.runInContext(readFileSync('simulation.js','utf8'),ctx);
const run=vm.runInContext('makePractice()',ctx);ctx.run=run;
const move=d=>{ctx.direction=d;vm.runInContext('practiceMove(run,direction)',ctx);};
move('up');assert.equal(run.blocked,1);assert.equal(run.steps,0);
// Visit the desk without the parcel: the task must not complete early.
for(let i=0;i<4;i++)move('down');assert.equal(run.done,false);
// Use the open lower corridor, collect the parcel, then return to reception.
for(let i=0;i<6;i++)move('right');for(let i=0;i<4;i++)move('up');assert.equal(run.parcel,true);assert.equal(run.done,false);
for(let i=0;i<4;i++)move('down');for(let i=0;i<6;i++)move('left');assert.equal(run.done,true);
const steps=run.steps;move('right');assert.equal(run.steps,steps);
assert.equal(vm.runInContext('makePractice().parcel',ctx),false);
console.log('41 distinct resident geometries and portraits; parcel task collision, collection, delivery and completion checks passed.');
