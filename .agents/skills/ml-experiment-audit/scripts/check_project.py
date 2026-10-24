"""Mechanical audit precheck only; stdout JSON, no training or artifact writes."""
import argparse
import csv
import json
from pathlib import Path, PureWindowsPath
from check_hashes import project_file

METRICS = {'regression': {'mse', 'rmse', 'mae', 'r2'},
           'classification': {'accuracy', 'macro_f1', 'weighted_f1', 'precision', 'recall'}}


def validate_config(config):
    if not isinstance(config, dict) or set(config)-{'task', 'metrics', 'required_files', 'split_metadata'}:
        raise ValueError('Unknown audit configuration fields')
    task = config.get('task')
    if task not in METRICS:
        raise ValueError('Task must be regression or classification')
    metrics = config.get('metrics')
    if not isinstance(metrics, list) or not metrics or any(not isinstance(m, str) or m not in METRICS[task] for m in metrics):
        raise ValueError('Metric/task mismatch')
    files = config.get('required_files')
    if not isinstance(files, list) or not files or any(not isinstance(p, str) for p in files):
        raise ValueError('required_files must be a nonempty string list')
    split = config.get('split_metadata')
    if split is not None:
        if not isinstance(split, dict) or set(split) != {'path', 'sample_column', 'group_column', 'split_column'} or any(not isinstance(v, str) or not v for v in split.values()):
            raise ValueError('Invalid split_metadata specification')
    return config


def validate_output(root, relative):
    clean = relative.replace('\\', '/')
    parts = clean.split('/')
    if len(parts) < 2 or parts[0] not in ('staging', 'reproduction'):
        raise ValueError('Future output must be below staging/ or reproduction/')
    path = project_file(root, clean)
    if path.exists():
        raise FileExistsError('Refusing existing output directory')
    # A precheck, not a writer. Actual writes must still use project runtime guards.
    return path


def split_metadata(root, spec):
    groups, sample_ids = {}, set()
    path = project_file(root, spec['path'])
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        columns = [spec[k] for k in ('sample_column', 'group_column', 'split_column')]
        if len(fields) != len(set(fields)) or not set(columns).issubset(fields):
            raise ValueError('Split metadata schema mismatch')
        counts = {}
        for row in reader:
            sample, group, split = (row[c] for c in columns)
            if not sample or not group or not split or sample in sample_ids:
                raise ValueError('Empty or duplicate split identity')
            sample_ids.add(sample)
            groups.setdefault(split, set()).add(group)
            counts[split] = counts.get(split, 0)+1
    if not sample_ids or len(groups) < 2:
        raise ValueError('Missing split groups')
    overlaps = {a+'/'+b: sorted(groups[a] & groups[b]) for a in groups for b in groups if a < b and groups[a] & groups[b]}
    return dict(rows=len(sample_ids), counts=counts, groups={s: sorted(g) for s, g in groups.items()}, overlaps=overlaps)


def check_project(root, config, output_dir=None):
    root = Path(root).resolve(strict=True)
    validate_config(config)
    if output_dir is not None:
        validate_output(root, output_dir)
    missing = [p for p in config['required_files'] if not project_file(root, p).is_file()]
    splits = split_metadata(root, config['split_metadata']) if config.get('split_metadata') and not missing else None
    failed = bool(missing or (splits and splits['overlaps']))
    return dict(status='NEEDS ATTENTION' if failed else 'PARTIAL PASS', task=config['task'],
                metrics=config['metrics'], missing=missing, splits=splits, read_only=True,
                output_created=False, training_supported=False,
                limitation='Mechanical existence/group checks only; raw schema, fit scope, metric definitions and provenance require source review.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--config', required=True, help='Audit JSON, not the experiment YAML')
    parser.add_argument('--output-dir', help='Validate only; never create')
    args = parser.parse_args()
    try:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            config_path = project_file(args.project_root, args.config)
        report = check_project(args.project_root, json.loads(config_path.read_text(encoding='utf-8-sig')), args.output_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report = dict(status='NEEDS ATTENTION', error=str(exc), read_only=True)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report['status'] == 'NEEDS ATTENTION' else 0


if __name__ == '__main__':
    raise SystemExit(main())
