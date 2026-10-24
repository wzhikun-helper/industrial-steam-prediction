"""Offline, read-only SHA256 verification; no private raw files or model loading."""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re


def project_file(root, relative):
    root = Path(root).resolve(strict=True)
    if not isinstance(relative, str) or not relative:
        raise ValueError('Expected nonempty project-relative path')
    clean = relative.replace('\\', '/')
    parts = clean.split('/')
    if Path(clean).is_absolute() or PureWindowsPath(clean).drive or any(p in ('', '.', '..') for p in parts):
        raise ValueError('Absolute/traversal paths forbidden')
    lowered = [p.casefold() for p in parts]
    if lowered[0] in ('.git', 'private') or 'private' in lowered or (lowered[0] == 'data' and ('raw' in lowered or len(parts) == 1)):
        raise ValueError('Private/raw data and Git internals are outside audit scope')
    current = root
    for part in parts:
        current /= part
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('Linked/junction paths forbidden')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Path escapes project')
    return current


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def manifest_pairs(root, relative, key=None):
    path = project_file(root, relative)
    text = path.read_text(encoding='utf-8-sig')
    if path.suffix.lower() == '.json':
        pairs = json.loads(text)
        if key is not None:
            pairs = pairs[key]
        if not isinstance(pairs, dict):
            raise ValueError('Manifest must be a path-to-SHA256 mapping')
        pairs = list(pairs.items())
    else:
        if key is not None:
            raise ValueError('JSON key only applies to JSON manifests')
        pairs = []
        for line in text.splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = [s.strip().strip('`') for s in line.strip().strip('|').split('|')]
            if len(cells) >= 2 and re.fullmatch(r'[a-fA-F0-9]{64}', cells[1]):
                pairs.append((cells[0], cells[1]))
            elif len(cells) >= 2 and ('/' in cells[0] or '\\' in cells[0]):
                raise ValueError('Malformed manifest hash row')
    if not pairs or len({p for p, _ in pairs}) != len(pairs):
        raise ValueError('Empty or duplicate-path manifest')
    for relative, digest in pairs:
        if not isinstance(digest, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', digest):
            raise ValueError('Invalid SHA256')
        project_file(root, relative)
    return pairs


def check_hashes(root, manifest, key=None):
    pairs = manifest_pairs(root, manifest, key)
    missing, changed = [], []
    for relative, expected in pairs:
        path = project_file(root, relative)
        if not path.is_file():
            missing.append(relative)
        elif sha256(path) != expected.lower():
            changed.append(relative)
    return dict(status='NEEDS ATTENTION' if missing or changed else 'PASS',
                checked=len(pairs), matched=len(pairs)-len(missing)-len(changed),
                missing=missing, changed=changed, read_only=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--json-key')
    args = parser.parse_args()
    try:
        report = check_hashes(args.project_root, args.manifest, args.json_key)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        report = dict(status='NEEDS ATTENTION', error=str(exc), read_only=True)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
