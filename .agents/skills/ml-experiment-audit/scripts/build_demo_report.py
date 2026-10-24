"""Explicitly authorized frozen-CSV demonstration; no ML training or inference."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import textwrap

SKILL = Path(__file__).resolve().parents[1]
ADAPTER = {
    'models': ('results/paper_fig2_model_performance.csv', 'results/final_model_comparison.csv', 7),
    'features': ('results/paper_fig3_feature_method_comparison.csv', 'results/feature_method_comparison.csv', 3),
}
PROTOCOL = {'name': 'TimeSeriesSplit', 'n_splits': 5}
VALIDATION_CONTEXT = 'five TimeSeriesSplit validation folds'
SIGNIFICANCE_INFERENCE = False


def modules(root):
    sys.path.insert(0, str(Path(root).resolve(strict=True)))
    from src import frozen, runtime
    return frozen, runtime


def read_csv(root, relative, registry, frozen):
    if relative not in registry:
        raise ValueError('Unregistered CSV: '+relative)
    path = frozen.protected_path(root, relative)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != registry[relative]:
        raise ValueError('SHA256 drift: '+relative)
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not {'model','mse_mean'} <= set(fields):
        raise ValueError('Invalid CSV schema')
    rows = list(reader)
    if not rows or len({r['model'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate model identities')
    for row in rows:
        if not row['model'] or None in row:
            raise ValueError('Malformed row')
        for key in fields:
            if key != 'model':
                value = float(row[key])
                if not math.isfinite(value) or (key.startswith('mse') and value < 0):
                    raise ValueError('Non-finite or negative error field')
                row[key] = value
    return rows


def ensure_same_protocol(protocols):
    if not protocols or any(p != PROTOCOL for p in protocols):
        raise ValueError('Mixed or unsupported evaluation protocols; never combine fusion and CV')


def preflight(root, output):
    root = Path(root).resolve(strict=True)
    frozen, runtime = modules(root)
    if not output.replace('\\','/').startswith('staging/'):
        raise ValueError('Demo outputs must be in a new staging run')
    runtime.validate_output_dir(root, output)
    registry = frozen.verify_registry(root)  # strict count + all SHA256 before CSV parsing
    config = json.loads((root/'configs/experiment.yaml').read_text(encoding='utf-8-sig'))
    ensure_same_protocol([config['validation']['primary']])
    if config['rmse_aggregation'] != 'mean_of_fold_rmse':
        raise ValueError('Unsupported metric aggregation')
    evidence, data = [], {}
    for name,(source, canonical, count) in ADAPTER.items():
        rows = read_csv(root, source, registry, frozen)
        base = read_csv(root, canonical, registry, frozen)
        if len(rows) != count or {r['model'] for r in rows} != {r['model'] for r in base}:
            raise ValueError('Model identities/count differ from canonical results')
        lookup = {r['model']:r for r in base}
        for row in rows:
            if 'mse_std' not in row:
                raise ValueError('Missing fold SD')
            for key,value in lookup[row['model']].items():
                if key != 'model' and not math.isclose(row[key],value,rel_tol=0,abs_tol=1e-12):
                    raise ValueError('Derived and canonical values differ')
        data[name] = sorted(rows,key=lambda r:r['mse_mean'])
        for rel in (source, canonical):
            evidence.append({'path':rel,'sha256':registry[rel], 'protocol':PROTOCOL})
    ensure_same_protocol([e['protocol'] for e in evidence])
    return root, frozen, runtime, config, data, evidence


def write_json(root, output, name, data, runtime):
    with runtime.open_new_output(root, output, name) as stream:
        json.dump(data,stream,indent=2,ensure_ascii=True)


def save(fig, root, output, stem, formats, dpi):
    """Exclusive three-format export, reusing the project runtime write guard."""
    _,runtime=modules(root)
    for extension in formats:
        with runtime.open_new_binary_output(root,output,f'{stem}.{extension}') as stream:
            fig.savefig(stream,format=extension,dpi=dpi)


def build(root, output, authorized=False):
    if not authorized:
        raise PermissionError('Explicit human demo authorization required; no training capability')
    root, frozen, runtime, config, data, evidence = preflight(root, output)
    run = runtime.create_run_dir(root,output)
    try:
        write_json(root,output,'config_snapshot.json',config,runtime)
        write_json(root,output,'input_manifest.json',evidence,runtime)
        write_json(root,output,'plotted_values.json',data,runtime)
        write_json(root,output,'figure_contract.json',{
            'claims': ['Best Ridge has the lowest mean MSE but is numerically close to Ridge.',
                       'Neither feature-processing alternative improves Ridge in this setting.'],
            'encoding':'sorted dot-whisker; absolute MSE; +/-1 fold SD; no significance inference',
            'sources':evidence, 'training_executed':False},runtime)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        from matplotlib import font_manager
        from PIL import Image
        sys.path.insert(0,str(root/'scripts/figures'))
        from _style import paper_style, PALETTE
        paper_style(font='sans')
        font = font_manager.findfont('Arial',fallback_to_default=False)
        chart_manifest = []
        pages = []
        for index,(name,rows) in enumerate(data.items(),1):
            fig,ax = plt.subplots(figsize=(6.6,3.6))
            fig.subplots_adjust(left=.25,right=.96,bottom=.21,top=.86)
            for i,row in enumerate(rows):
                best = row['model'] in ('Best Ridge','Ridge') and i == 0
                tuned = row['model'].startswith('Best ') or best
                marker = "D" if tuned else "o"
                color = PALETTE[0] if best else '#555555'
                face = 'white' if row['model']=='Best XGBoost' else color
                ax.errorbar(row['mse_mean'],i,xerr=row['mse_std'],fmt='none',ecolor='#999999',elinewidth=.75,capsize=2)
                ax.plot(row['mse_mean'],i,marker=marker,ms=5,color=color,markerfacecolor=face)
                ax.annotate(f"{row['mse_mean']:.4f}",(row['mse_mean'],i),xytext=(5,6),textcoords='offset points',fontsize=8,color='#444444')
            ax.set_yticks(range(len(rows)))
            ax.set_yticklabels([r['model'] for r in rows],fontsize=9)
            ax.set_ylim(len(rows)-.5,-.6)
            lo=min(r['mse_mean']-r['mse_std'] for r in rows)
            hi=max(r['mse_mean']+r['mse_std'] for r in rows)
            ax.set_xlim(max(0,lo-.12*(hi-lo)),hi+.12*(hi-lo))
            ax.set_xlabel('Mean squared error (MSE; lower is better)',fontsize=10)
            ax.tick_params(labelsize=9)
            ax.set_title('Model comparison' if name=='models' else 'Feature-processing comparison',loc='left',fontsize=12,pad=23)
            fig.text(.25,.89,f"N = {config['data']['train_shape'][0]:,} (configuration); 5 TimeSeriesSplit folds",fontsize=8,color='#666666')
            fig.text(.25,.045,'Error bars: +/-1 SD across five TimeSeriesSplit validation folds.',fontsize=8,color='#555555')
            save(fig, root, output, f'demo_{name}', formats=("pdf", "svg", "png"), dpi=300)
            with Image.open(run/f'demo_{name}.png') as im:
                with runtime.open_new_binary_output(root,output,f'demo_{name}_gray.png') as stream:
                    im.convert('L').save(stream,format='PNG')
            chart_manifest.append({'figure':name,'outputs':[f'demo_{name}.{e}' for e in ('pdf','svg','png')],
                                   'source':ADAPTER[name][0], 'protocol':PROTOCOL})
            pages.append((fig,name))
        # A genuinely new two-page vector document, not a copy of a manuscript.
        with runtime.open_new_binary_output(root,output,'demo_report.pdf') as stream:
            with PdfPages(stream,metadata={'Title':'Industrial Steam ML Workflow Demonstration','Author':'Saved-result reporting workflow'}) as pdf:
                for fig,name in pages:
                    # Recreate the chart as vector artists by relocating its axes.
                    fig.set_size_inches(8.27,11.69)
                    fig.axes[0].set_position([.25,.47,.67,.29])
                    for artist in list(fig.texts):
                        artist.remove()
                    fig.text(.09,.94,'Industrial Steam ML Workflow Demonstration',fontsize=17,weight='bold')
                    fig.text(.09,.90,f'Page {1 if name=="models" else 2} | Archived results, not a new experiment',fontsize=11,color='#555555')
                    fig.text(.25,.835,f"N = {config['data']['train_shape'][0]:,} (configuration); 5 TimeSeriesSplit folds",fontsize=9,color='#555555')
                    notes = ([
                        'The original protocol compares all seven models using five ordered TimeSeriesSplit folds.',
                        'Points show mean MSE. Whiskers show +/-1 fold standard deviation, not uncertainty from repeated independent trials.',
                        'Best Ridge and Ridge are numerically close; no statistical significance is inferred.',
                    ] if name=='models' else [
                        'All 38 original features outperform KBest20 and PCA95 in this dataset and evaluated setting.',
                        'This does not establish that feature selection is generally ineffective.',
                        'No raw data, unlabeled test data, stored models or fusion predictions were opened.',
                    ])
                    notes += ['Sources: '+ADAPTER[name][0], 'Canonical check: '+ADAPTER[name][1],
                              'Limitations: anonymous feature semantics; no repeated independent trials.',
                              'Five-fold CV is not comparable as a leaderboard with the 481-row fusion-validation subset.',
                              'Source SHA256 and full-precision plotted values are retained alongside this PDF.']
                    fig.text(.09,.39,'Provenance and interpretation',fontsize=12,weight='bold')
                    y=.36
                    for note in notes:
                        lines=textwrap.wrap(note,92)
                        fig.text(.09,y,'\n'.join(lines),fontsize=10,va='top',linespacing=1.5)
                        y-=.016*len(lines)+.009
                    fig.text(.09,.06,'Demo only - no training, tuning, inference or significance testing.',fontsize=9,color='#666666')
                    pdf.savefig(fig)
                    plt.close(fig)
        write_json(root,output,'figure_manifest.json',chart_manifest,runtime)
        command=['pdftoppm','-r','110','-png',str(run/'demo_report.pdf'),str(run/'page')]
        result=subprocess.run(command,capture_output=True,text=True,errors='replace')
        write_json(root,output,'build_record.json',{'builder':'matplotlib PdfPages','argv':sys.argv,'render_command':command,'render_exit_code':result.returncode,
            'render_stderr':result.stderr,'font':font,'python':sys.version,'matplotlib':matplotlib.__version__,'training_executed':False,
            'script_sha256':frozen.file_sha256(Path(__file__)),
            'style_sha256':frozen.file_sha256(root/'scripts/figures/_style.py')},runtime)
        if result.returncode:
            raise RuntimeError('PDF rendering failed')
        frozen.verify_registry(root)
        write_json(root,output,'build_status.json',{'status':'BUILT_AWAITING_VISUAL_REVIEW','pages':2,'exit_code':0},runtime)
        return run
    except Exception as exc:
        write_json(root,output,'failure.json',{'status':'FAIL','error':str(exc)},runtime)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True)
    p.add_argument('--output-dir',required=True)
    flags=p.add_mutually_exclusive_group()
    flags.add_argument('--authorize-demo',action='store_true')
    flags.add_argument('--check-only',action='store_true')
    args=p.parse_args()
    try:
        if not args.authorize_demo:
            *_,evidence=preflight(args.project_root,args.output_dir)
            print(json.dumps({'status':'CHECK_ONLY','read_only':True,'output_created':False,'inputs':evidence}))
        else:
            print(build(args.project_root,args.output_dir,authorized=True))
        return 0
    except Exception as exc:
        print(json.dumps({'status':'NEEDS ATTENTION','error':str(exc)}))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
