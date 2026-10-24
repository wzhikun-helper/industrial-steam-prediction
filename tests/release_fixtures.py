"""Synthetic-only frozen registry fixtures; never read real artifacts."""
import hashlib


def register(root, relative='results/input.csv'):
    results=root/'results'
    results.mkdir(exist_ok=True)
    paths=[relative]
    for i in range(88):
        p=f'results/synthetic_{i}.bin'
        (root/p).write_bytes(b'synthetic')
        paths.append(p)
    rows=['# Synthetic registry','| 相对路径 | SHA256 |','|---|---|']
    rows.extend(f'| {p} | {hashlib.sha256((root/p).read_bytes()).hexdigest()} |' for p in paths)
    (results/'frozen_artifacts_sha256.md').write_text('\n'.join(rows),encoding='utf-8')
