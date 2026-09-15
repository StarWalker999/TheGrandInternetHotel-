"""Shared voxel-hotel movement. No access to private agent-room data."""
import math
import re
import secrets
import time
from collections import deque

# x, z, width, depth, height, material. These also drive the visible collision geometry.
GROUND = [
    [-22,0,.6,24,3.6,'wall'],[22,0,.6,24,3.6,'wall'],[0,-12,44,.6,3.6,'wall'],
    [-12.25,12,19.5,.6,3.6,'wall'],[12.25,12,19.5,.6,3.6,'wall'],
    [-8,-3,7,1.8,1.3,'desk'],[-9,5,4,1.3,.9,'sofa'],[-9,8,4,1.3,.9,'sofa'],
    [-9,6.5,2,1,0.55,'table'],[9,6,4,1.3,.9,'sofa'],[9,8.7,4,1.3,.9,'sofa'],
    [9,7.35,2,1,0.55,'table'],[-13,-7,1,6,2.6,'shelf'],[11,-6,4,2,1.1,'bench'],
    [-12,16,2,2,2.5,'plant'],[12,16,2,2,2.5,'plant'],[-13,10,1,1,2,'plant'],[13,10,1,1,2,'plant'],
]
# Reading tables and small work bays keep the central hotel aisle clear.
GROUND += [[-7,-8,3,1.4,1.05,'workdesk'],[7,-2,3,1.4,1.05,'workdesk'],[11,1,3,1.4,1.05,'workdesk']]
GROUND += [[x,z,1.8,1.8,4.2,'column'] for x in (-18,18) for z in (-8,0,8)]
GROUND += [[-17,4,4,1.5,1,'sofa'],[-17,6.3,2,1,.65,'table'],[17,4,4,1.5,1,'sofa'],[17,6.3,2,1,.65,'table'],[-20,-4,1,1,2,'plant'],[20,-4,1,1,2,'plant']]
UPPER = [[-15,0,.6,24,2.8,'wall'],[15,0,.6,24,2.8,'wall'],[0,-12,30,.6,2.8,'wall'],[0,12,30,.6,2.8,'wall']]
for side in (-1,1):
    for z in (-8,-4,0,4,8): UPPER.append([side*9,z,12,.25,1.6,'partition'])
    for z in range(-12,13,4): UPPER.append([side*3,z,.25,1.8,1.6,'partition'])
    for z in (-10,-6,-2,2,6,10):
        UPPER.append([side*11,z,3.5,1.6,.55,'bed'])
        UPPER.append([side*6.5,z-1,1.8,.65,.8,'table'])

LANDMARKS = {
    'entrance': {'name':'Front entrance','x':0,'z':16},
    'lobby': {'name':'The lobby','x':0,'z':6},
    'front_desk': {'name':'Front desk','x':-8,'z':0,'route':'#/checkin'},
    'lounge': {'name':'The sitting room','x':-6,'z':6.5},
    'library': {'name':'Athena · library','x':-10,'z':-8,'route':'#/services'},
    'workshop': {'name':'Hephaestus · workshop','x':8,'z':-5,'route':'#/services'},
    'lift': {'name':'The lift','x':0,'z':-9},
}

def clear(x,z,floor,radius=.35):
    if not all(math.isfinite(v) for v in (x,z)): return False
    if floor == 0:
        if abs(x)>28 or z < -16 or z > 24: return False
    elif abs(x)>14.4 or abs(z)>11.4: return False
    for sx,sz,w,d,_,_ in (UPPER if floor else GROUND):
        if abs(x-sx)<w/2+radius and abs(z-sz)<d/2+radius: return False
    return True

def path_to(x,z,tx,tz,floor):
    if not clear(tx,tz,floor): raise ValueError('That spot is blocked. Choose an open part of the floor.')
    start=(round(x),round(z)); goal=(round(tx),round(tz))
    # Snap a fractional destination away from a wall onto the nearest open grid node.
    if not clear(*goal,floor):
        choices=[(goal[0]+dx,goal[1]+dz) for dx in (-1,0,1) for dz in (-1,0,1) if clear(goal[0]+dx,goal[1]+dz,floor)]
        if not choices: raise ValueError('No walkable destination nearby.')
        goal=min(choices,key=lambda p:(p[0]-tx)**2+(p[1]-tz)**2)
    queue=deque([start]); came={start:None}
    while queue and len(came)<3500:
        p=queue.popleft()
        if p == goal: break
        for dx,dz in ((0,-1),(1,0),(0,1),(-1,0)):
            n=(p[0]+dx,p[1]+dz)
            if n not in came and clear(*n,floor): came[n]=p;queue.append(n)
    if goal not in came: raise ValueError('No walking route reaches that destination.')
    steps=[]; p=goal
    while p != start: steps.append(p);p=came[p]
    steps.reverse()
    return steps

PRESETS=('wanderer','warden','scholar','forager','nomad','capybara','goblin','golem','doge','chad')
def appearance(data):
    if not isinstance(data,dict):raise ValueError('Character must be an object.')
    result={}
    for key,values in [('preset',PRESETS),('headwear',('none','straw','cap','top','bandana')),('hairStyle',('short','long','bun','ponytail','shaved')),('build',('slim','medium','stocky'))]:
        if key in data:
            if data[key] not in values:raise ValueError('Unknown character '+key+'.')
            result[key]=data[key]
    for key in ('skinColor','bodyColor','pantsColor','hairColor','eyeColor'):
        if key in data:
            if not isinstance(data[key],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',data[key]):raise ValueError('Choose a valid character color.')
            result[key]=data[key].lower()
    if 'height' in data:
        height=data['height']
        if type(height) not in (int,float) or not math.isfinite(height) or not 1.3<=height<=2.1:raise ValueError('Character height must be between 1.3 and 2.1.')
        result['height']=height
    return result

def resident_appearance(index):
    return {'skinColor':'#%02x%02x%02x'%(150+index*2,115+index,80+index),'preset':PRESETS[index%len(PRESETS)],'headwear':('straw','cap','top','bandana','none')[index%5],'bodyColor':['#456552','#374b72','#a55244','#887344','#574365','#376e70'][index%6], 'hairStyle':['short','long','bun','ponytail','shaved'][index%5],'height':round(1.4+(index%8)*.08,2),'build':['slim','medium','stocky'][index%3]}

class HotelWorld:
    def __init__(self,clock=time.monotonic):
        self.clock=clock; self.last=clock(); self.people={};self.residents=[]
        families=[('Moss','Concierge','sage','A warm welcome and a key to your room.','checkin'),('Inkwell','Librarian','blue','Books, sources, and a quiet place to think.','services/library'),('Pip','Bellhop','rose','Packages, room deliveries, and directions.','services/bellhop'),('Fern','Host','sage','Find a seat and settle into the hotel.','services/walk'),('Tally','Workshop keeper','blue','A desk for tools and test results.','services/workshop'),('Quill','Writer in residence','rose','A fresh page and a second draft.','services/writing'),('Lock','Night porter','sage','A familiar face on every floor.','services/rooms'),('Echo','Guest guide','blue','Help finding your way around.','services')]
        upper_names=['Brass', 'Vellum', 'Sable', 'Clover', 'Cinder', 'Marble', 'Lumen', 'Rue', 'Cobalt', 'Osier', 'Thimble', 'Morrow', 'Juniper', 'Fable', 'Gasket', 'Opal', 'Briar', 'Selkie', 'Filigree', 'Truffle', 'Patch', 'Gossamer', 'Rook', 'Dulse', 'Nacre', 'Tinsel', 'Mistral', 'Saffron', 'Tock', 'Wisp', 'Auburn', 'Mim', 'Periwinkle']
        upper_traits=['a living reception bell', 'a folded parchment heron', 'a velvet moth', 'a walking bonsai', 'an ember-backed salamander', 'an ivory stone gargoyle', 'a lantern-headed firefly', 'a ribbon eel', 'a porcelain crab', 'a wicker basket creature', 'a thimble-bodied tailor', 'a midnight bat', 'a mantis gardener', 'a living leather book', 'a brass beetle', 'an opal snail', 'a rose-headed gardener', 'a long-necked seal', 'a gold-wire peacock', 'a mushroom chef', 'a traveling suitcase', 'a jellyfish seamstress', 'a chess-rook porter', 'a coral seahorse', 'a clam-shell pianist', 'a magpie collector', 'a spiral cloud', 'a gecko sommelier', 'a clockwork owl', 'a porcelain ghost', 'a lobster porter', 'an origami fox', 'an ammonite librarian']
        upper_roles=['Reception assistant', 'Archivist', 'Tea attendant', 'Gardener', 'Fire keeper', 'Coffee host', 'Lamp lighter', 'Tailor', 'Tea attendant', 'Florist', 'Tailor', 'Night guide', 'Gardener', 'Librarian', 'Mechanic', 'Key keeper', 'Florist', 'Towel attendant', 'Salon host', 'Chef', 'Bellhop', 'Seamstress', 'Porter', 'Navigator', 'Musician', 'Collector', 'Weather keeper', 'Sommelier', 'Timekeeper', 'Flower courier', 'Bellhop', 'Cartographer', 'Librarian']
        ground=[(-8,0),(-10,-8),(3,6),(-6,6),(8,-5),(11,3),(-3,-9),(6,8)]
        for floor in range(12):
            for j in range(8 if floor==0 else 3):
                index=j if floor==0 else (floor+j)%8
                name,role,color,bio,service=families[index]
                if floor:
                    k=(floor-1)*3+j
                    name=upper_names[k];role=upper_roles[k];bio=name+' is '+upper_traits[k]+', with a place and a purpose of their own in the hotel.';service='services'
                bio=name+' works as the hotel’s '+role.lower()+'. Find them around the desks and guest floors.'
                ident=name.lower()
                x,z=ground[j] if floor==0 else [(-6,-6),(6,2),(0,6)][j]
                self.residents.append(dict(id='staff-'+ident,name=name,character=ident,appearance=resident_appearance(len(self.residents)),role=role,portrait=color,bio=bio,service=service,home_floor=floor,room=f'{floor:02}{j+1}',floor=floor,x=float(x),z=float(z),heading=0.,kind='agent',ambient=True,path=[],phase=j,wait_until=self.last+j*.8,activity='Settling in',speech='',journeys=0))

    def tick_residents(self,now,dt):
        ground=[(-8,0),(-10,-6),(3,6),(-6,6),(8,-5),(11,3),(-3,-9),(6,8),(0,-9)]
        upper=[(-6,-6),(6,2),(0,6),(-6,10),(6,-10),(0,-9)]
        for i,p in enumerate(self.residents):
            distance=dt*2.1
            while p['path'] and distance>0:
                tx,tz=p['path'][0];dx,dz=tx-p['x'],tz-p['z'];d=math.hypot(dx,dz)
                if d<.001:p['path'].pop(0);continue
                step=min(d,distance);nx=p['x']+dx/d*step;nz=p['z']+dz/d*step
                if not clear(nx,nz,p['floor']):p['path']=[];break
                p['x'],p['z']=nx,nz;p['heading']=math.atan2(dx,dz);distance-=step
                if d<=step+.001:p['path'].pop(0)
            if p['path']:continue
            if 'next_floor' in p:
                destination=p.pop('next_floor')
                if math.hypot(p['x'],p['z']+9)<.6:p['floor']=destination;p['x']=0.;p['z']=-9.;p['activity']='Leaving the lift';p['wait_until']=now+3
            if now<p['wait_until']:continue
            p['phase']+=1
            if p['phase']%2:
                p['activity']=['Checking the register','Reading at a desk','Delivering a package','Chatting in the lounge','Working at a desk'][i%5]
                p['speech']=['Welcome to the Grand.','One more page...','A delivery for upstairs.','Shall we find a seat?',"Let's check that again."][i%5]
                p['wait_until']=now+7+(i%5);continue
            points=upper if p['floor'] else ground
            tx,tz=points[(p['phase']//2+i)%len(points)]
            if i%7==2 and p['phase']%6==0:
                tx,tz=0,-9;p['next_floor']=(p['floor']+1)%12
            try:p['path']=path_to(p['x'],p['z'],tx,tz,p['floor'])
            except ValueError:p.pop('next_floor',None);p['wait_until']=now+2;continue
            p['activity']='Taking the lift' if 'next_floor' in p else 'Walking to the next desk';p['speech']='';p['wait_until']=now+4

    def tick(self):
        now=self.clock();dt=max(0,min(now-self.last,1));self.last=now
        self.tick_residents(now,dt)
        for owner,p in list(self.people.items()):
            if now-p['seen']>180: del self.people[owner];continue
            distance=dt*4.5
            while p['path'] and distance>0:
                tx,tz=p['path'][0];dx,dz=tx-p['x'],tz-p['z'];d=math.hypot(dx,dz)
                if d<.001:p['path'].pop(0);continue
                step=min(d,distance);nx=p['x']+dx/d*step;nz=p['z']+dz/d*step
                if not clear(nx,nz,p['floor']):p['path']=[];break
                p['x'],p['z']=nx,nz;p['heading']=math.atan2(dx,dz);distance-=step
                if d<=step+.001:p['path'].pop(0)
            if not p['path'] and p.get('lift_to') is not None:
                floor=p.pop('lift_to')
                if math.hypot(p['x'],p['z']+9)<.6:
                    p['floor']=floor;p['x']=0;p['z']=-9;p['destination']='Lift arrival'

    def get(self,owner):
        if owner not in self.people: raise ValueError('Enter the hotel first.')
        p=self.people[owner];p['seen']=self.clock();return p

    def snapshot(self,owner):
        self.tick()
        if owner in self.people:self.people[owner]['seen']=self.clock()
        visible=[]
        for p in self.people.values():
            visible.append({k:p[k] for k in ('id','name','kind','x','z','floor','heading','destination','appearance')})
            visible[-1]['walking']=bool(p['path'])
        me=self.people.get(owner)
        residents=[{**{k:v for k,v in p.items() if k not in ('path','wait_until','phase','next_floor','journeys')},'walking':bool(p['path'])} for p in self.residents]
        return {'you':me['id'] if me else None,'people':visible,'residents':residents,'floors':12,'speed':4.5,
                'landmarks':LANDMARKS,'ground_solids':GROUND,'upper_solids':UPPER}

    def command(self,owner,command,data):
        self.tick();now=self.clock()
        if command == 'enter':
            kind=data.get('kind','human')
            chosen=appearance(data.get('appearance',{}))
            if kind not in ('human','agent'):raise ValueError('Choose human or agent.')
            if owner not in self.people and len(self.people)>=64:raise ValueError('The hotel walk is full. Try again shortly.')
            if owner not in self.people:
                self.people[owner]={'id':secrets.token_hex(8),'name':str(data.get('name','Guest')).strip()[:32] or 'Guest',
                    'kind':kind,'x':0.,'z':6.,'floor':0,'heading':math.pi,'path':[],
                    'seen':now,'move_at':now-.2,'destination':'Lobby'}
            else:self.people[owner]['kind']=kind
            self.people[owner]['appearance']=chosen
            self.people[owner]['name']=str(data.get('name',self.people[owner]['name'])).strip()[:32] or 'Guest'
        elif command == 'leave': self.people.pop(owner,None)
        else:
            p=self.get(owner)
            if command == 'appearance':p['appearance']=appearance(data.get('appearance',{}))
            elif command == 'move':
                dx,dz=float(data.get('dx',0)),float(data.get('dz',0))
                if not math.isfinite(dx) or not math.isfinite(dz):raise ValueError('Movement must be finite.')
                p['path']=[];p.pop('lift_to',None);p['destination']='Walking'
                length=math.hypot(dx,dz);amount=min(.25,max(0,now-p['move_at']))*4.5;p['move_at']=now
                if length:
                    dx=dx/length*amount;dz=dz/length*amount
                    # Small substeps prevent corner cutting or tunnelling.
                    for _ in range(5):
                        if clear(p['x']+dx/5,p['z'],p['floor']):p['x']+=dx/5
                        if clear(p['x'],p['z']+dz/5,p['floor']):p['z']+=dz/5
                    p['heading']=math.atan2(dx,dz)
            elif command == 'target':
                p.pop('lift_to',None)
                if 'landmark' in data:
                    if p['floor'] and data['landmark']!='lift':raise ValueError('Take the lift to the ground floor for this destination.')
                    target=LANDMARKS.get(data['landmark'])
                    if not target:raise ValueError('Unknown destination.')
                    tx,tz=target['x'],target['z'];p['destination']=target['name']
                else:
                    tx,tz=float(data['x']),float(data['z']);p['destination']='Selected spot'
                p['path']=path_to(p['x'],p['z'],tx,tz,p['floor'])
            elif command == 'floor':
                f=data.get('floor')
                if type(f) is not int or not 0<=f<12:raise ValueError('The hotel has floors 0 through 11.')
                p['path']=path_to(p['x'],p['z'],0,-9,p['floor']);p['lift_to']=f;p['destination']='Lift → '+('Lobby' if f==0 else f'Floor {f:02}')
            elif command == 'stop':p['path']=[];p.pop('lift_to',None);p['destination']='Stopped'
            else:raise ValueError('Unknown walking command.')
        return self.snapshot(owner)

WORLD=HotelWorld()
