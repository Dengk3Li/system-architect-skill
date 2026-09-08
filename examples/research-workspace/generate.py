#!/usr/bin/env python3
"""Generate a fictional research catalog by measuring temporary synthetic files.

Only this disposable fixture is mutated. No user's project is scanned or modified.
Capture labels/dates and allocation values are normalized for a portable example;
file sizes and full SHA-256 identities always come from the scanner.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'skills/architecture-workspace/scripts'))
from workspace_model import SCHEMA, add_run, digest, seal_snapshot, summarize
from workspace_scan import scan
from workspace_render import render_html

HERE = Path(__file__).parent
MAPPING = {
    'schema': 'system-architect.workspace-map/v1',
    'project': {'id': 'river-temperature-study', 'title': '河流温度预测实验', 'synthetic': True},
    'modules': [
        {'id': 'data', 'title': '观测数据', 'purpose': '整理站点观测与特征', 'paths': ['data/**'], 'evidence': '合成项目的显式职责映射'},
        {'id': 'model', 'title': '预测模型', 'purpose': '比较特征与训练配置', 'paths': ['src/**','config/**'], 'evidence': '合成项目的显式职责映射'},
        {'id': 'results', 'title': '实验成果', 'purpose': '保存预测、评估与结论', 'paths': ['results/**','notes/**'], 'evidence': '合成项目的显式职责映射'}],
    'relationships': [
        {'id':'r1','source':'data','target':'model','label':'提供训练输入','evidence':'合成项目声明'},
        {'id':'r2','source':'model','target':'results','label':'生成预测与评估','evidence':'合成项目声明'}],
    'nature_rules': [
        {'pattern':'data/raw/**','nature':'原始观测'}, {'pattern':'data/features/**','nature':'特征数据'},
        {'pattern':'config/**','nature':'实验配置'}, {'pattern':'src/**','nature':'模型代码'},
        {'pattern':'results/**','nature':'预测产物'}, {'pattern':'notes/**','nature':'研究结论'}],
    'exclude': []}


def build():
    cat={'schema':SCHEMA,'project':MAPPING['project'],'snapshots':[],'runs':[]}
    with tempfile.TemporaryDirectory(prefix='synthetic-workspace-') as temp:
        project=Path(temp)
        def write(path, content):
            p=project/path;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(content if isinstance(content,bytes) else content.encode())
        def snapshot(label,date):
            s=scan(project,MAPPING,label=label,hash_max_bytes=2*1024*1024)
            s.pop('id');s['captured_at']=date
            s['source_key']=digest(['synthetic-river-project'])
            s['synthetic_normalization']='Example dates and allocation normalized; logical sizes and hashes measured.'
            for f in s['files']:
                f['mtime_ms']=1788825600000
                f['allocated_bytes']=((f['size_bytes']+4095)//4096)*4096
                f['storage_id']=digest(['synthetic-storage',f['path']])
            s['summary']=summarize(s['files'])
            s=seal_snapshot(s);cat['snapshots'].append(s);return s
        def ref(s,path):return {'snapshot_id':s['id'],'path':path}
        def record(id,title,before,after,outputs,mae,conclusion,status='completed'):
            return {'schema':'system-architect.run/v1','id':id,'title':title,'status':status,
                'started_at':'2026-09-08T02:00:00Z' if id=='run-baseline' else '2026-09-08T03:00:00Z',
                'ended_at':'2026-09-08T02:05:00Z' if id=='run-baseline' else '2026-09-08T03:05:00Z',
                'inputs':[ref(before,'data/features/window.csv'),ref(before,'src/predict.py')],
                'config':[ref(before,'config/model.json')],
                'outputs':[ref(after,p) for p in outputs],
                'command':'python src/predict.py --config config/model.json',
                'metrics':{'MAE (°C)':mae} if mae is not None else {},
                'conclusion':conclusion,'evidence':'合成实验记录，指标仅供交互示例，不构成实际研究结果'}
        write('data/raw/observations.csv','station,temp\n'+('R01,18.2\n'*48000))
        write('data/features/window.csv','temp,lag\n'+('18.2,17.9\n'*24000))
        write('src/predict.py','# Synthetic example; this file is not executed.\n')
        write('config/model.json','{"window": 12, "seed": 42}\n')
        write('notes/question.md','# 河流温度预测\n比较历史窗口对温度预测的影响。\n')
        s0=snapshot('准备 · 输入与配置','2026-09-08T01:55:00Z')
        write('results/baseline/predictions.csv','observed,predicted\n'+('18.2,17.8\n'*16000))
        write('results/baseline/metrics.json','{"mae": 0.84, "unit": "C", "synthetic": true}\n')
        write('notes/baseline.md','# 基线\n12 步窗口，合成 MAE 0.84°C。\n')
        s1=snapshot('基线 · 12 步窗口','2026-09-08T02:06:00Z')
        cat=add_run(cat,record('run-baseline','基线 · 12 步窗口',s0,s1,['results/baseline/predictions.csv','results/baseline/metrics.json','notes/baseline.md'],0.84,'12 步窗口作为比较基线。样例 MAE 为 0.84°C。'))
        write('config/model.json','{"window": 24, "seed": 42}\n')
        write('data/features/window.csv','temp,lag\n'+('18.2,17.6\n'*32000))
        s2=snapshot('新配置 · 24 步窗口','2026-09-08T02:55:00Z')
        write('results/window-24/predictions.csv','observed,predicted\n'+('18.2,18.0\n'*22000))
        write('results/window-24/metrics.json','{"mae": 0.71, "unit": "C", "synthetic": true}\n')
        write('notes/window-24.md','# 24 步窗口\n合成 MAE 0.71°C，尚未进行跨站点验证。\n')
        s3=snapshot('比较 · 两组预测结果','2026-09-08T03:06:00Z')
        cat=add_run(cat,record('run-window-24','对照 · 24 步窗口',s2,s3,['results/window-24/predictions.csv','results/window-24/metrics.json','notes/window-24.md'],0.71,'样例 MAE 从 0.84°C 降到 0.71°C。输入特征与窗口配置均有变化，不能仅凭这两次记录认定改善原因。跨站点验证尚未完成。'))
        failed=record('run-aborted','重试 · 无新产物',s2,s3,[],None,'模拟一次取消的尝试，保留输入与配置，没有生成新产物。','cancelled')
        failed['started_at']='2026-09-08T03:10:00Z';failed['ended_at']='2026-09-08T03:11:00Z'
        cat=add_run(cat,failed)
    return cat


def main():
    cat=build();HERE.mkdir(parents=True,exist_ok=True)
    (HERE/'workspace-map.json').write_text(json.dumps(MAPPING,ensure_ascii=False,indent=2)+'\n')
    (HERE/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
    html=render_html(cat)
    # The example starts at its most useful artifact and completed comparison.
    initial={'file':'results/window-24/predictions.csv','run':'run-window-24','before':cat['snapshots'][1]['id']}
    html=html.replace('<script type="application/json" id="initial-state">{}</script>', '<script type="application/json" id="initial-state">'+json.dumps(initial)+'</script>')
    (HERE/'index.html').write_text(html)
    print('Generated synthetic workspace: 4 snapshots, 3 runs, measured sizes and full hashes.')


if __name__=='__main__':main()
