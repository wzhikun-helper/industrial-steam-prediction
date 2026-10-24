"""Verify saved-CSV demo artifacts. Completion requires actual page-review evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from build_demo_report import ADAPTER, modules, read_csv, write_json, ensure_same_protocol


def validate_mapping(figures):
    if len(figures)!=len(ADAPTER) or {f['figure'] for f in figures}!=set(ADAPTER):
        raise ValueError('Incomplete or duplicate figure mapping')
    ensure_same_protocol([f['protocol'] for f in figures])
    for f in figures:
        name=f['figure']
        if f['source']!=ADAPTER[name][0] or f['outputs']!=[f'demo_{name}.{e}' for e in ('pdf','svg','png')]:
            raise ValueError('Figure/source/artifact mapping differs')


def verify(root, relative):
    root=Path(root).resolve(strict=True)
    frozen,runtime=modules(root)
    if not relative.replace('\\','/').startswith('staging/'):
        raise ValueError('Expected isolated staging run')
    run=runtime._new_output_path(root,relative,'demo_report.pdf').parent
    if (run/'failure.json').exists():
        raise ValueError('Run has a failure record')
    registry=frozen.verify_registry(root)
    manifests=json.loads((run/'input_manifest.json').read_text())
    expected={p for a in ADAPTER.values() for p in a[:2]}
    if {e['path'] for e in manifests} != expected or len(manifests)!=len(expected):
        raise ValueError('Incomplete or duplicate source mapping')
    for e in manifests:
        if e['sha256']!=registry[e['path']]:
            raise ValueError('Source manifest digest mismatch')
    plotted=json.loads((run/'plotted_values.json').read_text())
    figures=json.loads((run/'figure_manifest.json').read_text())
    validate_mapping(figures)
    from PIL import Image
    for name,(source,_,_) in ADAPTER.items():
        actual=sorted(read_csv(root,source,registry,frozen),key=lambda r:r['mse_mean'])
        if plotted[name]!=actual:
            raise ValueError('Plotted values differ from registered CSV')
        mapping=next(f for f in figures if f['figure']==name)
        if mapping['source']!=source or mapping['outputs']!=[f'demo_{name}.{e}' for e in ('pdf','svg','png')]:
            raise ValueError('Figure provenance mapping differs')
        for ext in ('pdf','svg','png'):
            p=runtime._new_output_path(root,relative,f'demo_{name}.{ext}')
            if not p.is_file() or p.stat().st_size==0:
                raise ValueError('Missing figure artifact')
        with Image.open(run/f'demo_{name}.png') as im:
            if abs(im.info.get('dpi',(0,0))[0]-300)>.1:
                raise ValueError('PNG is not 300 dpi')
    pdf=run/'demo_report.pdf'
    info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,errors='replace',check=True)
    import re
    count=int(re.search(r'Pages:\s+(\d+)',info.stdout).group(1))
    if count!=2:
        raise ValueError('Expected two-page report')
    text=subprocess.run(['pdftotext',str(pdf),'-'],capture_output=True,text=True,errors='replace',check=True).stdout
    for rows in plotted.values():
        for row in rows:
            if f"{row['mse_mean']:.4f}" not in text or row['model'] not in text:
                raise ValueError('PDF text lacks expected labels')
    pages=[run/f'page-{i}.png' for i in range(1,count+1)]
    if any(not p.is_file() for p in pages):
        raise ValueError('Missing page renders')
    status='MECHANICAL_PASS_AWAITING_VISUAL'
    review=run/'visual_review.json'
    if review.is_file():
        report=json.loads(review.read_text())
        if not report.get('reviewer') or len(report.get('pages',[]))!=count:
            raise ValueError('Incomplete visual review')
        for i,p in enumerate(pages):
            record=report['pages'][i]
            if record['path']!=p.name or record['sha256']!=frozen.file_sha256(p) or record['status']!='PASS' or not record.get('observations'):
                raise ValueError('Visual review does not match actual pages')
        status='PASS'
    result={'status':status,'pages':count,'sources':len(manifests),'figures':len(figures),'training_executed':False,
            'artifact_sha256':{p.name:frozen.file_sha256(p) for p in run.iterdir() if p.suffix in ('.pdf','.svg','.png')}}
    if status=='PASS':
        if (run/'completion.json').exists():
            if json.loads((run/'completion.json').read_text())!=result:
                raise ValueError('Existing completion no longer matches artifacts')
        else:
            write_json(root,relative,'completion.json',result,runtime)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True)
    p.add_argument('--run-dir',required=True)
    args=p.parse_args()
    try:
        print(json.dumps(verify(args.project_root,args.run_dir),indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'status':'NEEDS ATTENTION','error':str(exc)}))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
