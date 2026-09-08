"""Read only observations of one local tree; POSIX directory handles avoid symlink escape."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import fnmatch
import hashlib
import os
from pathlib import Path
import stat

from workspace_model import classify, digest, relative, require, seal_snapshot, summarize, validate_map

EXCLUDED_DIRS = {'node_modules', '__pycache__', 'venv', 'vendor'}
SENSITIVE_NAMES = {'credentials.json', 'credentials', 'id_rsa', 'id_ed25519', 'secrets.json', 'secrets.yaml'}


def excluded(path, mapping):
    parts = path.split('/')
    return (any(p.startswith('.') or p in EXCLUDED_DIRS for p in parts)
            or parts[-1].lower() in SENSITIVE_NAMES
            or parts[-1].lower().endswith(('.pem', '.key', '.p12', '.pfx'))
            or any(fnmatch.fnmatchcase(path, p) for p in mapping['exclude']))


def signature(s):
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def observe(name, dirfd, path, mapping, hash_max_bytes, nonce):
    before = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode): return None
    owner, nature = classify(path, mapping)
    record = {'path': path, 'size_bytes': before.st_size,
              'allocated_bytes': before.st_blocks * 512 if hasattr(before, 'st_blocks') else None,
              'mtime_ms': max(0, before.st_mtime_ns // 1000000),
              'storage_id': digest([nonce, before.st_dev, before.st_ino]),
              'format': Path(path).suffix.lower() or '(none)', 'format_source': 'extension',
              'module_id': owner, 'nature': nature, 'content_id': None,
              'hash_status': 'disabled' if hash_max_bytes == 0 else 'size_limit'}
    if hash_max_bytes == 0 or before.st_size > hash_max_bytes: return record
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dirfd)
        with os.fdopen(fd, 'rb') as source:
            start = os.fstat(source.fileno())
            if not stat.S_ISREG(start.st_mode) or signature(before) != signature(start):
                record['hash_status'] = 'changed'; return record
            h = hashlib.sha256()
            count = 0
            while True:
                data = source.read(min(1024 * 1024, hash_max_bytes - count + 1))
                if not data: break
                count += len(data)
                if count > hash_max_bytes:
                    record['hash_status'] = 'changed'; return record
                h.update(data)
            end = os.fstat(source.fileno())
            current = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            if count != before.st_size or signature(before) != signature(end) or signature(before) != signature(current):
                record['hash_status'] = 'changed'
            else:
                record.update(content_id='sha256:' + h.hexdigest(), hash_status='full')
    except OSError:
        record['hash_status'] = 'unreadable'
    return record


def scan(root, mapping, label='Snapshot', hash_max_bytes=16 * 1024 * 1024, max_files=100000):
    validate_map(mapping)
    require(os.name == 'posix' and hasattr(os, 'O_NOFOLLOW'), 'scanner v1 requires macOS or Linux')
    require(type(hash_max_bytes) is int and hash_max_bytes >= 0, 'hash budget must be nonnegative')
    require(type(max_files) is int and max_files > 0, 'max_files must be positive')
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'scan root must be an existing real directory')
    captured = datetime.now(timezone.utc).isoformat()
    nonce = captured
    files, skipped = [], []
    complete = True

    def error(exc):
        nonlocal complete
        complete = False
        # Error text can contain absolute paths: record only an errno.
        skipped.append({'path': '(directory)', 'reason': f'read_error_{exc.errno}'})

    with _directory(root) as rootfd:
        root_stat = os.fstat(rootfd)
        source_key = digest([str(root.resolve()), root_stat.st_dev, root_stat.st_ino])
        for directory, dirs, names, dirfd in os.fwalk('.', topdown=True, onerror=error, follow_symlinks=False, dir_fd=rootfd):
            prefix = '' if directory == '.' else directory.removeprefix('./') + '/'
            keep = []
            for name in sorted(dirs):
                path = prefix + name
                if excluded(path, mapping): skipped.append({'path': path, 'reason': 'excluded'}); continue
                try:
                    relative(path)
                    info = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
                    if stat.S_ISLNK(info.st_mode): skipped.append({'path': path, 'reason': 'symlink'}); continue
                    keep.append(name)
                except (OSError, ValueError):
                    complete = False; skipped.append({'path': '(directory)', 'reason': 'unreadable_or_unsupported'})
            dirs[:] = keep
            for name in sorted(names):
                path = prefix + name
                if excluded(path, mapping): skipped.append({'path': path, 'reason': 'excluded'}); continue
                try: relative(path)
                except ValueError:
                    complete = False; skipped.append({'path': '(file)', 'reason': 'unsupported_path'}); continue
                if len(files) >= max_files:
                    complete = False; skipped.append({'path': '(remaining)', 'reason': 'file_limit'}); break
                try:
                    record = observe(name, dirfd, path, mapping, hash_max_bytes, nonce)
                    if record is None: skipped.append({'path': path, 'reason': 'symlink_or_special'}); continue
                    if record['hash_status'] in ('changed', 'unreadable'): complete = False
                    files.append(record)
                except OSError as exc:
                    complete = False; skipped.append({'path': path, 'reason': f'read_error_{exc.errno}'})
            if len(files) >= max_files and not complete: break
    files.sort(key=lambda f: f['path'])
    return seal_snapshot({'label': label, 'captured_at': captured, 'source_key': source_key, 'map': copy.deepcopy(mapping),
                          'complete': complete, 'files': files, 'summary': summarize(files), 'skipped': skipped,
                          'policy': {'hash_max_bytes': hash_max_bytes, 'max_files': max_files,
                                     'hidden': 'excluded', 'symlinks': 'excluded', 'atomic': False}})


class _directory:
    def __init__(self, root): self.root = root
    def __enter__(self):
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        return self.fd
    def __exit__(self, *args): os.close(self.fd)
