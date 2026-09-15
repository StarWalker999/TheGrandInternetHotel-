"""Replayable hotel tasks. Explicit rules, not a learned world model."""
import copy
import math
import time
import uuid
from world import clear, path_to, resident_appearance, GROUND, UPPER

def step(action,at,label,effect=None):
    return {'action':action,'at':at,'label':label,'effect':effect or {}}

DESK=[-8,0,0];LIBRARY=[-10,-8,0];SERVICE=[8,-5,0];LOUNGE=[-6,6,0];ROOM=[-6,-6,1];ENTRANCE=[0,16,0];LIFT=[0,-9,0]
def delivery(name,item,source,destination,skill,extra=None):
    return {'name':name,'item':item,'source':source,'destination':destination,'skill':skill,
        'steps':[step('pickup',source,'Collect '+item.lower()),step('deliver',destination,'Deliver '+item.lower())]+(extra or [])}
def service(name,item,steps,skill,objects=None):
    return {'name':name,'item':item,'source':steps[0]['at'],'destination':steps[-1]['at'],'steps':steps,'skill':skill,'objects':objects or {}}

TASKS = {
 'parcel':delivery('Library delivery','Parcel',DESK,LIBRARY,'Route planning and correct handoff'),
 'tea':delivery('Tea in the lounge','Tea tray',SERVICE,LOUNGE,'Service routing and delivery'),
 'room':delivery('Upstairs room service','Fresh towels',DESK,ROOM,'Multi-floor planning and room delivery'),
 'lost_property':delivery('Return lost property','Lost bag',LOUNGE,DESK,'Collection and return to reception'),
 'restock':delivery('Restock the service desk','Supply box',DESK,SERVICE,'Replenishment and stock placement',[step('arrange',SERVICE,'Put supplies away',{'supplies':'restocked'})]),
 'meeting':delivery('Prepare a meeting space','Meeting materials',DESK,LOUNGE,'Setup sequencing and readiness checks',[step('arrange',LOUNGE,'Arrange the meeting materials',{'meeting':'set up'}),step('inspect',LOUNGE,'Check the meeting space',{'meeting':'ready'})]),
 'housekeeping':service('Turn over a guest room','Guest room',[step('inspect',ROOM,'Inspect the guest room',{'room':'needs cleaning'}),step('clean',ROOM,'Clean and reset the room',{'room':'clean'}),step('inspect',ROOM,'Check the finished room',{'room':'ready'})],'Inspection, cleaning and quality checks',{'room':'used'}),
 'maintenance':delivery('Repair service equipment','Toolkit',DESK,SERVICE,'Diagnose, repair and test',[step('inspect',SERVICE,'Diagnose the equipment',{'equipment':'fault identified'}),step('repair',SERVICE,'Repair the equipment',{'equipment':'repaired'}),step('test',SERVICE,'Test the repaired equipment',{'equipment':'working'})]),
 'safety':service('Check the public areas','Public areas',[step('inspect',ENTRANCE,'Check the entrance',{'entrance':'obstruction found'}),step('clear',ENTRANCE,'Clear the entrance',{'entrance':'clear'}),step('inspect',LOUNGE,'Check the lounge',{'lounge':'checked'}),step('inspect',LIFT,'Check the lift approach',{'lift approach':'clear'})],'Inspection rounds and resolving an obstruction',{'entrance':'obstructed'}),
 'inventory':service('Count service supplies','Supply shelf',[step('inspect',SERVICE,'Inspect the supply shelf'),step('count',SERVICE,'Count the visible supply boxes',{'inventory':'count verified'}),step('report',DESK,'Report the count to reception',{'inventory':'reported'})],'Counting and reporting stock',{'inventory':'uncounted'}),
}
TASKS['inventory']['stock']=[{'id':'box-'+str(i+1),'kind':'supply box'} for i in range(7)]
WORK_ACTIONS=('pickup','deliver','inspect','clean','arrange','repair','test','clear','count','report')

def create(task):
    if not isinstance(task,str) or task not in TASKS: raise ValueError('Choose a hotel task.')
    run={'id':uuid.uuid4().hex,'created':time.time(),'version':'hotel-voxel-tasks/2','task':copy.deepcopy(TASKS[task]),'task_id':task,
         'status':'running','stage':'work','phase':0,'objects':copy.deepcopy(TASKS[task].get('objects',{})),'worker':{'x':0.,'z':6.,'floor':0,'heading':math.pi,'appearance':resident_appearance(2)},
         'path':[],'carrying':False,'actions':0,'rejected':0,'distance':0.,'seconds':0.,'frames':[]}
    record(run,'start','Task started. '+run['task']['steps'][0]['label']+'.')
    return run

def record(run,action,message,accepted=True):
    run['frames'].append({'seq':run['actions'],'action':action,'message':message,'accepted':accepted,
        'worker':copy.deepcopy(run['worker']),'carrying':run['carrying'],'stage':run['stage'],'status':run['status'],
        'rejected':run['rejected'],'phase':run['phase'],'objects':copy.deepcopy(run['objects']),'seconds':run['seconds'],'distance':round(run['distance'],3)})

def near(worker,spot):
    return worker['floor']==spot[2] and math.hypot(worker['x']-spot[0],worker['z']-spot[1])<=1.1

def advance(run):
    p=run['worker'];remaining=.9
    while run['path'] and remaining>0:
        x,z=run['path'][0];dx,dz=x-p['x'],z-p['z'];distance=math.hypot(dx,dz)
        if distance<.001:run['path'].pop(0);continue
        amount=min(distance,remaining);nx,nz=p['x']+dx/distance*amount,p['z']+dz/distance*amount
        if not clear(nx,nz,p['floor']):run['path']=[];return False,'The route is blocked.'
        p['x'],p['z'],p['heading']=nx,nz,math.atan2(dx,dz);run['distance']+=amount;remaining-=amount
        if amount>=distance-.001:run['path'].pop(0)
    return True,'Walking to the next stop.'

def apply(run,action,data=None):
    data=data or {}
    requested=action
    inputs={k:data[k] for k in ('x','z','dx','dz','floor','count') if k in data}
    if run['status']!='running':raise ValueError('This run has ended. Start another task.')
    if action not in ('step','target','advance','lift','move','stop')+WORK_ACTIONS:raise ValueError('Unknown simulation action.')
    if data.get('seq',run['actions'])!=run['actions']:raise ValueError('Run changed. Observe again before acting.')
    worker=run['worker'];task=run['task'];required=task['steps'][run['phase']];accepted=True;message='';actual=action
    if action=='step':
        goal=required['at']
        if near(worker,goal):
            actual=required['action']
            if actual=='count':data={**data,'count':len(task.get('stock',[]))};inputs['count']=data['count']
        elif worker['floor']!=goal[2] and near(worker,[0,-9,worker['floor']]):actual='lift';data={**data,'floor':goal[2]}
        else:
            tx,tz=(0,-9) if worker['floor']!=goal[2] else goal[:2]
            if not run['path']:run['path']=path_to(worker['x'],worker['z'],tx,tz,worker['floor'])
            actual='advance'
    if actual=='target':
        x,z=data.get('x'),data.get('z')
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (x,z)):raise ValueError('Provide finite x and z coordinates.')
        try:run['path']=path_to(worker['x'],worker['z'],x,z,worker['floor']);message='Route selected.'
        except ValueError as e:accepted=False;message=str(e)
    elif actual=='advance':accepted,message=advance(run)
    elif actual=='move':
        dx,dz=data.get('dx',0),data.get('dz',0)
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (dx,dz)):raise ValueError('Provide finite movement.')
        length=math.hypot(dx,dz);run['path']=[]
        if length:
            dx,dz=dx/length*.9,dz/length*.9
            # Test the entire move, not just its endpoint.
            if all(clear(worker['x']+dx*i/5,worker['z']+dz*i/5,worker['floor']) for i in range(1,6)):
                worker['x']+=dx;worker['z']+=dz;worker['heading']=math.atan2(dx,dz);run['distance']+=.9;message='Moved.'
            else:accepted=False;message='Furniture blocks that move.'
        else:message='Stayed in place.'
    elif actual in WORK_ACTIONS:
        if actual!=required['action']:accepted=False;message='First: '+required['label'].lower()+'.'
        elif not near(worker,required['at']):accepted=False;message='Move closer to the work point on floor '+str(required['at'][2])+'.'
        elif actual=='count' and (type(data.get('count')) is not int or data['count']!=len(task.get('stock',[]))):accepted=False;message='The count does not match the visible supply boxes.'
        else:
            if actual=='pickup':run['carrying']=True
            if actual=='deliver':run['carrying']=False
            run['objects'].update(required['effect']);run['phase']+=1;run['path']=[]
            message=required['label']+'. Done.'
            if actual=='pickup':message=task['item']+' collected.'
            if run['phase']==len(task['steps']):run['stage']='done';run['status']='completed';message+=' Task complete.'
            else:run['stage']='deliver' if run['carrying'] else 'work'
    elif actual=='lift':
        floor=data.get('floor')
        if type(floor) is not int or not 0<=floor<12:raise ValueError('Choose floor 0 through 11.')
        if not near(worker,[0,-9,worker['floor']]):accepted=False;message='Walk to the lift first.'
        else:worker.update(x=0.,z=-9.,floor=floor);run['path']=[];message='Arrived on floor '+str(floor)+'.'
    elif actual=='stop':run['status']='stopped';run['path']=[];message='Run stopped.'
    run['actions']+=1;run['seconds']=round(run['seconds']+.2,1)
    if not accepted:run['rejected']+=1
    if run['actions']>=1000 and run['status']=='running':run['status']='limit';message+=' Action limit reached.'
    record(run,actual,message,accepted)
    run['frames'][-1]['requested_action']=requested
    run['frames'][-1]['input']=inputs
    return run

def observe(run):
    result=copy.deepcopy(run)
    result['geometry']={'ground_solids':copy.deepcopy(GROUND),'upper_solids':copy.deepcopy(UPPER),'floors':12,'agent_radius':.35}
    result['observation']={'position':copy.deepcopy(run['worker']),'carrying':run['carrying'],
        'collection':run['task']['source'],'delivery':run['task']['destination'],'lift':[0,-9],
        'next_step':copy.deepcopy(run['task']['steps'][run['phase']]) if run['phase']<len(run['task']['steps']) else None,
        'objects':copy.deepcopy(run['objects']),'stock':copy.deepcopy(run['task'].get('stock',[])),
        'allowed_actions':['target','advance','move','lift','stop']+list(WORK_ACTIONS),
        'controller':'step runs the built-in rule-based job policy','tick_seconds':.2}
    return result
