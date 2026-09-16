"""Read-only, sanitized public description of the operator-published Marble scene."""
import json, math, re
from pathlib import Path

FILE = re.compile(r'^[a-f0-9]{16}\.(spz|glb)$')

def active(root):
    folder=Path(root)/'assets/worldlabs'
    path=folder/'active.json'
    if not path.is_file(): return {'status':'awaiting_world','provider':'World Labs','model':'marble-1.1'}
    try:
        if path.stat().st_size>8192: raise ValueError()
        data=json.loads(path.read_text(encoding='utf-8'))
        if data.get('format')!='hotel-marble/1': raise ValueError()
        splat=data['splat']; collider=data.get('collider')
        for name in (splat,collider):
            if name is not None:
                if not isinstance(name,str) or not FILE.fullmatch(name): raise ValueError()
                f=folder/name
                if not f.resolve().is_relative_to(folder.resolve()) or not f.is_file() or f.stat().st_size>64*1024*1024: raise ValueError()
        if not splat.endswith('.spz') or (collider and not collider.endswith('.glb')): raise ValueError()
        semantics=data['semantics']
        scale=semantics['metric_scale_factor'];offset=semantics['ground_plane_offset']
        camera=data.get('camera',[0,1.6,0])
        values=[scale,offset,*camera]
        if len(camera)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>=10000 for x in values) or scale<=0: raise ValueError()
        base='/agents/assets/worldlabs/'
        return {'status':'ready','provider':'World Labs','model':str(data.get('model','Marble'))[:40],
                'title':str(data.get('title','The Grand · Marble world'))[:80],
                'splat':base+splat,'collider':base+collider if collider else None,
                'semantics':{'metric_scale_factor':scale,'ground_plane_offset':offset},'camera':camera}
    except (ValueError,KeyError,TypeError,OSError):
        return {'status':'unavailable','provider':'World Labs','model':'marble-1.1'}

