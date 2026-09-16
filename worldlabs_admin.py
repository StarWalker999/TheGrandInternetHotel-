"""Owner-operated World Labs importer. Run OUTSIDE the hotel service sandbox.

No public generation endpoint. A generation call happens only for the explicit
'generate' command. Resume never submits a second generation request.
"""
import argparse, getpass, hashlib, json, math, os, re, struct, sys, time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

API = 'https://api.worldlabs.ai/marble/v1/'
MODELS = ('marble-1.1', 'marble-1.1-plus', 'marble-1.0-draft')
ID = re.compile(r'^[A-Za-z0-9_-]{1,128}$')
ASSET_HOSTS = {'cdn.marble.worldlabs.ai', 'assets.worldlabs.ai'}
MAX_ASSET = 64 * 1024 * 1024

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Unexpected redirect; no credentials or assets were forwarded.')

def write_json(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    tmp=path.with_suffix(path.suffix+'.tmp')
    fd=os.open(tmp,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,allow_nan=False)
    os.replace(tmp,path)

def identifier(value):
    if not isinstance(value,str) or not ID.fullmatch(value): raise ValueError('Invalid World Labs identifier.')
    return value

def api_call(path, key, data=None):
    if not key or '\n' in key or '\r' in key: raise ValueError('A valid World Labs API key is required.')
    body=None if data is None else json.dumps(data).encode()
    req=Request(API+path,body,{'WLT-Api-Key':key,'Content-Type':'application/json'})
    try:
        with build_opener(NoRedirect()).open(req,timeout=60) as r:
            raw=r.read(4*1024*1024+1)
            if len(raw)>4*1024*1024: raise ValueError('API response exceeds the size limit.')
            return json.loads(raw)
    except HTTPError as e:
        raise ValueError(f'World Labs returned HTTP {e.code}; check API access and credits. No automatic retry was made.') from None

def unwrap_world(raw):
    world=raw.get('world',raw)
    if not isinstance(world,dict) or not isinstance(world.get('assets'),dict):
        raise ValueError('Expected a completed World Labs world response.')
    identifier(world.get('id',world.get('world_id')))
    return world

def wait_for_world(operation, key, output, timeout=900):
    op=identifier(operation)
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        result=api_call('operations/'+op,key)
        if result.get('error'): raise ValueError('World generation failed. Inspect its status in World Labs; do not blindly resubmit.')
        if result.get('done'):
            response=result.get('response') or {}
            world=unwrap_world(response)
            # Fetch the full response because operation snapshots may omit fields.
            world=unwrap_world(api_call('worlds/'+identifier(world.get('id',world.get('world_id'))),key))
            write_json(Path(output)/'world.json',world)
            write_json(Path(output)/'operation.json',{'operation_id':op,'status':'complete'})
            return world
        time.sleep(5)
    raise ValueError('Generation is still pending. Use resume with the saved operation id; no new generation is needed.')

def generate(prompt, model, key, output):
    output=Path(output); journal=output/'operation.json'
    if journal.exists(): raise ValueError('This output already has a generation journal. Resume it or choose a new directory deliberately.')
    if not prompt.strip() or len(prompt)>12000: raise ValueError('Use a non-empty prompt of at most 12000 characters.')
    write_json(journal,{'status':'submitting','model':model})
    # Never retry an uncertain POST: that could spend credits twice.
    result=api_call('worlds:generate',key,{'display_name':'The Grand Internet Hotel','model':model,
        'permission':{'public':False},'world_prompt':{'type':'text','text_prompt':prompt}})
    operation=identifier(result.get('operation_id'))
    write_json(journal,{'operation_id':operation,'status':'pending','model':model})
    return wait_for_world(operation,key,output)

def asset_url(url):
    p=urlparse(url)
    if p.scheme!='https' or p.hostname not in ASSET_HOSTS or p.port not in (None,443) or p.username or p.password:
        raise ValueError('Asset URL is outside the approved World Labs CDN hosts. Review the provider URL before changing the allowlist.')
    return url

def download(url, dest):
    # Deliberately no API key header here. Signed asset URLs stay in the private workspace.
    req=Request(asset_url(url),headers={'User-Agent':'GrandHotel-WorldLabs-Importer/1'})
    tmp=Path(str(dest)+'.part')
    try:
        with build_opener(NoRedirect()).open(req,timeout=60) as r, tmp.open('wb') as f:
            size=0
            while chunk:=r.read(1024*1024):
                size+=len(chunk)
                if size>MAX_ASSET: raise ValueError('World asset exceeds 64 MiB.')
                f.write(chunk)
        if size<16: raise ValueError('World asset is empty or invalid.')
        os.replace(tmp,dest)
    finally: tmp.unlink(missing_ok=True)

def semantics(world):
    s=world['assets'].get('splats',{}).get('semantics_metadata') or {}
    scale=s.get('metric_scale_factor'); offset=s.get('ground_plane_offset')
    if type(scale) not in (int,float) or not math.isfinite(scale) or not 0<scale<10000:
        raise ValueError('World is missing a valid metric scale factor.')
    if type(offset) not in (int,float) or not math.isfinite(offset) or abs(offset)>10000:
        raise ValueError('World is missing a valid ground-plane offset.')
    return {'metric_scale_factor':scale,'ground_plane_offset':offset}

def publish(world, destination, title, camera=(0,1.6,0)):
    world=unwrap_world(world); transform=semantics(world)
    dest=Path(destination); dest.mkdir(parents=True,exist_ok=True)
    version=hashlib.sha256(identifier(world.get('id',world.get('world_id'))).encode()).hexdigest()[:16]
    urls=world['assets'].get('splats',{}).get('spz_urls',{})
    selected=urls.get('100k') or urls.get('500k')
    if not selected: raise ValueError('World has no 100k or 500k SPZ asset.')
    splat=dest/(version+'.spz')
    download(selected,splat)
    collider_url=world['assets'].get('mesh',{}).get('collider_mesh_url')
    collider=None
    if collider_url:
        collider=dest/(version+'.glb'); download(collider_url,collider)
        if collider.read_bytes()[:4]!=b'glTF': raise ValueError('Collider is not a GLB file.')
    manifest={'format':'hotel-marble/1','provider':'World Labs','model':world.get('model') or 'Marble',
        'title':title[:80],'splat':splat.name,'collider':collider.name if collider else None,
        'semantics':transform,'camera':list(camera),'sha256':hashlib.sha256(splat.read_bytes()).hexdigest()}
    # Only publish the sanitized manifest after all assets succeed.
    write_json(dest/'active.json',manifest)
    for p in (splat,collider,dest/'active.json'):
        if p: p.chmod(0o644)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--key-file',type=Path,help='Private file containing only the API key; otherwise use WORLDLABS_API_KEY or a hidden prompt.')
    sub=p.add_subparsers(dest='command',required=True)
    g=sub.add_parser('generate');g.add_argument('--prompt-file',type=Path,required=True);g.add_argument('--model',choices=MODELS,default='marble-1.1');g.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('resume');r.add_argument('--operation',required=True);r.add_argument('--output',type=Path,required=True)
    f=sub.add_parser('fetch');f.add_argument('--world',required=True);f.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('publish');q.add_argument('--world-file',type=Path,required=True);q.add_argument('--destination',type=Path,required=True);q.add_argument('--title',default='The Grand · Marble world');q.add_argument('--camera',nargs=3,type=float,default=[0,1.6,0])
    args=p.parse_args()
    try:
        if args.command=='publish':
            if not all(math.isfinite(x) and abs(x)<10000 for x in args.camera): raise ValueError('Invalid camera position.')
            publish(json.loads(args.world_file.read_text(encoding='utf-8')),args.destination,args.title,args.camera)
            print('Sanitized world assets published. Review the scene before deploying it.')
        else:
            key=(args.key_file.read_text().strip() if args.key_file else os.environ.get('WORLDLABS_API_KEY')) or getpass.getpass('World Labs API key (hidden): ')
            if args.command=='generate': generate(args.prompt_file.read_text(encoding='utf-8'),args.model,key,args.output)
            elif args.command=='resume': wait_for_world(args.operation,key,args.output)
            else:
                world=unwrap_world(api_call('worlds/'+identifier(args.world),key))
                write_json(args.output/'world.json',world)
            print('World response saved privately. Use publish to prepare reviewed public assets.')
    except (ValueError,OSError,KeyError,TypeError) as e:
        # Avoid echoing provider URLs, API response bodies, keys or user filesystem paths.
        print(str(e) if isinstance(e,ValueError) else 'Could not complete the operation. Check the private input/output files and network connection.',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__': sys.exit(main())

