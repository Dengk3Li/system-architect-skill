import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/architecture-workspace/scripts'
sys.path.insert(0, str(SCRIPTS))
try:
    import workspace_model as model
    import workspace_scan as scan
    import workspace
except ImportError:
    model = scan = workspace = None


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(workspace, 'workspace capability is not implemented')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'data').mkdir()
        (self.root / 'data/input.csv').write_text('a,b\n1,2\n')
        self.mapping = {'schema': 'system-architect.workspace-map/v1',
                        'project': {'id': 'test', 'title': 'Test', 'synthetic': True},
                        'modules': [{'id': 'data', 'title': 'Data', 'purpose': 'Inputs',
                                     'paths': ['data/**'], 'evidence': 'User-declared map'}],
                        'relationships': [],
                        'nature_rules': [{'pattern': 'data/**', 'nature': 'Source data'}],
                        'exclude': []}

    def snapshot(self, **kw):
        return scan.scan(self.root, self.mapping, label='Test', **kw)

    def catalog(self, snap=None):
        return {'schema': model.SCHEMA, 'project': self.mapping['project'],
                'snapshots': [snap or self.snapshot()], 'runs': []}

    def record(self, snap):
        return {'schema': 'system-architect.run/v1', 'id': 'run-1', 'title': 'Trial',
                'status': 'completed', 'started_at': '2026-09-08T01:00:00Z',
                'ended_at': '2026-09-08T01:01:00Z', 'command': 'python train.py',
                'inputs': [{'snapshot_id': snap['id'], 'path': 'data/input.csv'}],
                'outputs': [], 'config': [], 'metrics': {'score': 0.8},
                'conclusion': 'Illustrative result', 'evidence': 'User-supplied run receipt'}

    def test_content_identity_is_full_hash_and_no_absolute_path_or_content(self):
        s = self.snapshot()
        f = s['files'][0]
        self.assertEqual(f['content_id'], 'sha256:' + model.sha256_bytes(b'a,b\n1,2\n'))
        self.assertEqual(f['hash_status'], 'full')
        self.assertEqual(f['module_id'], 'data')
        self.assertEqual(f['nature'], 'Source data')
        self.assertEqual(s['summary']['logical_bytes'], 8)
        self.assertNotIn(str(self.root), json.dumps(s))
        self.assertNotIn('a,b', json.dumps(s))

    def test_unknown_hash_stays_unknown_even_if_size_and_time_equal(self):
        s = self.snapshot(hash_max_bytes=1)
        self.assertIsNone(s['files'][0]['content_id'])
        self.assertEqual(s['files'][0]['hash_status'], 'size_limit')
        self.assertEqual(model.compare_snapshots(s, s)[0]['change'], 'unknown')

    def test_snapshots_preserve_overwritten_input_and_diff(self):
        before = self.snapshot()
        (self.root / 'data/input.csv').write_text('a,b\n2,3\n')
        after = self.snapshot()
        self.assertNotEqual(before['files'][0]['content_id'], after['files'][0]['content_id'])
        self.assertEqual(model.compare_snapshots(before, after)[0]['change'], 'modified')
        cat = self.catalog(before)
        cat['snapshots'].append(after)
        result = model.add_run(cat, self.record(before))
        self.assertEqual(result['runs'][0]['inputs'][0]['content_id'], before['files'][0]['content_id'])

    def test_removed_and_same_content_at_new_path_are_not_assumed_rename(self):
        before = self.snapshot()
        (self.root / 'data/input.csv').rename(self.root / 'data/renamed.csv')
        delta = model.compare_snapshots(before, self.snapshot())
        self.assertEqual({x['change'] for x in delta}, {'added', 'removed'})

    def test_run_records_are_independent_of_file_changes_and_immutable(self):
        s = self.snapshot()
        cat = model.add_run(self.catalog(s), self.record(s))
        with self.assertRaises(ValueError): model.add_run(cat, self.record(s))
        second = self.record(s); second['id'] = 'run-2'
        self.assertEqual(len(model.add_run(cat, second)['runs']), 2)

    def test_dangling_run_reference_and_forged_content_are_rejected(self):
        s = self.snapshot(); r = self.record(s)
        r['inputs'][0]['path'] = 'missing.csv'
        with self.assertRaises(ValueError): model.add_run(self.catalog(s), r)
        r = self.record(s); r['inputs'][0]['content_id'] = 'sha256:' + '0'*64
        with self.assertRaises(ValueError): model.add_run(self.catalog(s), r)

    def test_tampered_snapshot_is_rejected(self):
        cat = self.catalog(); cat['snapshots'][0]['files'][0]['size_bytes'] = 999
        with self.assertRaises(ValueError): model.validate_catalog(cat)

    def test_duplicate_or_escaping_map_paths_are_rejected(self):
        for pattern in ['/private/**', '../data/**', 'data/../secret/**']:
            bad = copy.deepcopy(self.mapping); bad['modules'][0]['paths'] = [pattern]
            with self.assertRaises(ValueError): scan.scan(self.root, bad)
        bad = copy.deepcopy(self.mapping)
        bad['modules'].append(dict(bad['modules'][0], id='other'))
        with self.assertRaises(ValueError): scan.scan(self.root, bad)

    def test_symlink_hidden_and_sensitive_names_are_excluded(self):
        (self.root / 'alias').symlink_to(self.root / 'data', target_is_directory=True)
        (self.root / 'data/link').symlink_to(self.root / 'data/input.csv')
        (self.root / '.env').write_text('TOKEN=secret')
        (self.root / 'credentials.json').write_text('secret')
        s = self.snapshot()
        self.assertEqual([f['path'] for f in s['files']], ['data/input.csv'])
        self.assertGreaterEqual(len(s['skipped']), 4)

    def test_hardlinks_count_logical_bytes_twice_and_allocated_once(self):
        os.link(self.root / 'data/input.csv', self.root / 'data/copy.csv')
        s = self.snapshot()
        self.assertEqual(s['summary']['logical_bytes'], 16)
        self.assertEqual(s['summary']['allocated_bytes'], s['files'][0]['allocated_bytes'])
        self.assertEqual(len({f['storage_id'] for f in s['files']}), 1)

    def test_limit_marks_scan_partial(self):
        (self.root / 'data/second.csv').write_text('other')
        s = self.snapshot(max_files=1)
        self.assertFalse(s['complete'])
        self.assertEqual(len(s['files']), 1)

    def test_cli_catalog_must_be_outside_scanned_root(self):
        with self.assertRaises(ValueError):
            workspace.scan_to_catalog(self.root, self.root/'catalog.json', self.mapping)
        self.assertFalse((self.root/'catalog.json').exists())

    def test_scan_and_store_keeps_prior_snapshots_and_rejects_wrong_project(self):
        path = self.base/'catalog.json'
        workspace.scan_to_catalog(self.root, path, self.mapping)
        workspace.scan_to_catalog(self.root, path, self.mapping)
        self.assertEqual(len(json.loads(path.read_text())['snapshots']), 2)
        bad = copy.deepcopy(self.mapping); bad['project']['id'] = 'other'
        with self.assertRaises(ValueError): workspace.scan_to_catalog(self.root, path, bad)

    def test_render_escapes_script_terminators(self):
        from workspace_render import render_html
        cat = self.catalog(); cat['project']['title'] = '</script><script>alert(1)</script>'
        result = render_html(cat)
        self.assertNotIn('</script><script>alert(1)', result)
        self.assertIn('Content-Security-Policy', result)

    def test_same_project_id_cannot_mix_two_root_directories(self):
        path=self.base/'catalog.json'
        workspace.scan_to_catalog(self.root,path,self.mapping)
        previous=path.read_bytes()
        other=self.base/'other';other.mkdir()
        with self.assertRaises(ValueError): workspace.scan_to_catalog(other,path,self.mapping)
        self.assertEqual(path.read_bytes(),previous)

    def test_excluded_files_are_not_reported_as_deleted(self):
        before=self.snapshot()
        self.mapping['exclude']=['data/**']
        after=self.snapshot()
        self.assertEqual(model.compare_snapshots(before,after)[0]['change'],'unobserved_after')

    def test_file_mutation_during_hash_discards_content_identity(self):
        fd=os.open(self.root/'data',os.O_RDONLY|os.O_DIRECTORY)
        self.addCleanup(os.close,fd)
        original=os.fstat;calls=0
        def racing_fstat(filefd):
            nonlocal calls
            calls+=1
            if calls==2:(self.root/'data/input.csv').write_text('changed after read')
            return original(filefd)
        with patch('workspace_scan.os.fstat',side_effect=racing_fstat):
            result=scan.observe('input.csv',fd,'data/input.csv',self.mapping,1024,'race')
        self.assertEqual(result['hash_status'],'changed')
        self.assertIsNone(result['content_id'])

    def test_unreadable_content_keeps_metadata_and_unknown_identity(self):
        fd=os.open(self.root/'data',os.O_RDONLY|os.O_DIRECTORY)
        self.addCleanup(os.close,fd)
        with patch('workspace_scan.os.open',side_effect=PermissionError):
            result=scan.observe('input.csv',fd,'data/input.csv',self.mapping,1024,'denied')
        self.assertEqual(result['hash_status'],'unreadable')
        self.assertEqual(result['size_bytes'],8)

    def test_scan_does_not_modify_existing_file_bytes_or_write_sidecars(self):
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.snapshot()
        after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_interrupted_atomic_replace_preserves_previous_catalog(self):
        path=self.base/'catalog.json'
        workspace.scan_to_catalog(self.root,path,self.mapping)
        original=path.read_bytes()
        with patch('workspace.os.replace',side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError): workspace.scan_to_catalog(self.root,path,self.mapping)
        self.assertEqual(path.read_bytes(),original)
        self.assertFalse(list(self.base.glob('.workspace-*.json')))

    def test_catalog_lock_rejects_second_writer(self):
        path=self.base/'catalog.json'
        with workspace.catalog_lock(path):
            with self.assertRaises(ValueError):
                with workspace.catalog_lock(path): pass

    def test_lock_symlink_and_catalog_symlink_are_rejected(self):
        path=self.base/'catalog.json'
        path.with_name('catalog.json.lock').symlink_to(self.root/'data/input.csv')
        with self.assertRaises(OSError): workspace.scan_to_catalog(self.root,path,self.mapping)
        alias=self.base/'alias.json';alias.symlink_to(self.root/'data/input.csv')
        with self.assertRaises(ValueError): workspace.scan_to_catalog(self.root,alias,self.mapping)
        self.assertEqual((self.root/'data/input.csv').read_bytes(),b'a,b\n1,2\n')

    def test_malformed_snapshot_policy_and_nan_metric_rejected(self):
        s=self.snapshot();s.pop('id');s['policy']={};s=model.seal_snapshot(s)
        with self.assertRaises(ValueError):model.validate_catalog(self.catalog(s))
        s=self.snapshot();r=self.record(s);r['metrics']['score']=float('nan')
        with self.assertRaises(ValueError):model.add_run(self.catalog(s),r)
        r['metrics']['score']=10**500
        with self.assertRaises(ValueError):model.add_run(self.catalog(s),r)

    def test_map_derivation_reuses_stable_module_and_interface_ids(self):
        raw={'schema_version':'system-architect.module-boundaries/v1',
             'modules':[{'module_id':'data','purpose':'Inputs','owned_paths':['data/**'],'consumes':[]},
                        {'module_id':'model','purpose':'Predict','owned_paths':['src/**'],'consumes':['data.v1']}],
             'interfaces':[{'interface_id':'data.v1','owner':'data'}]}
        result=model.map_from_boundaries(raw,self.mapping['project'],'explicit manifest')
        self.assertEqual(result['modules'][0]['paths'],['data/**'])
        self.assertEqual(result['relationships'][0]['source'],'data')
        self.assertEqual(result['relationships'][0]['target'],'model')

    def test_run_status_and_time_invariants(self):
        s=self.snapshot();r=self.record(s);r['status']='scientifically-verified'
        with self.assertRaises(ValueError):model.add_run(self.catalog(s),r)
        r=self.record(s);r['ended_at']='2026-09-08T00:00:00Z'
        with self.assertRaises(ValueError):model.add_run(self.catalog(s),r)

    def test_empty_catalog_renders_and_invalid_catalog_fails(self):
        from workspace_render import render_html
        cat=self.catalog();cat['snapshots']=[]
        self.assertIn('尚无文件快照',render_html(cat))
        cat['snapshots']=[{'id':'bad'}]
        with self.assertRaises(ValueError):render_html(cat)

    def test_example_is_reproducible_and_historical_refs_resolve(self):
        path=Path(__file__).resolve().parents[1]/'examples/research-workspace/generate.py'
        spec=importlib.util.spec_from_file_location('workspace_example',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        a=module.build();b=module.build()
        self.assertEqual(a,b)
        self.assertEqual(len(a['snapshots']),4)
        self.assertEqual(a['runs'][-1]['outputs'],[])
        self.assertNotEqual(a['runs'][0]['config'][0]['content_id'],a['runs'][1]['config'][0]['content_id'])

    def test_generated_script_is_one_complete_executable_element(self):
        from html.parser import HTMLParser
        from workspace_render import render_html
        class Reader(HTMLParser):
            def __init__(self):super().__init__();self.scripts=[];self.current=None
            def handle_starttag(self,t,a):
                if t=='script':self.current=dict(a);self.current['text']='';self.scripts.append(self.current)
            def handle_data(self,d):
                if self.current is not None:self.current['text']+=d
            def handle_endtag(self,t):
                if t=='script':self.current=None
        reader=Reader();reader.feed(render_html(self.catalog()))
        executable=[s for s in reader.scripts if s.get('type')!='application/json']
        self.assertEqual(len(executable),1)
        self.assertTrue(executable[0]['text'].rstrip().endswith('})();'))


if __name__ == '__main__': unittest.main()
