import {HotelScene} from './voxel-scene.js';

export function mountWalk(host){
  const el=id=>host.querySelector('#'+id),abort=new AbortController(),opts={signal:abort.signal};
  let scene,disposed=false,snapshot=null,me=null,sequence=0,applied=0,nearby=null,lastFrame=performance.now(),frameId,movePending=false,pollPending=false,predicted=null,lastResponse=performance.now();
  const keys=new Set(),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const status=(message,error=false)=>{el('walk-status').textContent=message;el('walk-status').classList.toggle('world-error',error);};
  function consume(data,n){if(disposed||n<applied)return;applied=n;snapshot=data;window.hotelResidentState=data.residents||[];me=data.people.find(p=>p.id===data.you);lastResponse=performance.now();
    if(!me)predicted=null;else if(!predicted||predicted.floor!==me.floor||Math.hypot(predicted.x-me.x,predicted.z-me.z)>2.5)predicted={...me};
    scene?.update(data);
    el('world-entry').hidden=!!me;el('walk-toolbar').hidden=!me;el('world-pad').hidden=!me;
    el('world-count').textContent=(data.residents||[]).filter(r=>r.floor===(me?.floor||0)).length+' residents · '+data.people.length+(data.people.length===1?' visitor':' visitors');
    el('world-location').textContent=me?(me.floor?'FLOOR '+String(me.floor).padStart(2,'0')+(me.floor===11?' · SIMULATION SUITE':' · GUEST ROOMS'):Math.abs(me.x)<21.8&&me.z<11.7?'G · THE LOBBY':'THE FRONT COURTYARD'):'G · THE LOBBY';
    el('world-position').textContent=me?`${me.name} · ${me.kind} · x ${me.x.toFixed(1)} / z ${me.z.toFixed(1)} · ${me.walking?'walking':'at rest'}`:'Hotel characters follow ambient routines.';
    if(me&&el('walk-status').textContent==='Enter the courtyard to begin.')status('Welcome back. Choose a destination or continue walking.');
    nearby=null;
    if(me&&me.floor===0)for(const target of Object.values(data.landmarks))if(target.route&&Math.hypot(me.x-target.x,me.z-target.z)<2.8){nearby=target;break;}
    if(me?.floor===11&&Math.hypot(me.x,me.z+9)<3)nearby={name:'Simulation Suite',route:'#/simulation'};
    el('world-near').hidden=!nearby;if(nearby)el('near-label').textContent=nearby.name;
    for(const option of el('walk-destination').options)option.disabled=!!me?.floor&&option.value!=='lift';
    if(me?.floor&&el('walk-destination').value!=='lift')el('walk-destination').value='lift';
  }
  async function request(command,body){const n=++sequence;const response=await fetch('/agents/api/world'+(command?'/'+command:''),{
    method:command?'POST':'GET',headers:command?{'Content-Type':'application/json'}:{},body:command?JSON.stringify(body||{}):undefined,signal:AbortSignal.any([abort.signal,AbortSignal.timeout(8000)])});
    const data=await response.json();if(!response.ok)throw Error(data.error||'The hotel could not complete that movement.');consume(data,n);return data;
  }
  async function command(name,data,feedback){keys.clear();predicted=null;try{const result=await request(name,data);if(feedback)status(feedback);return result;}catch(e){if(!disposed)status(e.name==='TypeError'?'Connection lost. Movement will resume when the hotel reconnects.':e.message,true);throw e;}}
  try{scene=new HotelScene(el('walk-canvas'),{onResident:id=>window.openResidentCard?.(id),onGround:(x,z)=>{if(me)command('target',{x,z},'Walking to the selected spot.').catch(()=>{});}});scene.decorate(2);if(window.hotelWorldInitial)scene.update(window.hotelWorldInitial);}catch(e){el('walk-canvas').innerHTML='<div class="walk-unavailable"><h3>The 3D view is unavailable.</h3><p>This browser could not start WebGL. You can still enter, choose destinations, and use the shared movement API below.</p></div>';}
  const listen=(element,event,fn)=>element.addEventListener(event,fn,opts);
  host.querySelectorAll('[data-enter]').forEach(b=>listen(b,'click',async()=>{
    host.querySelectorAll('[data-enter]').forEach(x=>x.disabled=true);
    try{await command('enter',{kind:b.dataset.enter,name:el('visitor-name').value},'Welcome to the lobby. Walk around, meet a resident, or choose a floor.');scene?.canvas.focus();}
    catch{}finally{host.querySelectorAll('[data-enter]').forEach(x=>x.disabled=false);}
  }));
  host.querySelectorAll('[data-enter]').forEach(b=>b.disabled=false);
  listen(el('walk-go'),'click',()=>command('target',{landmark:el('walk-destination').value},'Your walking route is set.').catch(()=>{}));
  listen(el('walk-lift'),'click',()=>command('floor',{floor:Number(el('walk-floor').value)},'Walking to the lift. It will take you to your selected floor.').catch(()=>{}));
  listen(el('walk-stop'),'click',()=>{keys.clear();command('stop',{},'Stopped. Take a look around.').catch(()=>{});});
  listen(el('walk-leave'),'click',()=>{keys.clear();command('leave',{},'You have left the hotel. Come back any time.').catch(()=>{});});
  const interact=()=>{if(nearby)location.hash=nearby.route.slice(1);};listen(el('world-interact'),'click',interact);
  host.querySelectorAll('[data-camera]').forEach(b=>listen(b,'click',()=>{if(!scene)return;switch(b.dataset.camera){case'left':scene.azimuth+=Math.PI/8;break;case'right':scene.azimuth-=Math.PI/8;break;case'in':scene.zoom=Math.min(1.8,scene.zoom+.15);break;case'out':scene.zoom=Math.max(.6,scene.zoom-.15);break;default:scene.azimuth=.5;scene.zoom=1;}scene.render(0);}));
  function vector(){let a=0,b=0;if(keys.has('up'))b++;if(keys.has('down'))b--;if(keys.has('right'))a++;if(keys.has('left'))a--;const angle=scene?.azimuth||0;return{dx:a*Math.cos(angle)-b*Math.sin(angle),dz:-a*Math.sin(angle)-b*Math.cos(angle)};}
  async function move(){if(!me||movePending||!keys.size||disposed)return;movePending=true;try{await request('move',vector());}catch(e){if(!disposed)status('Connection lost. Reconnecting to the hotel…',true);}finally{movePending=false;}}
  const keymap={w:'up',ArrowUp:'up',s:'down',ArrowDown:'down',a:'left',ArrowLeft:'left',d:'right',ArrowRight:'right'};
  listen(window,'keydown',e=>{if(!me||/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;const key=keymap[e.key]||keymap[e.key.toLowerCase()];if(key){e.preventDefault();keys.add(key);move();}if(e.key.toLowerCase()==='e')interact();});
  listen(window,'keyup',e=>{const key=keymap[e.key]||keymap[e.key.toLowerCase()];if(key)keys.delete(key);});
  const clearKeys=()=>{keys.clear();host.querySelectorAll('.pressed').forEach(x=>x.classList.remove('pressed'));};listen(window,'blur',clearKeys);listen(document,'visibilitychange',()=>{if(document.hidden)clearKeys();});
  host.querySelectorAll('[data-direction]').forEach(b=>{
    listen(b,'pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);keys.add(b.dataset.direction);b.classList.add('pressed');move();});
    for(const event of ['pointerup','pointercancel','lostpointercapture'])listen(b,event,()=>{keys.delete(b.dataset.direction);b.classList.remove('pressed');});
    listen(b,'click',e=>{if(e.detail===0){keys.add(b.dataset.direction);move().finally(()=>keys.delete(b.dataset.direction));}});
  });
  const movementTimer=setInterval(move,110);
  const poll=async()=>{if(pollPending||disposed||document.hidden)return;pollPending=true;try{await request();}catch(e){if(!disposed)status('Connection lost. Reconnecting to the hotel…',true);}finally{pollPending=false;}};
  const pollingTimer=setInterval(poll,250);poll();
  function openSpot(x,z,floor){if(floor?(Math.abs(x)>14.4||Math.abs(z)>11.4):(Math.abs(x)>28||z< -16||z>24))return false;return !(floor?snapshot.upper_solids:snapshot.ground_solids).some(([sx,sz,w,d])=>Math.abs(x-sx)<w/2+.35&&Math.abs(z-sz)<d/2+.35);}
  function frame(now){if(disposed)return;const dt=Math.min(.06,(now-lastFrame)/1000);lastFrame=now;
    if(me&&predicted&&snapshot){
      if(keys.size&&now-lastResponse<700){const v=vector(),length=Math.hypot(v.dx,v.dz);if(length){const dx=v.dx/length*4.5*dt,dz=v.dz/length*4.5*dt;if(openSpot(predicted.x+dx,predicted.z,me.floor))predicted.x+=dx;if(openSpot(predicted.x,predicted.z+dz,me.floor))predicted.z+=dz;predicted.heading=Math.atan2(dx,dz);}}
      else{const blend=1-Math.exp(-dt*14);predicted.x+=(me.x-predicted.x)*blend;predicted.z+=(me.z-predicted.z)*blend;predicted.heading=me.heading;}
      const visual={...me,x:predicted.x,z:predicted.z,heading:predicted.heading};scene?.update({...snapshot,people:snapshot.people.map(p=>p.id===me.id?visual:p)});
    }
    scene?.render(reduced?0:dt);frameId=requestAnimationFrame(frame);
  }frameId=requestAnimationFrame(frame);

  // A structured browser-agent surface when the browser exposes WebMCP. REST always works.
  const registered=[];
  if(navigator.modelContext?.registerTool){
    const tools=[
      ['hotel_observe','Observe your location, other visitors, destinations and collision geometry.',{},()=>request()],
      ['hotel_enter','Enter the shared voxel hotel as an agent.',{name:{type:'string'}},args=>request('enter',{kind:'agent',name:args.name||'Agent guest'})],
      ['hotel_walk_to','Walk to an available named landmark. Observe until arrival.',{landmark:{type:'string',enum:['entrance','lobby','front_desk','lounge','library','workshop','lift']}},args=>request('target',args)],
      ['hotel_take_lift','Walk to the lift and travel to floor 0 (lobby) through 11.',{floor:{type:'integer',minimum:0,maximum:11}},args=>request('floor',args)],
      ['hotel_stop','Stop the current walking route.',{},()=>request('stop',{})],
    ];
    for(const [name,description,properties,execute] of tools){try{navigator.modelContext.registerTool({name,description,inputSchema:{type:'object',properties,additionalProperties:false},execute:async args=>({content:[{type:'text',text:JSON.stringify(await execute(args))}]})});registered.push(name);}catch{}}
    if(registered.length)el('world-agent-support').textContent='Browser-agent walking tools and the HTTP movement API are available.';
  }
  return{dispose(){disposed=true;abort.abort();clearInterval(pollingTimer);clearInterval(movementTimer);cancelAnimationFrame(frameId);keys.clear();scene?.dispose();for(const name of registered)try{navigator.modelContext.unregisterTool(name);}catch{}}};
}
