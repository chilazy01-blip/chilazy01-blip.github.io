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

def weekly_replacements(data_key='weekly_update', prefix='weekly'):
    week = DATA[data_key]
    result = {'weekly_' + key: e(week[key]) for key in ('date', 'period', 'title', 'summary')}
    result['weekly_metrics'] = ''.join(
        f'<article><span>{e(row["label"])}</span><strong>{e(row["value"])}</strong><p>{e(row["description"])}</p></article>'
        for row in week['metrics'])
    result['weekly_progress'] = ''.join(
        f'<article class="route-progress-card"><span class="eyebrow">{i + 1:02d} / {e(row["label"])}</span><h4>{e(row["title"])}</h4><p>{e(row["description"])}</p></article>'
        for i, row in enumerate(week['progress']))
    result['weekly_steps'] = ''.join(
        f'<li><span class="route-step-number">{i + 1:02d}</span><div><span class="eyebrow">{e(row["label"])}</span><h4>{e(row["title"])}</h4><p>{e(row["description"])}</p><small>验收：{e(row["gate"])}</small></div></li>'
        for i, row in enumerate(week['steps']))
    result['weekly_evidence'] = ''.join(
        f'<article><h4>{e(row["title"])}</h4><p>{e(row["summary"])}</p><code>{e(row["record"])}</code></article>'
        for row in week['evidence'])
    return {key.replace('weekly_', prefix + '_', 1): value for key, value in result.items()}

def related_work_replacements():
    work = DATA['related_work']
    sources = {row['id']: row for row in work['sources']}

    def source_link(key):
        row = sources[key]
        return f'<a href="{e(row["url"])}" target="_blank" rel="noopener noreferrer">{e(row["label"])} ↗</a>'

    result = {'related_' + key: e(work[key]) for key in (
        'date', 'paper_version', 'title', 'summary', 'overview_takeaway',
        'scene_note', 'decision_summary')}
    result['related_workflow'] = ''.join(
        f'<li><span class="reference-step">{i + 1:02d}</span><h3>{e(row["title"])}</h3><p>{e(row["description"])}</p></li>'
        for i, row in enumerate(work['workflow']))
    result['related_comparisons'] = ''.join(
        f'<tr><th scope="row">{e(row["label"])}</th><td>{e(row["theirs"])}</td><td>{e(row["ours"])}</td></tr>'
        for row in work['comparisons'])
    result['related_lessons'] = ''.join(
        f'<article class="reference-lesson"><span class="eyebrow">{i + 1:02d} / 技术启发</span><h3>{e(row["title"])}</h3>'
        f'<dl><div><dt>他们的设计</dt><dd>{e(row["design"])}</dd></div>'
        f'<div><dt>对我们的启发</dt><dd>{e(row["implication"])}</dd></div>'
        f'<div class="reference-limit"><dt>适用边界</dt><dd>{e(row["boundary"])}</dd></div></dl>'
        f'<p class="reference-citation">{source_link(row["source"])}'
        f'{" · " + source_link("paper") if row["source"] == "export" else ""}</p></article>'
        for i, row in enumerate(work['lessons']))
    result['related_decisions'] = ''.join(
        f'<article class="reference-decision"><div class="reference-card-heading"><span class="eyebrow">{i + 1:02d}</span>'
        f'{badge(row["kind"], row["status"])}</div><h3>{e(row["title"])}</h3><p class="reference-choice">{e(row["decision"])}</p>'
        f'<dl><div><dt>判断依据</dt><dd>{e(row["reason"])}</dd></div>'
        f'<div><dt>后续核对</dt><dd>{e(row["next"])}</dd></div></dl></article>'
        for i, row in enumerate(work['decisions']))
    result['related_backlog'] = ''.join(
        f'<li><span>{e(row["id"])}</span><div><strong>{e(row["title"])}</strong><p>{e(row["description"])}</p></div></li>'
        for row in work['scene_backlog'])
    result['related_sources'] = ''.join(f'<li>{source_link(row["id"])}</li>' for row in work['sources'])
    result['related_project_evidence'] = ''.join(
        f'<article><h4>{e(row["title"])}</h4><p>{e(row["summary"])}</p><small>{e(row["record"])}</small></article>'
        for row in work['project_evidence'])
    return result

def work_resource_links(work_id):
    return '<nav class="work-resources" aria-label="' + e(work_id) + '原始资料">' + ''.join(
        f'<a href="{e(row["url"])}" target="_blank" rel="noopener noreferrer">{e(row["label"])} <span aria-hidden="true">↗</span></a>'
        for row in DATA['work_resources'][work_id]) + '</nav>'

def robosim_replacements():
    work = DATA['robosim_work']
    result = {'rss_' + key: e(work[key]) for key in (
        'date', 'paper_version', 'title', 'summary', 'limits', 'physical_takeaway',
        'candidate_check', 'discussion_status')}
    result['rss_workflow'] = ''.join(
        f'<li><span class="reference-step">{i + 1:02d}</span><h3>{e(row["title"])}</h3><p>{e(row["description"])}</p></li>'
        for i, row in enumerate(work['workflow']))
    result['rss_features'] = ''.join(
        f'<article><h3>{e(row["title"])}</h3><p>{e(row["description"])}</p></article>'
        for row in work['features'])
    result['rss_physical_rows'] = ''.join(
        f'<tr><td>{e(row["base"])}</td><td>{e(row["lesson"])}</td><td>{e(row["choice"])}</td></tr>'
        for row in work['physical_rows'])
    result['rss_physical_steps'] = ''.join(
        f'<article><span class="eyebrow">{i + 1:02d} / 候选顺序</span><h3>{e(row["title"])}</h3><p>{e(row["description"])}</p></article>'
        for i, row in enumerate(work['physical_steps']))
    result['rss_video_choices'] = ''.join(
        f'<article>{badge(row["kind"], row["status"])}<h3>{e(row["title"])}</h3><p>{e(row["description"])}</p></article>'
        for row in work['video_choices'])
    result['rss_pose_targets'] = ''.join(
        f'<li><strong>{e(row["title"])}</strong><p>{e(row["description"])}</p></li>'
        for row in work['pose_targets'])
    result['rss_candidate_flow'] = ''.join(
        f'<li>{e(label)}</li>' for label in work['candidate_flow'])
    result['rss_sources'] = ''.join(
        f'<li><a href="{e(row["url"])}" target="_blank" rel="noopener noreferrer">{e(row["label"])} ↗</a></li>'
        for row in work['sources'])
    return result

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
    update = DATA['plan_update']
    update_progress = ''.join(f'''<article class="route-progress-card"><span class="eyebrow">0{i+1} / {e(r['label'])}</span>
      <h4>{e(r['title'])}</h4><p>{e(r['description'])}</p></article>''' for i,r in enumerate(update['progress']))
    update_bottleneck_metrics = ''.join(f'''<div><strong>{e(r['value'])}</strong><span>{e(r['label'])}</span><p>{e(r['description'])}</p></div>''' for r in update['bottleneck_metrics'])
    update_route_options = ''.join(f'''<article class="route-option {e(r['kind'])}"><div><span class="eyebrow">{e(r['label'])}</span>{badge(r['kind'],r['status'])}</div>
      <h4>{e(r['title'])}</h4><p>{e(r['description'])}</p><strong>{e(r['judgement'])}</strong></article>''' for r in update['route_options'])
    update_ownership = ''.join(f'''<article><span class="eyebrow">{e(r['label'])}</span><h4>{e(r['title'])}</h4><p>{e(r['description'])}</p></article>''' for r in update['ownership'])
    update_steps = ''.join(f'''<li><span class="route-step-number">{i+1:02d}</span><div><span class="eyebrow">{e(r['label'])}</span><h4>{e(r['title'])}</h4><p>{e(r['description'])}</p><small>{e(r['gate'])}</small></div></li>''' for i,r in enumerate(update['steps']))
    update_candidates = ''.join(f'''<article><div><h4>{e(r['title'])}</h4>{badge(r['kind'],r['status'])}</div><p>{e(r['description'])}</p><a href="{e(r['url'])}" target="_blank" rel="noopener noreferrer">查看原始项目 ↗</a></article>''' for r in update['candidates'])
    update_evidence = ''.join(f'''<div><h4>{e(r['title'])}</h4><p>{e(r['summary'])}</p></div>''' for r in update['evidence'])
    template = (HERE/'content/page.html').read_text()
    replacements = {'metrics': metrics,'stages': stages,'papers': papers,'comparisons': comparisons,'plans': plans,'evidence': evidence_items,'frames': frames,'evidence_count':str(len(DATA['evidence']))}
    replacements.update({k:e(DATA[k]) for k in ['date','updated_date','version','title','goal','summary','literature_date']})
    replacements.update({
        'plan_update_progress': update_progress,
        'plan_update_bottleneck_metrics': update_bottleneck_metrics,
        'plan_update_route_options': update_route_options,
        'plan_update_ownership': update_ownership,
        'plan_update_steps': update_steps,
        'plan_update_candidates': update_candidates,
        'plan_update_evidence': update_evidence,
    })
    replacements.update({'plan_update_'+k:e(update[k]) for k in [
        'date','title','summary','bottleneck_title','bottleneck_summary','bottleneck_verdict',
        'decision','value_answer','boundary','conclusion'
    ]})
    replacements.update(weekly_replacements())
    replacements.update(weekly_replacements('current_update', 'current'))
    replacements.update(related_work_replacements())
    replacements.update(robosim_replacements())
    replacements.update({work_id + '_resources': work_resource_links(work_id)
                         for work_id in DATA['work_resources']})
    replacements['main_navigation'] = ''.join(
        f'<a href="#{e(group["entry"])}" data-report-group="{e(group["id"])}">{e(group["label"])}</a>'
        for group in DATA['navigation'])
    for group in DATA['navigation']:
        replacements[group['id'] + '_pages'] = ''.join(
            f'<a href="#{e(page_id)}" data-page-link>{e(label)}</a>'
            for page_id, label in group['pages'])
        if group.get('topics'):
            replacements[group['id'] + '_topics'] = ''.join(
                f'<a href="#{e(topic["entry"])}" data-work-link="{e(topic["id"])}">{e(topic["label"])}</a>'
                for topic in group['topics'])
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
    current = base/'embodied_stretch_ai_admission_20260926_v1'
    mapping.update({
        'week-20261027-expert.mp4':base/'embodied_codex_expert_20261025_v2/trials/dev010/actual_video/motion.mp4',
        'week-20261027-expert.jpg':base/'embodied_codex_expert_20261025_v2/trials/dev010/actual_video/actual_1444.jpg',
        'week-20261021-native.mp4':base/'embodied_native_walk_20261021_v1/video_A_complete/motion.mp4',
        'week-20261021-native.jpg':base/'embodied_native_walk_20261021_v1/A_video_review/A_decoded_0630.jpg',
        'week-20261021-transport.mp4':base/'embodied_transport_continuous_20261020_v3/qualified_transport_framed/motion.mp4',
        'week-20261021-transport.jpg':base/'embodied_transport_continuous_20261020_v3/qualified_transport_framed/preview.jpg',
        'week-20261021-locomotion.mp4':base/'embodied_locomotion_pipeline_20261020_v1/review_v4/C025/motion.mp4',
        'week-20261021-locomotion.jpg':base/'embodied_locomotion_pipeline_20261020_v1/review_v4/C025/preview.jpg',
        'stretch-room.gif':current/'capability_household/observations_corrected/room.gif',
        'stretch-task.gif':current/'capability_household/observations_corrected/task.gif',
        'stretch-room-poster.png':current/'capability_household/observations_corrected/room_hold.png',
        'stretch-task-poster.png':current/'capability_household/observations_corrected/task_hold.png',
        'layout-sd01.png':current/'capability_scene_diversity/SD01_static_robot.png',
        'layout-sd02.png':current/'capability_scene_diversity/SD02_static_robot.png',
        'geometry-placement.png':current/'capability_geometry_collection/PLACEMENT_BY_GEOMETRY.png',
        'mass-geometry-placement.png':current/'capability_mass_geometry/PLACEMENT_BY_MASS_GEOMETRY.png',
        'mass-dynamics-comparison.png':current/'capability_mass_dynamics_probe/COMPARISON.png',
    })
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
    for rec in [*DATA['evidence'], *DATA['current_update']['evidence'],
                *DATA['related_work']['project_evidence']]:
        for relative in rec['files']:
            src=ROOT/relative
            raw=src.read_bytes()
            manifest.append({'source':relative,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    # Keep historical provenance captured by earlier report updates.
    previous_path = HERE/'source_manifest.json'
    if previous_path.is_file():
        known = {(row['source'], row.get('public_asset')) for row in manifest}
        for row in json.loads(previous_path.read_text())['files']:
            key = (row['source'], row.get('public_asset'))
            if key not in known:
                manifest.append(row)
                known.add(key)
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
