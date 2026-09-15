import {HotelScene} from './voxel-scene.js';
import * as T from './assets/three/three.module.js';

export function mountSimulation(host) {
  const el=id=>host.querySelector('#'+id), abort=new AbortController();
  let disposed=false,busy=false,auto=false,replaying=false,run=null,world=null,scene=null,jobs={},frameId,last=performance.now(),parcel;
  const props=new T.Group();
  const listen=(node,event,fn)=>node.addEventListener(event,fn,{signal:abort.signal});
  const status=text=>el('sim-status').textContent=text;
  async function api(path='',body) {
    const response=await fetch('/agents/api/simulation'+path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,signal:abort.signal});
    const result=await response.json();
    if(!response.ok)throw Error(result.error||'The simulation request failed.');
    return result;
  }
  function draw(frame) {
    if(!run||!world)return;
    const worker={...frame.worker,id:'simulation-worker',name:'Task agent',kind:'agent',walking:false};
    scene?.update({...world,people:[worker],residents:[],you:worker.id});
    el('sim-location').textContent=worker.floor?'FLOOR '+worker.floor:'G · LOBBY';
    if(!scene)return;
    for(const child of [...props.children]){child.geometry?.dispose();child.material?.dispose();props.remove(child);}
    const next=run.task.steps[frame.phase],floor=worker.floor;
    const rings=[[run.task.source,0xd97937],[run.task.destination,0x386247],...(next?[[next.at,0x397da5]]:[])];
    for(const [spot,color] of rings)if(spot[2]===floor){
      const ring=new T.Mesh(new T.RingGeometry(.85,1.1,32),new T.MeshBasicMaterial({color,side:T.DoubleSide}));
      ring.rotation.x=-Math.PI/2;ring.position.set(spot[0],.24,spot[1]);props.add(ring);
    }
    parcel=new T.Mesh(new T.BoxGeometry(.6,.45,.5),new T.MeshLambertMaterial({color:run.task_id==='tea'?0xf8f2df:0xd6a367}));
    props.add(parcel);parcel.visible=frame.carrying||frame.phase===0&&run.task.steps[0].action==='pickup'&&run.task.source[2]===floor;
    if(frame.carrying)parcel.position.set(worker.x,1.25,worker.z+.6);else parcel.position.set(run.task.source[0],.35,run.task.source[1]);
    if(run.task.stock&&floor===0)for(let i=0;i<run.task.stock.length;i++){
      const box=new T.Mesh(new T.BoxGeometry(.36,.4,.36),new T.MeshLambertMaterial({color:i%2?0xbb8756:0xe3bd81}));
      box.position.set(10.15+(i%4)*.52,1.35+Math.floor(i/4)*.43,-6);props.add(box);
    }
  }
  function buttons() {
    const active=run?.status==='running'&&!replaying;
    for(const id of ['sim-auto','sim-step','sim-stop'])el(id).disabled=!active||busy;
    el('sim-new').disabled=busy||!world;el('sim-task').disabled=busy;el('sim-history').disabled=busy;
    host.querySelectorAll('[data-sim]').forEach(button=>button.disabled=!active||busy||auto);
    el('sim-auto').textContent=auto?'Pause agent':'Run agent';el('sim-export').disabled=!run;
    el('sim-replay').disabled=!run||busy||auto;el('sim-current').disabled=!replaying;
  }
  function paint(frame=run.frames.at(-1),replay=false) {
    if(!run)return;
    const next=run.task.steps[frame.phase];replaying=replay;draw(frame);
    el('sim-goal').textContent=run.task.name;el('sim-skill').textContent=run.task.skill;
    el('sim-next').textContent=next?'Next: '+next.label+' · floor '+next.at[2]:'All job steps complete.';
    el('sim-checklist').replaceChildren(...run.task.steps.map((step,index)=>{
      const li=document.createElement('li');li.textContent=(index<frame.phase?'✓ ':index===frame.phase?'→ ':'')+step.label;return li;
    }));
    status(frame.message);el('sim-metrics').replaceChildren();
    const metrics=[['State',frame.status],['Actions',frame.seq],['Rejected',frame.rejected],['Simulated time',frame.seconds+' s'],['Distance',frame.distance.toFixed(1)+' m'],['Carrying',frame.carrying?run.task.item:'Nothing'],...Object.entries(frame.objects||{})];
    for(const [label,value] of metrics){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;el('sim-metrics').append(dt,dd);}
    el('sim-events').replaceChildren(...run.frames.filter(f=>f.seq<=frame.seq).slice(-6).map(frame=>{const li=document.createElement('li');li.textContent=frame.seq+' · '+frame.message;return li;}));
    el('sim-replay').max=run.frames.length-1;el('sim-replay').value=run.frames.indexOf(frame);el('sim-frame').textContent=(replay?'Replay '+frame.seq+' · '+frame.action:'Current state')+' · '+run.id.slice(0,8);buttons();
  }
  async function history() {
    const data=await api();jobs=data.tasks;const selected=el('sim-task').value;
    el('sim-task').replaceChildren(...Object.entries(jobs).map(([id,task])=>new Option(task.name,id)));
    el('sim-task').value=selected;el('sim-skill').textContent=jobs[selected]?.skill||'';
    el('sim-history').replaceChildren(new Option('Choose a run',''),...data.runs.map(run=>new Option(run.task.name+' · '+run.status+' · '+run.id.slice(0,6),run.id)));
  }
  async function act(action,extra={}) {
    if(busy||!run||disposed)return;busy=true;buttons();
    try{run=await api('/action',{id:run.id,seq:run.actions,action,...extra});if(run.status!=='running'){auto=false;await history();}paint();}
    catch(error){auto=false;if(!disposed)status(error.message);}
    finally{busy=false;if(!disposed)buttons();}
  }
  listen(el('sim-new'),'click',async()=>{
    auto=false;busy=true;buttons();
    try{run=await api('/start',{task:el('sim-task').value});await history();paint();}
    catch(error){if(!disposed)status(error.message);}finally{busy=false;if(!disposed)buttons();}
  });
  listen(el('sim-history'),'change',async event=>{
    if(!event.target.value)return;auto=false;busy=true;buttons();
    try{run=await api('/'+event.target.value);paint();}catch(error){if(!disposed)status(error.message);}
    finally{busy=false;if(!disposed)buttons();}
  });
  listen(el('sim-task'),'change',()=>el('sim-skill').textContent=jobs[el('sim-task').value]?.skill||'');
  listen(el('sim-auto'),'click',()=>{auto=!auto;status(auto?'Agent running.':'Paused. The run is saved; resume when ready.');buttons();});
  listen(el('sim-step'),'click',()=>{auto=false;act('step');});
  listen(el('sim-stop'),'click',()=>{auto=false;act('stop');});
  for(const button of host.querySelectorAll('[data-sim]'))listen(button,'click',()=>{
    auto=false;const action=button.dataset.sim,next=run.task.steps[run.phase];
    if(action==='next'){
      const [x,z,floor]=next.at;if(floor!==run.worker.floor){status('Use the lift to reach floor '+floor+' first.');return;}act('target',{x,z});
    }else if(action==='lift-target')act('target',{x:0,z:-9});
    else if(action==='lift')act('lift',{floor:next.at[2]});
    else if(action==='work')act(el('sim-operation').value,{count:Number(el('sim-count').value)});
    else act(action);
  });
  listen(el('sim-replay'),'input',()=>{auto=false;paint(run.frames[Number(el('sim-replay').value)],true);});
  listen(el('sim-current'),'click',()=>paint());
  listen(el('sim-export'),'click',()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(run,null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download='hotel-run-'+run.id+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  const timer=setInterval(()=>{if(auto&&!busy&&!disposed)act('step');},200);
  function frame(now){
    if(disposed)return;
    scene?.render(matchMedia('(prefers-reduced-motion: reduce)').matches?0:Math.min(.06,(now-last)/1000));last=now;
    if(parcel&&run&&!replaying&&run.carrying){const mesh=scene?.actorMeshes.get('simulation-worker');if(mesh)parcel.position.set(mesh.position.x+Math.sin(mesh.rotation.y)*.6,1.25,mesh.position.z+Math.cos(mesh.rotation.y)*.6);}
    frameId=requestAnimationFrame(frame);
  }
  frameId=requestAnimationFrame(frame);
  (async()=>{
    try{
      const response=await fetch('/agents/api/world',{signal:abort.signal});if(!response.ok)throw Error('Hotel geometry is unavailable.');world=await response.json();if(disposed)return;
      try{scene=new HotelScene(el('sim-canvas'));scene.decorate(2);scene.scene.add(props);scene.update({...world,people:[],residents:[],you:null});}
      catch{el('sim-canvas').textContent='The 3D view is unavailable. Task controls and records remain available.';}
      await history();buttons();
    }catch(error){if(!disposed)status(error.message);}
  })();
  buttons();return{dispose(){disposed=true;auto=false;abort.abort();clearInterval(timer);cancelAnimationFrame(frameId);scene?.dispose();}};
}
