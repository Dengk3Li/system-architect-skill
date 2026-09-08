#!/usr/bin/env python3
"""Local architecture workspace CLI. Writes metadata only, outside the scanned root."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile

from workspace_model import SCHEMA, add_run, compare_snapshots, map_from_boundaries, require, validate_catalog
from workspace_scan import scan


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'cannot read JSON: {Path(path).name}: {exc.__class__.__name__}') from exc


@contextmanager
def catalog_lock(path):
    # flock survives interruption without stale lease cleanup. The empty lock is permanent.
    import fcntl
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as handle:
        try: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise ValueError('catalog is in use; retry after the current writer finishes') from exc
        yield


def save_catalog(path, cat):
    validate_catalog(cat)
    path = Path(path)
    require(not path.is_symlink(), 'catalog cannot be a symlink')
    fd, tmp = tempfile.mkstemp(prefix='.workspace-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as target:
            json.dump(cat, target, ensure_ascii=True, indent=2, allow_nan=False)
            target.write('\n'); target.flush(); os.fsync(target.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def scan_to_catalog(root, path, mapping, **options):
    root, path = Path(root), Path(path)
    require(not path.resolve().is_relative_to(root.resolve()), 'catalog must be outside the scanned directory')
    require(not path.is_symlink(), 'catalog cannot be a symlink')
    with catalog_lock(path):
        if path.exists():
            cat = validate_catalog(read_json(path))
            require(cat['project'] == mapping['project'], 'catalog belongs to a different project or project declaration')
        else:
            cat = {'schema': SCHEMA, 'project': mapping['project'], 'snapshots': [], 'runs': []}
        s = scan(root, mapping, **options)
        require(not cat['snapshots'] or cat['snapshots'][0]['source_key'] == s['source_key'], 'catalog source directory changed; use a new catalog')
        cat['snapshots'].append(s)
        save_catalog(path, cat)
    return s


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    m = sub.add_parser('map-from-boundaries', help='derive a workspace map from existing module ownership')
    m.add_argument('manifest', type=Path); m.add_argument('--project-id', required=True)
    m.add_argument('--title', required=True); m.add_argument('--output', type=Path, required=True)
    s = sub.add_parser('scan', help='read one directory into a catalog stored elsewhere')
    s.add_argument('root', type=Path); s.add_argument('--map', type=Path, required=True)
    s.add_argument('--catalog', type=Path, required=True); s.add_argument('--label', default='Snapshot')
    s.add_argument('--hash-max-bytes', type=int, default=16*1024*1024); s.add_argument('--max-files', type=int, default=100000)
    r = sub.add_parser('record-run', help='append an explicit run receipt without executing its command')
    r.add_argument('record', type=Path); r.add_argument('--catalog', type=Path, required=True)
    v = sub.add_parser('validate'); v.add_argument('catalog', type=Path)
    r = sub.add_parser('render', help='render a validated catalog to one offline HTML file')
    r.add_argument('catalog', type=Path); r.add_argument('--output', type=Path, required=True)
    d = sub.add_parser('diff'); d.add_argument('catalog', type=Path)
    d.add_argument('--before', required=True); d.add_argument('--after', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'map-from-boundaries':
            mapping = map_from_boundaries(read_json(args.manifest), {'id': args.project_id, 'title': args.title, 'synthetic': False},
                                          f'Module boundary declaration: {args.manifest.name}')
            require(not args.output.exists(), 'map output exists; choose a new path')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as target:
                json.dump(mapping, target, indent=2, ensure_ascii=True); target.write('\n')
            print(f'Created {args.output.name}; add explicit nature rules as needed')
        elif args.command == 'scan':
            result = scan_to_catalog(args.root, args.catalog, read_json(args.map), label=args.label,
                                     hash_max_bytes=args.hash_max_bytes, max_files=args.max_files)
            print(json.dumps({'snapshot_id': result['id'], 'complete': result['complete'], **result['summary']}))
        elif args.command == 'record-run':
            with catalog_lock(args.catalog):
                cat = add_run(read_json(args.catalog), read_json(args.record))
                save_catalog(args.catalog, cat)
            print(f"Recorded {cat['runs'][-1]['id']}")
        elif args.command == 'validate':
            validate_catalog(read_json(args.catalog)); print('Workspace catalog: PASS')
        elif args.command == 'render':
            from workspace_render import render_html
            require(args.output.resolve() != args.catalog.resolve(), 'HTML output must differ from catalog')
            require(not args.output.exists(), 'output already exists; choose a new HTML path')
            result = render_html(read_json(args.catalog))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as target: target.write(result)
            print(f'Created {args.output.name}')
        elif args.command == 'diff':
            cat = validate_catalog(read_json(args.catalog)); snapshots = {s['id']: s for s in cat['snapshots']}
            require(args.before in snapshots and args.after in snapshots, 'unknown snapshot')
            print(json.dumps(compare_snapshots(snapshots[args.before], snapshots[args.after]), ensure_ascii=True, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f'Workspace error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__': sys.exit(main())
