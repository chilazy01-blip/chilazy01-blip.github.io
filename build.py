#!/usr/bin/env python3
"""Build only this report directory; project inputs are read-only."""
import argparse
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'public'
DATA = json.loads((HERE / 'content/report.json').read_text())
e = lambda value: html.escape(str(value), quote=True)

def badge(kind, label):
    return f'<span class="badge {e(kind)}">{e(label)}</span>'

def evidence(ids):
    return '<span class="citations">' + ' '.join(
        f'<a href="#evidence-{e(i)}" title="查看本地证据摘要">[{e(i)}]</a>' for i in ids.split(',')
    ) + '</span>'

REFS = {r['id']: r for r in DATA['references']}

def refs(ids):
    return ' / '.join(f'<a href="{e(REFS[i]["url"])}" target="_blank" rel="noopener noreferrer">{e(REFS[i]["name"])}</a>' for i in ids.split(','))

def generate():
    metrics = ''.join(f'''<tr><th scope="row">{e(r[0])}</th><td>{e(r[1])}</td>
      <td>{e(r[2])}{evidence(r[6])}</td><td>{badge(r[3],r[4])}<p>{e(r[5])}</p></td></tr>''' for r in DATA['metrics'])
    stages = ''.join(f'''<li class="stage {e(r[4])}"><span class="stage-number">{e(r[0])}</span>
      <h3>{e(r[1])}</h3><p>{e(r[2])}</p>{badge(r[4],r[3])}</li>''' for r in DATA['stages'])
    papers = ''.join(f'''<tr><th scope="row"><a href="{e(r['url'])}" target="_blank" rel="noopener noreferrer">{e(r['name'])} ↗</a></th>
      <td><time>{e(r['date'])}</time><small>{e(r['update'])}</small></td><td><strong>{e(r['focus'])}</strong><p>{e(r['summary'])}</p></td></tr>''' for r in DATA['references'])
    comparisons = ''.join(f'''<tr data-group="{e(r[0])}"><th scope="row"><small>{e(r[0])}</small>{e(r[1])}</th>
      <td>{badge(r[2],{'limited':'有限成果','active':'正在接通','gap':'仍有缺口'}[r[2]])}<p>{e(r[3])}</p></td>
      <td><span class="ref-list">{refs(r[4])}</span><p>{e(r[5])}</p></td><td>{e(r[6])}</td></tr>''' for r in DATA['comparisons'])
    plans = ''.join(f'''<article class="plan-card"><div class="eyebrow">0{i+1} / {e(r['tag'])}</div><h3>{e(r['type'])}</h3>
      <p class="plain">{e(r['plain'])}</p><ol>{''.join(f'<li><h4>{e(a)}</h4><p>{e(b)}</p></li>' for a,b in r['items'])}</ol>
      <p class="exit-rule">{e(r['exit'])}</p></article>''' for i,r in enumerate(DATA['plans']))
    evidence_items = ''.join(f'''<article id="evidence-{e(r['id'])}" class="evidence-item"><span class="eyebrow">{e(r['id'])} · {e(r['date'])}</span>
      <h4>{e(r['title'])}</h4><p>{e(r['summary'])}</p><details><summary>原始记录标识</summary>{''.join(f'<code>{e(f)}</code>' for f in r['files'])}</details></article>''' for r in DATA['evidence'])
    timeline = [('000_pregrasp','接近前',0),('040_grasp','抓取',2),('080_close','闭合',4),('100_lift','抬升',5),('140_transfer','转移',7),('200_release','释放',10),('240_open','张开',12),('260_retreat','撤离',13),('300_settle','稳定',15),('350_settle','末态',17.5)]
    frames = ''.join(f'''<figure><a href="assets/temporal-{name}.png" target="_blank" rel="noopener"><img src="assets/temporal-{name}.png" alt="O01 原始阶段帧：{label}，{sec:g} 秒" loading="lazy" width="320" height="240"></a><figcaption><strong>{label}</strong><span>{sec:g} s</span></figcaption></figure>''' for name,label,sec in timeline)
    template = (HERE/'content/page.html').read_text()
    replacements = {'metrics': metrics,'stages': stages,'papers': papers,'comparisons': comparisons,'plans': plans,'evidence': evidence_items,'frames': frames}
    replacements.update({k:e(DATA[k]) for k in ['date','version','title','goal','summary']})
    for key,value in replacements.items():
        template=template.replace('{{'+key+'}}',value)
    if re.search(r'\{\{[^}]+\}\}',template):
        raise ValueError('Unresolved template token')
    (OUT/'index.html').write_text(template)
    (OUT/'evidence/snapshot.json').write_text(json.dumps(DATA, ensure_ascii=False, indent=2)+'\n')
    (OUT/'.nojekyll').write_text('')

def prepare_assets():
    base = ROOT/'scene_runs/codex_trellis_v2'
    room = base/'scene_reliability_20260914_v1/living_room/presentation'
    sim = base/'scene_reliability_20260914_v1/simulation/presentation/media'
    temporal = base/'embodied_temporal_dataset_20260924_v1/candidate/previews'
    learned = base/'embodied_release_history_20260921_v1/presentation/success'
    mapping = {'room-rgb.png':room/'overview/rgb.png','room-depth.png':room/'overview/depth_preview.png','room-instance.png':room/'overview/instance_preview.png',
        'room-seating.png':room/'seating/rgb.png','room-table.png':room/'table/rgb.png','room-shelf.png':room/'shelf/rgb.png',
        'learned.mp4':learned/'rollout.mp4','learned-poster.png':learned/'frame_0922.png',
        'production-summary.png':base/'embodied_production_pilot_20260921_v1/presentation/production_summary.png'}
    for name in ('navigate','pick_place','grasp_closeup'):
        mapping[f'{name}.mp4']=sim/f'{name}.mp4'
        mapping[f'{name}-poster.png']=sim/f'{name}_poster.png'
    for p in sorted(temporal.glob('*.png')):
        mapping['temporal-'+p.name]=p
    manifest=[]
    for name,src in mapping.items():
        dst=OUT/'assets'/name
        raw=src.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        # Copy exact original bytes. Never alter experiment assets.
        dst.write_bytes(raw)
        manifest.append({'source':str(src.relative_to(ROOT)),'public_asset':'assets/'+name,'sha256':sha,'bytes':len(raw)})
    for rec in DATA['evidence']:
        for relative in rec['files']:
            src=ROOT/relative
            raw=src.read_bytes()
            manifest.append({'source':relative,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    (HERE/'source_manifest.json').write_text(json.dumps({'captured_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'files':manifest},ensure_ascii=False,indent=2)+'\n')
    public_assets = [{'path':r['public_asset'],'sha256':r['sha256'],'bytes':r['bytes']}
                     for r in manifest if 'public_asset' in r]
    (HERE/'content/assets.json').write_text(json.dumps({'assets':public_assets},ensure_ascii=False,indent=2)+'\n')

def verify_sources():
    manifest=json.loads((HERE/'source_manifest.json').read_text())
    changed=[]
    for rec in manifest['files']:
        sha=hashlib.sha256((ROOT/rec['source']).read_bytes()).hexdigest()
        if sha!=rec['sha256']:
            changed.append(rec['source'])
    print(json.dumps({'checked':len(manifest['files']),'changed_since_snapshot':changed},ensure_ascii=False,indent=2))
    if changed:
        raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--copy-assets',action='store_true',help='Read and copy original report visuals; capture provenance hashes')
    parser.add_argument('--verify-sources',action='store_true')
    args=parser.parse_args()
    if args.verify_sources:
        verify_sources()
    else:
        (OUT/'assets').mkdir(parents=True,exist_ok=True)
        (OUT/'evidence').mkdir(exist_ok=True)
        if args.copy_assets:
            prepare_assets()
        generate()
        print('Built',OUT/'index.html')
