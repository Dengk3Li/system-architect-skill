"""Versioned, content-checked catalog contracts. No filesystem or model calls."""
from __future__ import annotations

import copy
from datetime import datetime
import fnmatch
import hashlib
import json
import math
from pathlib import PurePosixPath
import re

SCHEMA = 'system-architect.workspace/v1'
MAP_SCHEMA = 'system-architect.workspace-map/v1'
RUN_SCHEMA = 'system-architect.run/v1'
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$')
CONTENT = re.compile(r'^sha256:[0-9a-f]{64}$')
MAX_SAFE_INTEGER = 9007199254740991


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and 0 < len(value) <= 10000, f'{name} must be non-empty text')
    return value


def integer(value, name):
    require(type(value) is int and 0 <= value <= MAX_SAFE_INTEGER, f'{name} must be a nonnegative safe integer')


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest(value):
    return sha256_bytes(canonical(value).encode())


def relative(value, pattern=False):
    text(value, 'relative path')
    require(not value.startswith('/') and '\\' not in value and ':' not in value
            and not any(p in ('', '.', '..') for p in value.split('/'))
            and not any(ord(c) < 32 for c in value), 'path must be a normalized relative POSIX path')
    if not pattern:
        require(not any(c in value for c in '*?[]'), 'literal paths cannot contain glob characters')
    return value


def timestamp(value):
    text(value, 'timestamp')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('timestamp must be ISO 8601') from exc
    require(result.tzinfo is not None, 'timestamp requires a timezone')
    return result


def unique(records, label):
    require(isinstance(records, list), f'{label} must be an array')
    result = {}
    for row in records:
        require(isinstance(row, dict), f'{label} entries must be objects')
        key = row.get('id')
        require(isinstance(key, str) and ID.fullmatch(key), f'invalid {label} id')
        require(key not in result, f'duplicate {label} id: {key}')
        result[key] = row
    return result


def validate_project(project):
    require(isinstance(project, dict), 'project must be an object')
    require(isinstance(project.get('id'), str) and ID.fullmatch(project['id']), 'invalid project id')
    text(project.get('title'), 'project title')
    require(type(project.get('synthetic')) is bool, 'project.synthetic must be explicit')


def validate_map(mapping):
    require(isinstance(mapping, dict) and mapping.get('schema') == MAP_SCHEMA, 'unsupported workspace map')
    validate_project(mapping.get('project'))
    modules = unique(mapping.get('modules'), 'module')
    for m in modules.values():
        for key in ('title', 'purpose', 'evidence'):
            text(m.get(key), f'module {key}')
        require(isinstance(m.get('paths'), list) and m['paths'], 'module paths required')
        for p in m['paths']: relative(p, pattern=True)
    for r in unique(mapping.get('relationships'), 'relationship').values():
        require(r.get('source') in modules and r.get('target') in modules, 'unknown relationship module')
        text(r.get('label'), 'relationship label')
        text(r.get('evidence'), 'relationship evidence')
    require(isinstance(mapping.get('nature_rules'), list), 'nature_rules must be an array')
    for rule in mapping['nature_rules']:
        require(isinstance(rule, dict), 'nature rule must be an object')
        relative(rule.get('pattern'), pattern=True)
        text(rule.get('nature'), 'nature')
    require(isinstance(mapping.get('exclude'), list), 'exclude must be an array')
    for p in mapping['exclude']: relative(p, pattern=True)
    return mapping


def classify(path, mapping):
    owners = [m['id'] for m in mapping['modules'] if any(fnmatch.fnmatchcase(path, p) for p in m['paths'])]
    require(len(owners) <= 1, f'overlapping module ownership: {path}')
    natures = {r['nature'] for r in mapping['nature_rules'] if fnmatch.fnmatchcase(path, r['pattern'])}
    require(len(natures) <= 1, f'conflicting nature rules: {path}')
    return (owners[0] if owners else None, next(iter(natures), None))


def map_from_boundaries(manifest, project, evidence):
    """Project existing declared ownership, without discovering or changing architecture."""
    require(isinstance(manifest, dict) and manifest.get('schema_version') == 'system-architect.module-boundaries/v1', 'unsupported boundary manifest')
    validate_project(project)
    require(isinstance(manifest.get('modules'), list), 'boundary modules required')
    modules = []
    for m in manifest['modules']:
        modules.append({'id': m.get('module_id'), 'title': m.get('title', m.get('module_id')),
                        'purpose': m.get('purpose'), 'paths': m.get('owned_paths'), 'evidence': evidence})
    ids = {m['id'] for m in modules}
    require(isinstance(manifest.get('interfaces'), list), 'boundary interfaces required')
    interfaces = {i.get('interface_id'): i for i in manifest['interfaces']}
    require(len(interfaces) == len(manifest['interfaces']), 'duplicate boundary interface')
    relations = []
    for m in manifest['modules']:
        require(isinstance(m.get('consumes'), list), 'boundary consumes must be an array')
        for contract in m['consumes']:
            require(contract in interfaces and interfaces[contract].get('owner') in ids, 'unknown boundary interface or owner')
            interface = interfaces[contract]
            relations.append({'id': 'edge-' + digest([contract,m['module_id']])[:20],
                              'source': interface['owner'], 'target': m['module_id'],
                              'label': contract, 'evidence': evidence})
    return validate_map({'schema': MAP_SCHEMA, 'project': project, 'modules': modules,
                         'relationships': relations, 'nature_rules': [], 'exclude': []})


def summarize(files):
    storage = {}
    for f in files:
        key = f['storage_id']
        if key not in storage: storage[key] = f['allocated_bytes']
        elif storage[key] != f['allocated_bytes']: storage[key] = None
    allocated = None if any(v is None for v in storage.values()) else sum(storage.values())
    return {'file_count': len(files), 'logical_bytes': sum(f['size_bytes'] for f in files),
            'allocated_bytes': allocated, 'storage_object_count': len(storage),
            'full_hash_count': sum(f['hash_status'] == 'full' for f in files),
            'unclassified_count': sum(f['nature'] is None for f in files)}


def seal_snapshot(snapshot):
    return dict(snapshot, id='s-' + digest(snapshot))


def validate_snapshot(s):
    require(isinstance(s, dict), 'snapshot must be an object')
    require(s.get('id') == 's-' + digest({k: v for k, v in s.items() if k != 'id'}), 'snapshot digest mismatch')
    text(s.get('label'), 'snapshot label'); timestamp(s.get('captured_at'))
    require(isinstance(s.get('source_key'), str) and re.fullmatch(r'[0-9a-f]{64}', s['source_key']), 'snapshot source binding required')
    validate_map(s.get('map'))
    require(type(s.get('complete')) is bool, 'snapshot completeness required')
    policy = s.get('policy')
    require(isinstance(policy, dict), 'scan policy required')
    integer(policy.get('hash_max_bytes'), 'hash_max_bytes')
    integer(policy.get('max_files'), 'max_files')
    require(policy['max_files'] > 0 and policy.get('atomic') is False, 'invalid scan policy')
    require(policy.get('hidden') == 'excluded' and policy.get('symlinks') == 'excluded', 'unsupported traversal policy')
    require(isinstance(s.get('files'), list), 'snapshot files must be an array')
    paths = set()
    for f in s['files']:
        require(isinstance(f, dict), 'file observation must be an object')
        path = relative(f.get('path'))
        require(path not in paths, 'duplicate snapshot path'); paths.add(path)
        for field in ('size_bytes', 'mtime_ms'):
            integer(f.get(field), field)
        if f.get('allocated_bytes') is not None: integer(f['allocated_bytes'], 'allocated_bytes')
        text(f.get('storage_id'), 'storage identity')
        text(f.get('format'), 'format')
        require(f.get('format_source') == 'extension', 'v1 format source is extension')
        require(f.get('hash_status') in ('full', 'size_limit', 'disabled', 'changed', 'unreadable'), 'invalid hash status')
        cid = f.get('content_id')
        require((f['hash_status'] == 'full' and isinstance(cid, str) and CONTENT.fullmatch(cid))
                or (f['hash_status'] != 'full' and cid is None), 'content identity requires a full hash')
        owner, nature = classify(path, s['map'])
        require(f.get('module_id') == owner and f.get('nature') == nature, 'file classification disagrees with snapshot map')
    require(s.get('summary') == summarize(s['files']), 'snapshot totals disagree with files')
    require(isinstance(s.get('skipped'), list), 'scan coverage required')
    for item in s['skipped']:
        require(isinstance(item, dict), 'skipped entry must be an object')
        text(item.get('path'), 'skipped path'); text(item.get('reason'), 'skipped reason')
    return s


def file_index(cat):
    return {(s['id'], f['path']): f for s in cat['snapshots'] for f in s['files']}


def normalize_run(cat, record):
    require(isinstance(record, dict) and record.get('schema') == RUN_SCHEMA, 'unsupported run record')
    unique([record], 'run')
    for key in ('title', 'evidence'):
        text(record.get(key), f'run {key}')
    require(record.get('status') in ('completed', 'failed', 'cancelled'), 'invalid terminal run status')
    require(timestamp(record.get('started_at')) <= timestamp(record.get('ended_at')), 'run ends before it starts')
    for key in ('command', 'conclusion'):
        require(isinstance(record.get(key), str) and len(record[key]) <= 10000, f'invalid {key}')
    metrics = record.get('metrics')
    require(isinstance(metrics, dict), 'run metrics must be an object')
    for k, v in metrics.items():
        text(k, 'metric name')
        require(type(v) in (float, int) and abs(v) <= MAX_SAFE_INTEGER and math.isfinite(v), 'metric must be a finite safe number')
    result = copy.deepcopy(record)
    index = file_index(cat)
    for role in ('inputs', 'config', 'outputs'):
        require(isinstance(record.get(role), list), f'run {role} must be an array')
        refs = set()
        for ref in result[role]:
            require(isinstance(ref, dict), 'run file reference must be an object')
            key = (ref.get('snapshot_id'), relative(ref.get('path')))
            require(isinstance(key[0], str) and key in index, 'run references an unknown file observation')
            require(key not in refs, 'duplicate run file reference'); refs.add(key)
            f = index[key]
            if 'content_id' in ref:
                require(ref['content_id'] == f['content_id'], 'run content identity disagrees with observation')
            ref['content_id'] = f['content_id']
    result.pop('record_digest', None)
    result['record_digest'] = digest(result)
    return result


def validate_catalog(cat):
    require(isinstance(cat, dict) and cat.get('schema') == SCHEMA, 'unsupported workspace catalog')
    validate_project(cat.get('project'))
    snapshots = unique(cat.get('snapshots'), 'snapshot')
    for s in snapshots.values():
        validate_snapshot(s)
        require(s['map']['project']['id'] == cat['project']['id'], 'snapshot belongs to a different project')
    require(len({s['source_key'] for s in snapshots.values()}) <= 1, 'snapshots belong to different source directories')
    for run in unique(cat.get('runs'), 'run').values():
        require(normalize_run(cat, run) == run, 'run digest or content reference mismatch')
    return cat


def add_run(cat, record):
    validate_catalog(cat)
    require(record.get('id') not in {r['id'] for r in cat['runs']}, 'run id already recorded; create a new record')
    result = copy.deepcopy(cat)
    result['runs'].append(normalize_run(cat, record))
    return validate_catalog(result)


def compare_snapshots(before, after):
    a = {f['path']: f for f in before['files']}; b = {f['path']: f for f in after['files']}
    rows = []
    for path in sorted(a.keys() | b.keys()):
        old, new = a.get(path), b.get(path)
        def covered(s):
            return s['complete'] and not any(path == x['path'] or path.startswith(x['path'] + '/') for x in s['skipped'])
        if old is None: change = 'added' if covered(before) else 'unobserved_before'
        elif new is None: change = 'removed' if covered(after) else 'unobserved_after'
        elif old['content_id'] is None or new['content_id'] is None: change = 'unknown'
        elif old['content_id'] != new['content_id']: change = 'modified'
        else: change = 'unchanged'
        rows.append({'path': path, 'change': change, 'before': old, 'after': new})
    return rows
