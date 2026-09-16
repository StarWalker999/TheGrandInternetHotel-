import * as THREE from './assets/three/three.module.js';
import {SparkRenderer,SplatMesh,SparkControls} from './assets/spark/spark.module.js';

const stage=document.querySelector('#world-stage'), message=document.querySelector('#world-message');
let renderer,spark,splat,controls,disposed=false;
function fail(text){message.hidden=false;message.textContent=text;}
async function start(){
 const response=await fetch('/agents/api/worldlabs',{signal:AbortSignal.timeout(10000)});
 if(!response.ok)throw Error('manifest');
 const world=await response.json();
 if(world.status!=='ready'){fail('The first Marble world has not been published yet. Return to the hotel to explore the lobby.');return;}
 if(!/^\/agents\/assets\/worldlabs\/[a-f0-9]{16}\.spz$/.test(world.splat))throw Error('asset');
 document.querySelector('#world-title').textContent=world.title;
 const scene=new THREE.Scene();scene.background=new THREE.Color('#e7e3da');
 const camera=new THREE.PerspectiveCamera(65,innerWidth/innerHeight,.05,500);
 renderer=new THREE.WebGLRenderer({antialias:false,alpha:false});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);stage.append(renderer.domElement);
 spark=new SparkRenderer({renderer});scene.add(spark);
 const frame=new THREE.Group();frame.rotation.x=Math.PI;scene.add(frame);
 splat=new SplatMesh({url:world.splat});
 splat.scale.setScalar(world.semantics.metric_scale_factor);
 splat.position.y=-world.semantics.ground_plane_offset;
 frame.add(splat);
 await splat.initialized;if(disposed)return;
 controls=new SparkControls({canvas:renderer.domElement});controls.fpsMovement.moveSpeed=2;
 function reset(){camera.position.fromArray(world.camera);camera.rotation.set(0,0,0);stage.focus();}
 reset();document.querySelector('#reset').addEventListener('click',reset);
 addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
 renderer.setAnimationLoop(()=>{if(disposed)return;if(document.hasFocus())controls.update(camera);renderer.render(scene,camera);});
 message.hidden=true;document.body.dataset.ready='true';
}
addEventListener('pagehide',()=>{disposed=true;renderer?.setAnimationLoop(null);splat?.dispose();spark?.dispose();renderer?.dispose();});
start().catch(()=>fail('This scene could not load. Reload it or return to the hotel. A browser with WebGL 2 is required.'));
