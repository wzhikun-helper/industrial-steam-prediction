"""Offline delivery preflight. Never trains, predicts, compiles papers or installs.

--with-data explicitly permits Schema-only dry-runs over locally authorized data.
Detailed logs are exclusive outputs in a fresh staging/reproduction run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.runtime import create_run_dir, open_new_output

STAGES=('ridge-baseline','tree-baselines','feature-processing','ridge-tuning',
        'xgboost-tuning','fusion','shap','final-prediction')
REQUIRED_FILES=('README.md','environment.yml','configs/experiment.yaml',
                'scripts/FUSION_PROTOCOL.md','scripts/MIGRATION_SAFETY.md',
                'scripts/REMAINING_PROTOCOLS.md','docs/FINAL_PROJECT_ACCEPTANCE.md',
                '.agents/skills/ml-experiment-audit/SKILL.md',
                'paper/acm_mm_layout_revision/BUILD.md','paper/zju_zh_layout_revision/BUILD.md')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--with-data',action='store_true')
    parser.add_argument('--official-validator',help='Optional installed skill-creator quick_validate.py; not a clone prerequisite')
    args=parser.parse_args()
    create_run_dir(ROOT,args.output_dir)
    checks=[]
    missing=[p for p in REQUIRED_FILES if not (ROOT/p).is_file()]
    checks.append({'check':'required_delivery_files','exit_code':2 if missing else 0,'missing':missing})

    def save(name,data):
        with open_new_output(ROOT,args.output_dir,name) as stream:
            stream.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2))

    def check(label,arguments):
        run=subprocess.run(arguments,cwd=ROOT,capture_output=True)
        out=run.stdout.decode('utf-8',errors='replace')
        err=run.stderr.decode('utf-8',errors='replace')
        save(label+'.txt',out+'\nSTDERR:\n'+err)
        record={'check':label,'exit_code':run.returncode}
        matches=re.findall(r'Ran (\d+) tests?',err)
        if matches:
            total=int(matches[-1]); skip=re.search(r'skipped=(\d+)',err)
            record.update(total=total,skipped=int(skip.group(1)) if skip else 0)
            record['passed']=total-record['skipped'] if run.returncode==0 else None
        checks.append(record)
        return out

    py=[sys.executable,'-B']
    check('unit_tests',py+['-m','unittest','discover','-s','tests','-v'])
    check('skill_tests',py+['.agents/skills/ml-experiment-audit/scripts/test_checks.py'])
    if args.official_validator:
        check('official_skill_validation',py+[args.official_validator,'.agents/skills/ml-experiment-audit'])
    for script in ('run_experiment','export_paper_results','verify_frozen_results','check_delivery','check_skill_discovery'):
        check('help_'+script,py+['scripts/'+script+'.py','--help'])
    for stage in STAGES:
        base=py+['scripts/run_experiment.py','--config','configs/experiment.yaml','--stage',stage,
                 '--output-dir',args.output_dir+'_unused_'+stage]
        check('check_only_'+stage,base+['--check-only'])
        if args.with_data:
            check('dry_run_'+stage,base+['--dry-run'])
    check('frozen_hashes_optimized',[sys.executable,'-B','-O','scripts/verify_frozen_results.py','--hashes-only'])
    check('export_dry_run',py+['scripts/export_paper_results.py','--output-dir',args.output_dir+'_unused_export','--dry-run'])
    skill=ROOT/'.agents/skills/ml-experiment-audit/SKILL.md'
    front=skill.read_text(encoding='utf-8').split('---',2)[1]
    if not re.search(r'(?m)^name: ml-experiment-audit$',front) or not re.search(r'(?m)^description: .+',front):
        checks.append({'check':'skill_metadata','exit_code':2})
    unused=list((ROOT/args.output_dir).parent.glob(Path(args.output_dir).name+'_unused_*'))
    report={'status':'PASS' if all(c['exit_code']==0 for c in checks) and not unused else 'NEEDS ATTENTION',
            'checks':checks,'unused_outputs_created':len(unused),'data_schema_dry_runs':args.with_data,
            'training_executed':False,'paper_compilation_performed':False,
            'notebook_sha256':hashlib.sha256((ROOT/'notebooks/01_experiment.ipynb').read_bytes()).hexdigest(),
            'notebook_note':'Working-copy identity only; unpublished Notebook changes are not a Fresh Clone prerequisite.'}
    save('checks.json',report)
    print(json.dumps(report,ensure_ascii=True,indent=2))
    return 0 if report['status']=='PASS' else 2


if __name__=='__main__':
    raise SystemExit(main())
