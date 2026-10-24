"""Strict, read-only registry validation shared by verification and CSV export."""
import hashlib
from pathlib import Path, PureWindowsPath
import re

EXPECTED_ARTIFACTS = 89


def protected_path(root, relative):
    root = Path(root).resolve(strict=True)
    clean = str(relative).replace('\\', '/')
    parts = clean.split('/')
    if Path(clean).is_absolute() or PureWindowsPath(clean).drive or any(p in ('', '.', '..') for p in parts):
        raise ValueError('Invalid frozen relative path')
    path = root
    for part in parts:
        path /= part
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Linked frozen paths forbidden')
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise ValueError(f'Missing or escaped frozen file: {relative}')
    return path


def load_registry(root, expected_count=EXPECTED_ARTIFACTS):
    manifest = protected_path(root, 'results/frozen_artifacts_sha256.md')
    pairs = {}
    canonical = set()
    for line in manifest.read_text(encoding='utf-8-sig').splitlines():
        if not line.lstrip().startswith('|'):
            continue
        cells = [c.strip().strip('`') for c in line.strip().strip('|').split('|')]
        if len(cells) == 2 and (cells[0] == '相对路径' or all(set(c) <= set('-: ') for c in cells)):
            continue
        if len(cells) != 2 or not re.fullmatch(r'[0-9a-fA-F]{64}', cells[1]):
            raise ValueError('Malformed frozen registry row or SHA256')
        relative, digest = cells
        path = protected_path(root, relative)
        identity = path.as_posix().casefold()
        if identity in canonical:
            raise ValueError('Duplicate frozen path')
        canonical.add(identity)
        pairs[relative.replace('\\', '/')] = digest.lower()
    if len(pairs) != expected_count:
        raise ValueError(f'Expected {expected_count} frozen files, got {len(pairs)}')
    return pairs


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_registry(root):
    pairs = load_registry(root)
    changed = [p for p,h in pairs.items() if file_sha256(protected_path(root,p)) != h]
    if changed:
        raise ValueError('Frozen SHA256 mismatch: '+', '.join(changed))
    return pairs
