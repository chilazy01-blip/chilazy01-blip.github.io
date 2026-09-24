#!/usr/bin/env python3
"""Check the report's offline links, public content and exact copied assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json

HERE = Path(__file__).resolve().parent.parent
PUBLIC = HERE / 'public'

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if 'id' in fields:
            self.ids.append(fields['id'])
        for name in ('src', 'href'):
            if name in fields:
                self.refs.append(fields[name])

scan = Scan()
scan.feed((PUBLIC / 'index.html').read_text())
errors = []
for ref in scan.refs:
    url = urlsplit(ref)
    if url.scheme or url.netloc:
        continue
    if url.path and not (PUBLIC / unquote(url.path)).is_file():
        errors.append('missing file ' + ref)
    if not url.path and url.fragment and url.fragment not in scan.ids:
        errors.append('missing anchor ' + ref)
if len(set(scan.ids)) != len(scan.ids):
    errors.append('duplicate id')

public_files = [p for p in PUBLIC.rglob('*') if p.is_file()]
for file in public_files:
    if file.suffix in ('.html', '.css', '.js', '.json', '.svg'):
        content = file.read_text()
        for token in ('/data/wsj/', '/tmp/', 'file://'):
            if token in content:
                errors.append(str(file.relative_to(HERE)) + ' contains a machine-specific path: ' + token)

manifest = json.loads((HERE / 'content/assets.json').read_text())
copies = 0
for record in manifest['assets']:
    copies += 1
    target = PUBLIC / record['path']
    if not target.is_file():
        errors.append('missing asset: ' + record['path'])
    elif hashlib.sha256(target.read_bytes()).hexdigest() != record['sha256']:
        errors.append('copied asset mismatch: ' + record['path'])

result = {'links_checked': len(scan.refs), 'ids': len(scan.ids), 'public_files': len(public_files),
          'exact_asset_copies': copies, 'errors': errors, 'passed': not errors}
(HERE / 'checks/static-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
