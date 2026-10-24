"""Actual installed Codex skills/list probe; no model turn or training.

Requires installed Codex CLI and permission for its own user-state initialization.
Only a repo-scoped enabled skill counts: user-level installation cannot mask omission.
"""
import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.runtime import create_run_dir,open_new_output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    create_run_dir(ROOT,args.output_dir)
    cli=shutil.which('codex')
    if not cli:
        raise SystemExit('Codex CLI unavailable; discovery not verified')
    js=Path(cli).parent/'node_modules/@openai/codex/bin/codex.js'
    command=[shutil.which('node'),str(js)] if js.is_file() else [cli]
    process=subprocess.Popen(command+['app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    messages=queue.Queue()
    diagnostics=[]
    def read_stdout():
        for line in iter(process.stdout.readline,b''):
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass
    def read_stderr():
        for line in iter(process.stderr.readline,b''):
            diagnostics.append(line.decode('utf-8',errors='replace'))
    threading.Thread(target=read_stdout,daemon=True).start()
    threading.Thread(target=read_stderr,daemon=True).start()
    def request(value):
        process.stdin.write((json.dumps(value)+'\n').encode()); process.stdin.flush()
    def response(identifier):
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            try:
                event=messages.get(timeout=1)
            except queue.Empty:
                if process.poll() is not None:
                    raise RuntimeError('Codex app-server exited')
                continue
            if event.get('id')==identifier:
                if 'error' in event:
                    raise RuntimeError('Codex API returned an error')
                return event['result']
        raise TimeoutError('Codex skills/list timeout')
    try:
        request({'id':1,'method':'initialize','params':{'clientInfo':{'name':'delivery-discovery','version':'1.0'},'capabilities':{'experimentalApi':True}}})
        init=response(1)
        request({'method':'initialized','params':{}})
        request({'id':2,'method':'skills/list','params':{'cwds':[str(ROOT)],'forceReload':True}})
        data=response(2)
        matches=[s for record in data.get('data',[]) for s in record.get('skills',[]) if s.get('name')=='ml-experiment-audit']
        repo=[s for s in matches if s.get('scope')=='repo' and s.get('enabled') and Path(s['path']).resolve()==(ROOT/'.agents/skills/ml-experiment-audit/SKILL.md').resolve()]
        report={'status':'PASS' if repo else 'NEEDS ATTENTION','enabled_repo_matches':len(repo),
                'other_matching_scopes':[s.get('scope') for s in matches if s not in repo],
                'repo_path':'.agents/skills/ml-experiment-audit/SKILL.md','server_version':init.get('userAgent'),
                'model_turn_started':False,'raw_data_read':False}
        with open_new_output(ROOT,args.output_dir,'discovery.json') as stream:
            json.dump(report,stream,indent=2)
        print(json.dumps(report,ensure_ascii=True,indent=2))
        return 0 if repo else 2
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        with open_new_output(ROOT,args.output_dir,'stderr.txt') as stream:
            stream.write(''.join(diagnostics))


if __name__=='__main__':
    raise SystemExit(main())
