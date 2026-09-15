import * as T from './assets/three/three.module.js';

const C={paper:0xf6f3eb,wall:0xe9e1cc,trim:0xf8f2df,stone:0xc7c1af,ink:0x383931,sage:0x8d9d7c,roof:0x74876b,orange:0xd97937,amber:0xecc879,wood:0x9e7959,rose:0xc69480,blue:0x859b9e,tile:0xe5e2d5};
const cubeGeometry=new T.BoxGeometry(1,1,1);
const edgeGeometry=new T.EdgesGeometry(cubeGeometry);
const edgeCoords=edgeGeometry.attributes.position.array;

class Blocks {
  constructor(){this.colors=new Map();this.lines=[];}
  box(x,y,z,w,h,d,color,outline=true){
    if(!this.colors.has(color))this.colors.set(color,[]);
    this.colors.get(color).push([x,y,z,w,h,d]);
    if(outline)for(let i=0;i<edgeCoords.length;i+=3)this.lines.push(x+edgeCoords[i]*w,y+edgeCoords[i+1]*h,z+edgeCoords[i+2]*d);
  }
  finish(){const group=new T.Group(),matrix=new T.Matrix4();
    for(const [color,items] of this.colors){const material=new T.MeshLambertMaterial({color});const mesh=new T.InstancedMesh(cubeGeometry,material,items.length);items.forEach((a,i)=>{matrix.makeScale(a[3],a[4],a[5]);matrix.setPosition(a[0],a[1],a[2]);mesh.setMatrixAt(i,matrix);});mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);}
    const geom=new T.BufferGeometry();geom.setAttribute('position',new T.Float32BufferAttribute(this.lines,3));group.add(new T.LineSegments(geom,new T.LineBasicMaterial({color:C.ink,transparent:true,opacity:.22})));return group;
  }
}
function sign(text,w,h,color='#f6f3eb',ink='#34372f'){
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=Math.round(1024*h/w);
  const ctx=canvas.getContext('2d');ctx.fillStyle=color;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.strokeStyle=ink;ctx.lineWidth=5;ctx.strokeRect(10,10,canvas.width-20,canvas.height-20);
  const lines=text.split('\n');ctx.fillStyle=ink;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`${Math.round(canvas.height/(lines.length*1.5))}px Georgia`;
  lines.forEach((s,i)=>ctx.fillText(s,512,canvas.height*(i+.5)/lines.length,940));
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
  return new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:texture,side:T.DoubleSide}));
}
function topiary(b,x,z,s=1){b.box(x,.55,z,1.7*s,1.1,1.7*s,C.stone);b.box(x,1.7,z,.35,2,.35,C.wood);b.box(x,2.8,z,1.9*s,1.6,1.9*s,C.roof);b.box(x,3.8,z,1.1*s,.6,1.1*s,C.sage);}
function exterior(){const b=new Blocks();
  b.box(0,-.45,0,32,.8,26,C.stone);b.box(0,18.1,0,30,36,24,C.wall);
  for(let floor=0;floor<12;floor++){
    const y=1.65+floor*3;b.box(0,floor*3+.35,12.18,30.6,.28,.65,C.trim);b.box(15.17,floor*3+.35,0,.65,.28,24.5,C.trim);
    for(let i=0;i<12;i++){
      let x=-13.5+i*2.45;if(!floor&&Math.abs(x)<2)continue;
      b.box(x,y,12.12,1.52,2.2,.28,C.ink);b.box(x,y,12.31,1.15,1.85,.13,(i+floor)%4===0?C.amber:C.sage);b.box(x,y,12.41,.09,1.9,.12,C.trim);b.box(x,y-.16,12.41,1.17,.09,.12,C.trim);b.box(x,y-1.12,12.4,1.75,.18,.55,C.trim);

    }
    for(let i=0;i<8;i++){const z=-10.5+i*3;b.box(15.12,y,z,.25,2.2,1.5,C.ink);b.box(15.3,y,z,.12,1.8,1.15,(i+floor)%3===0?C.amber:C.sage);b.box(15.4,y,z,.1,1.85,.09,C.trim);}
  }
  for(const x of [-15,-10,10,15])b.box(x,18.2,12.45,.5,36.2,.65,C.trim);
  b.box(0,36.4,0,32,.65,26,C.trim);
  for(let i=0;i<6;i++)b.box(0,36.9+i*.5,0,31-i*1.6,.5,25-i*1.1,i%2?C.roof:C.sage);
  for(const x of [-12.5,12.5]){
    b.box(x,37,8,6,4,6,C.wall);for(let i=0;i<5;i++)b.box(x,39+i*.55,8,7-i*1.15,.55,7-i*1.15,C.roof);
    b.box(x,42.7,8,.12,3,.12,C.ink);b.box(x+.65,43.7,8,1.3,.7,.08,C.orange);
  }
  b.box(0,38.7,12.1,15,4.2,.7,C.trim);b.box(0,41,12.1,16,.35,1.1,C.stone);
  b.box(0,1.65,12.25,4.2,3.3,.4,C.ink);b.box(-1.04,1.55,12.5,1.8,2.9,.13,C.amber);b.box(1.04,1.55,12.5,1.8,2.9,.13,C.amber);
  for(let i=0;i<10;i++){b.box(-4.05+i*.9,3.7,13.4,.9,.35,3.5,i%2?C.trim:C.orange);b.box(-4.05+i*.9,3.3,15.1,.9,.55,.25,i%2?C.trim:C.orange);}
  for(const x of [-4.6,4.6]){b.box(x,1.8,14.8,.16,3.6,.16,C.ink);b.box(x,3,13.1,.6,.9,.65,C.amber);}
  const g=b.finish(),plaque=sign('THE GRAND\nINTERNET HOTEL',14,3.5);plaque.position.set(0,38.75,12.51);g.add(plaque);for(let floor=1;floor<12;floor+=2){const guest=actor('agent',floor%3===0?C.blue:floor%3===1?C.orange:C.sage);guest.scale.setScalar(.5);guest.position.set(-11+(floor%5)*4.7,floor*3+.5,12.9);g.add(guest);}
  return g;
}
function yard(){const b=new Blocks();b.box(0,-.7,2,53,.6,48,C.stone);b.box(0,-.35,4,49,.1,42,C.tile);
  for(let z=13;z<25;z+=1.5)for(let x=-4.5;x<=4.5;x+=1.5)b.box(x,-.23,z,1.45,.08,1.45,(Math.round((x+z)*2)%3)?C.trim:C.stone,false);
  for(const x of [-12,12])topiary(b,x,16,1.2);
  for(const x of [-20,20]){b.box(x,.7,16,4,.3,1.3,C.wood);b.box(x,1.4,16.6,4,1.3,.2,C.wood);for(const dx of [-1.5,1.5])b.box(x+dx,.2,16,.2,.7,1,C.ink);}
  for(const x of [-20,20]){b.box(x,2.4,8,.14,5,.14,C.ink);b.box(x,4.9,8,.9,1.1,.9,C.amber);b.box(x,5.55,8,1.2,.2,1.2,C.ink);}
  return b.finish();
}
function floorBase(){const b=new Blocks();b.box(0,-.1,0,30,.35,24,C.stone);
  for(let x=-14;x<=14;x+=2)for(let z=-11;z<=11;z+=2)b.box(x,.1,z,1.98,.1,1.98,((x/2+(z+11)/2)%2)?C.trim:C.tile,false);
  b.box(0,.19,1,4,.04,21,C.orange,false);b.box(0,.22,1,3.3,.02,20.6,0xd3a77d,false);return b;
}
function interior(solids,upper=false){const b=floorBase();
  for(const [x,z,w,d,h,kind] of solids){
    if(z>12||Math.abs(x)>15)continue;
    if(kind==='plant'){topiary(b,x,z,.65);continue;}
    const color={wall:C.wall,partition:C.wall,desk:C.wood,sofa:C.sage,table:C.wood,shelf:C.wood,bench:C.wood,workdesk:C.wood,bed:C.sage}[kind]||C.wall;
    const height=kind==='wall'?1.1:h;b.box(x,height/2+.2,z,w,height,d,color);
    if(kind==='wall'||kind==='partition')b.box(x,height+.23,z,w+.05,.09,d+.06,C.trim);
    if(kind==='desk'){b.box(x,h+.27,z,w+.3,.17,d+.25,C.ink);for(let i=0;i<5;i++)b.box(x-2.8+i*1.4,h/2,z+d/2+.05,.05,h*.7,.05,C.trim);b.box(x,h+.6,z,.5,.5,.5,C.amber);}
    if(kind==='sofa'){b.box(x,h+.3,z+.45,w,.5,.4,color);b.box(x-w/2,h+.1,z,.25,.7,d,color);b.box(x+w/2,h+.1,z,.25,.7,d,color);}
    if(kind==='table'){b.box(x,h+.4,z,.35,.4,.35,C.trim);b.box(x+.5,h+.25,z,.5,.07,.4,C.orange);}
    if(kind==='bed'){b.box(x,h+.32,z,w-.2,.25,d-.15,C.trim);b.box(x+Math.sign(x)*1.2,h+.6,z,.6,.28,d-.25,C.stone);}
    if(kind==='shelf'){for(let j=0;j<3;j++)for(let k=0;k<10;k++)b.box(x+.6,.65+j*.7,z-2.5+k*.52,.18,.5,.32,[C.sage,C.orange,C.blue,C.trim][k%4],false);}
    if(kind==='workdesk'){b.box(x,h+.55,z,.95,.75,.15,C.ink);b.box(x,h+.56,z+.09,.77,.55,.03,C.blue);b.box(x,h+.25,z+.42,.8,.06,.3,C.trim);b.box(x+1,h+.4,z,.25,.4,.25,C.orange);}
    if(kind==='bench'){for(let dx=-1;dx<=1;dx++)b.box(x+dx,h+.6,z,.65,.8,.25,C.ink);b.box(x,h+.32,z+.5,2,.1,.5,C.sage);}
  }
  b.box(0,1.4,-11.45,3.3,2.6,.2,C.ink);b.box(-.76,1.4,-11.23,1.4,2.4,.15,C.amber);b.box(.76,1.4,-11.23,1.4,2.4,.15,C.amber);
  const g=b.finish();const lift=sign('LIFT',2,.55);lift.position.set(0,3.1,-11.2);g.add(lift);
  if(!upper){for(const [text,x,z,w] of [['FRONT DESK',-8,-3,5],['ATHENA · LIBRARY',-10,-11,5],['HEPHAESTUS · WORKSHOP',10,-11,7]]){const p=sign(text,w,.75);p.position.set(x,2.2,z);g.add(p);}}
  else{for(const side of [-1,1])for(let i=0;i<6;i++){const p=sign(String(i+1+(side>0?6:0)).padStart(2,'0'),.85,.45);p.position.set(side*3,1.9,-10+i*4);p.rotation.y=side<0?Math.PI/2:-Math.PI/2;g.add(p);}}
  return g;
}
function actor(kind,color=C.sage){const g=new T.Group(),body=new Blocks();
  if(kind==='human'){
    body.box(0,1.1,0,.8,1.1,.5,color);body.box(0,1.95,0,.7,.7,.65,0xd8b99d);body.box(0,2.3,0,.78,.16,.72,C.ink);body.box(-.51,1.05,0,.24,1,.35,color);body.box(.51,1.05,0,.24,1,.35,color);
    for(const x of [-.17,.17]){body.box(x,1.98,.34,.08,.09,.04,C.ink);body.box(x,.35,0,.26,.7,.35,C.ink);}
  }else{
    body.box(0,.85,0,1.15,1.1,.8,color);body.box(0,1.6,0,.85,.45,.7,color);body.box(-.3,1.95,0,.23,.5,.23,color);body.box(.3,1.88,0,.23,.4,.23,color);
    for(const [x,y] of [[-.3,1.3],[.3,1.3],[0,.92],[-.3,1.99],[.3,1.94]]){body.box(x,y,.43,.22,.23,.1,C.trim);body.box(x+.025,y,.49,.1,.12,.03,C.ink);}
    for(const side of [-1,1]){body.box(side*.75,.55,0,.5,.35,.45,color);body.box(side*.96,.76,0,.22,.4,.3,color);body.box(side*.4,.21,.15,.35,.25,.7,color);}
  }
  if(kind==='agent'){if(color===C.blue){body.box(0,1.6,.63,1.2,.5,.17,C.ink);body.box(0,1.63,.74,1,.34,.04,C.trim);body.box(0,1.45,0,1.25,.16,.85,C.blue);}else if(color===C.rose){body.box(0,.85,.58,.92,.55,.12,C.trim);for(const x of [-.38,.38])body.box(x,2.13,0,.26,.4,.27,color);}else{body.box(0,2.15,0,.95,.3,.8,C.orange);body.box(0,2.04,0,1.04,.08,.86,C.ink);body.box(.86,.7,.18,.15,.55,.13,C.amber);}}g.add(body.finish());return g;
}

export class HotelScene {
  constructor(host,{preview=false,onGround=()=>{},onResident=()=>{}}={}){
    this.host=host;this.preview=preview;this.onGround=onGround;this.onResident=onResident;this.tags=new Map();this.disposed=false;this.azimuth=.5;this.zoom=1;this.actorMeshes=new Map();this.floor=0;this.inside=false;
    this.renderer=new T.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:preview});this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.65));this.renderer.setClearColor(C.paper);this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;this.renderer.outputColorSpace=T.SRGBColorSpace;
    this.canvas=this.renderer.domElement;this.canvas.setAttribute('aria-label',preview?'Voxel hotel exterior':'Walkable hotel. Use WASD, arrow keys, touch arrows, or choose a destination.');this.canvas.tabIndex=preview?-1:0;host.replaceChildren(this.canvas);if(!preview){this.labels=document.createElement('div');this.labels.className='resident-labels';host.append(this.labels);}
    this.scene=new T.Scene();this.scene.background=new T.Color(C.paper);this.scene.fog=new T.Fog(C.paper,100,190);
    this.camera=new T.OrthographicCamera(-35,35,30,-30,.1,250);
    this.scene.add(new T.HemisphereLight(0xfff9e9,0x8e947d,1.6));const sun=new T.DirectionalLight(0xfff5e5,1.4);sun.position.set(-35,60,40);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-45;sun.shadow.camera.right=45;sun.shadow.camera.top=50;sun.shadow.camera.bottom=-35;sun.shadow.camera.far=160;sun.shadow.normalBias=.05;this.scene.add(sun);
    this.exterior=exterior();this.yard=yard();this.scene.add(this.yard,this.exterior);this.target=new T.Vector3(0,16,0);this.currentTarget=this.target.clone();
    const land=new T.Mesh(new T.PlaneGeometry(300,300),new T.MeshLambertMaterial({color:C.paper}));land.rotation.x=-Math.PI/2;land.position.y=-1.1;land.receiveShadow=true;this.scene.add(land);this.land=land;
    this.ray=new T.Raycaster();this.plane=new T.Plane(new T.Vector3(0,1,0),-.2);
    this.abort=new AbortController();const opts={signal:this.abort.signal};let down=null;
    this.canvas.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY,az:this.azimuth};this.canvas.setPointerCapture(e.pointerId);},opts);
    this.canvas.addEventListener('pointermove',e=>{if(down){this.azimuth=down.az-(e.clientX-down.x)*.008;this.render(0);}},opts);
    this.canvas.addEventListener('pointerup',e=>{if(down&&Math.hypot(e.clientX-down.x,e.clientY-down.y)<8&&!this.preview){const r=this.canvas.getBoundingClientRect();this.ray.setFromCamera(new T.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),this.camera);const hits=this.ray.intersectObjects([...this.actorMeshes.values()].filter(m=>m.visible),true);if(hits.length){let o=hits[0].object;while(o&&!o.userData.state)o=o.parent;if(o?.userData.state?.ambient){this.onResident(o.userData.state.id);down=null;return;}}const p=new T.Vector3();if(this.ray.ray.intersectPlane(this.plane,p))this.onGround(p.x,p.z);}down=null;},opts);
    this.canvas.addEventListener('pointercancel',()=>down=null,opts);
    this.resizeObserver=new ResizeObserver(()=>this.resize());this.resizeObserver.observe(host);this.resize();
  }
  resize(){if(this.disposed)return;const r=this.host.getBoundingClientRect();this.width=Math.max(1,r.width);this.height=Math.max(1,r.height);this.renderer.setSize(this.width,this.height);this.render(0);}
  decorate(version){
    const b=new Blocks();
    for(const side of [-1,1]){
      b.box(side*12,40,0,7,5,9,C.wall);b.box(side*12,43,0,8,1,10,C.sage);
      for(let i=0;i<5;i++)b.box(side*12,44+i*.65,0,7-i*1.15,.7,9-i*1.35,C.roof);
      b.box(side*12,48,0,.16,4,.16,C.ink);b.box(side*12+1,49,0,2,1,.12,C.orange);
    }
    b.box(0,41,-6,8,5,7,C.ink);b.box(0,42,-6,7,3,6,C.blue);
    for(let i=0;i<4;i++)b.box(0,44+i*.55,-6,9-i*1.8,.65,8-i*1.5,C.sage);
    for(let i=0;i<10;i++){const a=i*.45;b.box(17+Math.sin(a)*2,9+i*.8,11+Math.cos(a)*2,1.7,1.5,1.6,C.sage);}
    const addition=b.finish();this.exterior.add(addition);
    const guest=actor('agent',C.sage);guest.scale.setScalar(2.2);guest.position.set(-9,37,9);this.exterior.add(guest);
    const welcome=sign('VACANCY',5,1.4,'#f6f3eb','#b15f24');welcome.position.set(-10,4,13);this.exterior.add(welcome);
    if(version===4)this.exterior.traverse(o=>{if(o.isLineSegments){o.material.opacity=.65;}if(o.isMesh&&o.material?.color){o.material.color.lerp(new T.Color(C.trim),.17);}});
    this.target.y=20;this.currentTarget.copy(this.target);this.render(0);
  }
  setLayout(data){if(this.lobby)return;this.lobby=interior(data.ground_solids);this.upper=interior(data.upper_solids,true);this.scene.add(this.lobby,this.upper);this.lobby.visible=false;this.upper.visible=false;}
  update(snapshot){this.snapshot=snapshot;this.me=snapshot.people.find(p=>p.id===snapshot.you);this.setLayout(snapshot);const occupants=[...snapshot.people,...(snapshot.residents||[])];
    const ids=new Set(occupants.map(p=>p.id));for(const [id,mesh] of this.actorMeshes){if(!ids.has(id)){this.scene.remove(mesh);this.release(mesh);this.actorMeshes.delete(id);}}
    for(const p of occupants){let m=this.actorMeshes.get(p.id);if(m&&m.userData.kind!==p.kind){this.scene.remove(m);this.release(m);this.actorMeshes.delete(p.id);m=null;}if(!m){m=actor(p.kind,p.portrait==='blue'?C.blue:p.portrait==='rose'?C.rose:p.id===snapshot.you?C.orange:C.sage);m.userData.kind=p.kind;m.position.set(p.x,0,p.z);this.scene.add(m);this.actorMeshes.set(p.id,m);}m.userData.state=p;}
    if(this.me){this.floor=this.me.floor;this.inside=this.floor>0||(Math.abs(this.me.x)<14.8&&this.me.z<11.7&&this.me.z>-12);this.exterior.visible=!this.inside;this.lobby.visible=this.inside&&this.floor===0;this.upper.visible=this.floor>0;this.yard.visible=this.floor===0;
      this.target.set(this.me.x,this.inside?1.5:9,this.me.z-(this.inside?0:8));}
    else{this.floor=0;this.inside=true;this.exterior.visible=false;this.lobby.visible=true;this.upper.visible=false;this.yard.visible=true;this.target.set(0,1.5,1);}
    for(const m of this.actorMeshes.values())m.visible=m.userData.state.floor===this.floor;
  }
  render(dt=.016){if(this.disposed)return;const aspect=this.width/this.height;let span=this.preview?57:this.me?(this.inside?27:54):32;span=span/this.zoom;if(aspect<1)span*=this.inside?1/aspect:Math.min(1.45,1/aspect);
    this.camera.left=-span*aspect/2;this.camera.right=span*aspect/2;this.camera.top=span/2;this.camera.bottom=-span/2;this.camera.updateProjectionMatrix();
    this.currentTarget.lerp(this.target,dt?Math.min(1,dt*7):1);const t=this.currentTarget;this.camera.position.set(t.x+Math.sin(this.azimuth)*65,t.y+(this.inside?66:33),t.z+Math.cos(this.azimuth)*65);this.camera.lookAt(t);
    const occupiedLabels=[];for(const m of this.actorMeshes.values()){const p=m.userData.state,blend=dt?Math.min(1,dt*13):1;m.position.x+=(p.x-m.position.x)*blend;m.position.z+=(p.z-m.position.z)*blend;m.rotation.y=p.heading;const walking=p.walking||Math.hypot(p.x-m.position.x,p.z-m.position.z)>.04;m.position.y=dt&&walking?Math.sin(performance.now()*.012+(p.id.length%7))*.065:0;
      if(p.ambient&&this.labels){let tag=this.tags.get(p.id);if(!tag){tag=document.createElement('button');tag.className='resident-tag';tag.innerHTML='<b></b><span></span>';tag.onclick=e=>{e.stopPropagation();this.hoverTag=null;tag.style.zIndex='';this.onResident(p.id);};tag.onpointerenter=()=>{this.hoverTag=tag;tag.style.zIndex='8';};tag.onpointerleave=()=>{this.hoverTag=null;tag.style.zIndex='';};this.labels.append(tag);this.tags.set(p.id,tag);}const pt=new T.Vector3(m.position.x,3.15,m.position.z).project(this.camera);tag.hidden=!m.visible||(!this.inside&&Math.abs(p.x)<14.8&&p.z<12)||Math.abs(pt.x)>.93||Math.abs(pt.y)>.9;if(!this.hoverTag&&!tag.hidden){const w=Math.max(50,tag.offsetWidth),h=Math.max(24,tag.offsetHeight);let x=Math.max(w/2,Math.min(this.width-w/2,(pt.x+1)*this.width/2)),y=(1-pt.y)*this.height/2;for(let tries=0;tries<12&&occupiedLabels.some(a=>Math.abs(a.x-x)<(a.w+w)/2+5&&Math.abs(a.y-y)<(a.h+h)/2+5);tries++)y-=h+7;occupiedLabels.push({x,y,w,h});tag.style.left=x+'px';tag.style.top=y+'px';}tag.querySelector('b').textContent=p.name;tag.querySelector('span').textContent=p.speech||'';tag.setAttribute('aria-label','Meet '+p.name+', '+p.role);}
    }
    this.renderer.render(this.scene,this.camera);
  }
  release(root){root.traverse(o=>{if(o.geometry&&o.geometry!==cubeGeometry)o.geometry.dispose();if(o.material){for(const m of(Array.isArray(o.material)?o.material:[o.material])){m.map?.dispose();m.dispose();}}});}
  dispose(){this.disposed=true;this.abort.abort();this.resizeObserver.disconnect();this.release(this.scene);this.renderer.dispose();this.renderer.forceContextLoss();this.canvas.remove();this.labels?.remove();}
}
