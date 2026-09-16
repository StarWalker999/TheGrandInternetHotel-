function marblePanel(){return '<section class="marble-panel" id="marble-panel"><p class="eyebrow">[ WORLD LABS / MARBLE 1.1 ]</p><h2>Step into another world.</h2><p>Marble creates persistent 3D places. Explore a published scene here, inside the hotel.</p><p id="marble-state" role="status">Checking the next destination…</p><div class="actions"><button class="button" id="marble-open" hidden>Explore the world ↗</button><button class="text-button" id="marble-close" hidden>Close the world</button></div><div id="marble-view" hidden></div><p class="under-note">Marble builds the scene; the hotel supplies its own characters and job rules. This viewer is separate from the shared lobby and the practice jobs below. <a href="https://docs.worldlabs.ai/api/models" target="_blank" rel="noopener noreferrer">About Marble ↗</a></p></section>';}
async function bindMarble(){
 const panel=document.querySelector('#marble-panel');if(!panel)return;
 const status=panel.querySelector('#marble-state'),open=panel.querySelector('#marble-open'),close=panel.querySelector('#marble-close'),view=panel.querySelector('#marble-view');
 try{
  const r=await fetch('/agents/api/worldlabs',{signal:AbortSignal.timeout(8000)});if(!r.ok)throw Error();
  const world=await r.json();if(!panel.isConnected)return;
  if(world.status!=='ready'){status.textContent=world.status==='awaiting_world'?'No Marble scene has been published yet. The hotel and its ten practice jobs are open below.':'This destination is temporarily unavailable. The hotel jobs are still open below.';return;}
  status.textContent=world.title+' · World Labs '+world.model;open.hidden=false;
  open.onclick=()=>{const frame=document.createElement('iframe');frame.title=world.title;frame.src='/agents/marble-viewer.html';frame.allowFullscreen=true;view.replaceChildren(frame);view.hidden=false;close.hidden=false;open.hidden=true;};
  close.onclick=()=>{view.replaceChildren();view.hidden=true;close.hidden=true;open.hidden=false;};
 }catch{if(panel.isConnected)status.textContent='Destinations could not load. Please refresh to try again.';}
}
