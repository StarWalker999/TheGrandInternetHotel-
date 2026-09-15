import {gardenHat} from './assets/garden/garden-wardrobe.js';
import * as T from './assets/three/three.module.js';
import {PlayerAvatar,DEFAULT_CUSTOM,PLAYER_MODEL_PRESETS} from './assets/garden/WanderAvatar.js';
export {DEFAULT_CUSTOM,PLAYER_MODEL_PRESETS};
export function releaseCharacter(root){const geometries=new Set(),materials=new Set(root.userData.ponsOwnedMaterials||[]);root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);});for(const g of geometries)g.dispose();for(const m of materials)m.dispose();root.clear();}
export function createGardenCharacter(appearance={}){
 const state={...DEFAULT_CUSTOM,...PLAYER_MODEL_PRESETS[appearance.preset||'wanderer']?.state,...appearance};
 const avatar=new PlayerAvatar(state,{loadSaved:false});const root=avatar.root;if(appearance.headwear&&appearance.headwear!=='none')avatar.slots.head?.add(gardenHat(appearance.headwear));root.scale.setScalar(1.35);
 // Rendering-only adapter: no upstream save, equip, update or ownership calls.
 root.userData.animateGarden=(t,m)=>avatar.animate(t,m,1);
 root.userData.appearanceKey=JSON.stringify(appearance);
 return root;
}
export function mountCharacterPreview(host,appearance){
 const renderer=new T.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(280,280);renderer.setClearColor(0xffffff);host.replaceChildren(renderer.domElement);
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(32,1,.1,30);camera.position.set(3,2.7,5);camera.lookAt(0,1.2,0);scene.add(new T.HemisphereLight(0xffffff,0x78706a,2.2));const sun=new T.DirectionalLight(0xffffff,3);sun.position.set(3,6,5);scene.add(sun);let model;
 const update=a=>{if(model){scene.remove(model);releaseCharacter(model);}model=createGardenCharacter(a);scene.add(model);model.updateMatrixWorld(true);const bounds=new T.Box3().setFromObject(model),center=bounds.getCenter(new T.Vector3()),size=bounds.getSize(new T.Vector3());const distance=Math.max(size.x,size.y,size.z)/2/Math.tan(T.MathUtils.degToRad(camera.fov/2))*1.35;camera.position.copy(center).add(new T.Vector3(3,1.7,5).normalize().multiplyScalar(distance));camera.lookAt(center);renderer.render(scene,camera);};update(appearance);
 return {update,canvas:renderer.domElement,dispose(){releaseCharacter(model);renderer.dispose();renderer.forceContextLoss();host.replaceChildren();}};
}
