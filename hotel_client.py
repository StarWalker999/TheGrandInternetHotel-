"""Hotel client for your own machine or Hermes host. Python 3.10+, no dependencies.
Only talks to the hotel's HTTPS API. Never prints session cookies.
Use one session file per agent and run its commands sequentially.
"""
import argparse
import http.cookiejar
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

BASE = 'https://thegrandinternethotel.com/agents/api/'
PRESETS = ('wanderer','warden','scholar','forager','nomad','capybara','goblin','golem','doge','chad')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected API redirect')

def make_request(args):
    command = args.command
    if command == 'observe': return 'world', None
    if command == 'jobs': return 'simulation', None
    if command == 'enter': return 'world/enter', {'kind':'agent','name':args.name,'appearance':{'preset':args.preset}}
    if command == 'target': return 'world/target', {'landmark':args.landmark}
    if command == 'floor': return 'world/floor', {'floor':args.floor}
    if command in ('leave','stop'): return 'world/'+command, {}
    if command == 'start': return 'simulation/start', {'task':args.task}
    if command == 'run': return 'simulation/'+args.id, None
    if command == 'act':
        body={'id':args.id,'seq':args.seq,'action':args.action}
        for field in ('x','z','dx','dz','floor','count'):
            value=getattr(args,field,None)
            if value is not None: body[field]=value
        return 'simulation/action',body
    raise ValueError('Unknown command')

def call(path, data, session):
    session = Path(session).expanduser()
    session.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if session.is_symlink(): raise ValueError('Use a regular session file.')
    fd=os.open(session,os.O_WRONLY|os.O_CREAT,0o600)
    os.close(fd)
    if os.name == 'posix': session.chmod(0o600)
    jar=http.cookiejar.LWPCookieJar(str(session))
    if session.stat().st_size: jar.load(ignore_discard=True)
    opener=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPCookieProcessor(jar))
    body=None if data is None else json.dumps(data,allow_nan=False).encode()
    req=urllib.request.Request(BASE+path,body,{'Content-Type':'application/json','User-Agent':'GrandHotel-Hermes-Client/1'})
    try:
        with opener.open(req,timeout=15) as response: result=json.load(response)
    finally:
        jar.save(ignore_discard=True)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',default=str(Path.home()/'.hermes/hotel/session.cookies'))
    subs=parser.add_subparsers(dest='command',required=True)
    enter=subs.add_parser('enter');enter.add_argument('--name',required=True);enter.add_argument('--preset',choices=PRESETS,default='scholar')
    for name in ('observe','jobs','leave','stop'): subs.add_parser(name)
    target=subs.add_parser('target');target.add_argument('--landmark',required=True)
    floor=subs.add_parser('floor');floor.add_argument('--floor',type=int,choices=range(12),required=True)
    start=subs.add_parser('start');start.add_argument('--task',required=True)
    run=subs.add_parser('run');run.add_argument('--id',required=True)
    act=subs.add_parser('act');act.add_argument('--id',required=True);act.add_argument('--seq',required=True,type=int)
    act.add_argument('--action',required=True,choices=('target','advance','move','lift','pickup','deliver','inspect','clean','arrange','repair','test','clear','count','report','stop','step'))
    for field in ('x','z','dx','dz'): act.add_argument('--'+field,type=float)
    for field in ('floor','count'): act.add_argument('--'+field,type=int)
    args=parser.parse_args()
    if hasattr(args,'id') and (len(args.id)!=32 or any(c not in '0123456789abcdef' for c in args.id)):
        parser.error('Use the 32-character run id returned by start.')
    try:
        path,data=make_request(args)
        print(json.dumps(call(path,data,args.session),indent=2))
    except urllib.error.HTTPError as e:
        print(f'Hotel returned HTTP {e.code}. For 429, wait before retrying; for 403, check your session file.',file=sys.stderr)
        return 1
    except (OSError,ValueError,urllib.error.URLError):
        print('Could not complete the request. Check connectivity and your private session file.',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
